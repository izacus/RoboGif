#!/usr/bin/env python
import subprocess
import signal
import time
import sys
import os
import click

from .utilities import which, is_win
from .utilities import get_new_temp_file_path
from .adb import adb_bin, get_devices
from .version import VERSION

if is_win:
    FFMPEG_BIN = "ffmpeg.exe"
else:
    FFMPEG_BIN = "ffmpeg"

def check_requirements():
    if which(adb_bin()) is None:
        click.secho("This program requires adb executable to be in path.", fg='red')
        sys.exit(-3)

    ffmpeg_path = which(FFMPEG_BIN)
    if ffmpeg_path is None:
        click.secho("This program requires ffmpeg in path.", fg='red')
        sys.exit(-4)

    # Check if ffmpeg supports all capabilities we need
    try:
        ffmpeg_p = subprocess.Popen([ffmpeg_path, "-codecs"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = ffmpeg_p.stdout.read().decode("utf-8")
        ffmpeg_p.communicate()

        if ffmpeg_p.returncode != 0:
            click.secho("Incompatible ffmpeg version detected, please update to newest ffmpeg.", fg='red')
            sys.exit(-4)

        if "gif" not in output:
            click.secho("Missing GIF encoder in your installed ffmpeg, cannot create gifs.", fg='red')
            sys.exit(-4)

        if "libx264" not in output:
            click.secho("Missing libx264 encoder in your installed ffmpeg, will not be able to create videos.", fg='yellow')

        ffmpeg_p = subprocess.Popen([ffmpeg_path, "-filters"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = ffmpeg_p.stdout.read().decode("utf-8")
        ffmpeg_p.communicate()
        if ffmpeg_p.returncode != 0:
            click.secho("Incompatible ffmpeg version detected, please update to newest ffmpeg.", fg='red')
            sys.exit(-4)

        if not("format" in output and "scale" in output and "palettegen" in output and "paletteuse" in output and "fps" in output):
            click.secho("Missing required filters in installed ffmpeg, installed ffmpeg requires", fg='red'), \
                  click.echo("format, fps, scale, palettegen and paletteuse", fg='green'), click.echo("filters.", fg='red')
            sys.exit(-4)
    except OSError:
        click.secho("This program requires a newish ffmpeg in path.", fg='red')
        sys.exit(-4)


def get_chosen_device(devices):
    click.secho("Multiple devices found, choose one: ", fg='green')
    num = 0
    entry_dict = {}
    print("===============")
    for device_id in devices:
        model = devices[device_id]["model"] if "model" in devices[device_id] else "(unknown)"
        click.echo(click.style("[%d] " % (num, ), fg='green') + model + " - " + click.style(device_id))        
        entry_dict[num] = device_id
        num += 1
    print("===============")
    entry = -1
    while entry not in entry_dict:
        inp = input(" Choose[0-%d]: " % (num - 1, ))
        try:
            entry = int(inp.strip())
        except ValueError:
            entry = -1

    print()
    return entry_dict[entry]


def create_optimized_video(in_file, out_file, size, fps, video_quality):
    click.secho("Optimizing video...", fg='green')

    FFMPEG_FILTERS = "format=pix_fmts=yuv420p,fps={fps},scale=w='if(gt(iw,ih),-2,{size})':h='if(gt(iw,ih),{size},-2)':flags=lanczos".format(fps=fps, size=size)
    FFMPEG_CONVERT = [FFMPEG_BIN, "-v", "error", "-i", in_file, "-codec:v", "libx264", "-preset", "slow", "-crf", str(video_quality), "-vf", FFMPEG_FILTERS, "-dn", "-y", "-f", "mp4", out_file]

    try:
        subprocess.check_call(FFMPEG_CONVERT)
        click.secho("Done!", fg='green')
    except:
        click.secho("Could not optimize downloaded recording!", fg='red')
        raise

    click.secho("Created %s" % (out_file,), fg='yellow')


def create_optimized_gif(in_file, out_file, size, fps):
    click.secho("Converting video to GIF...", fg='green')
    tmp_pal_file = get_new_temp_file_path("png")
    gifsicle_path = which("gifsicle")

    if gifsicle_path is not None:
        convert_output_path = get_new_temp_file_path("gif")
    else:
        convert_output_path = out_file

    FFMPEG_FILTERS = "fps={fps},scale=w='if(gt(iw,ih),-1,{size})':h='if(gt(iw,ih),{size},-1)':flags=lanczos".format(fps=fps, size=size)
    FFMPEG_PALLETE = [FFMPEG_BIN, "-v", "error", "-i", in_file, "-vf", FFMPEG_FILTERS + ",palettegen", "-dn", "-y", tmp_pal_file]
    FFMPEG_CONVERT = [FFMPEG_BIN, "-v", "error", "-i", in_file, "-i", tmp_pal_file, "-lavfi", FFMPEG_FILTERS + "[x];[x][1:v]paletteuse=dither=floyd_steinberg", "-dn", "-y", "-f", "gif", convert_output_path]
    GIFSICLE_OPTIMIZE = ["gifsicle", "-O3", convert_output_path, "-o", out_file]

    try:
        subprocess.check_call(FFMPEG_PALLETE)
        subprocess.check_call(FFMPEG_CONVERT)

        if gifsicle_path is not None:
            subprocess.check_call(GIFSICLE_OPTIMIZE)

        click.secho("Done!", fg='green')
    except:
        click.secho("Could not convert downloaded recording to GIF!", fg='red')
        raise
    finally:
        try:
            os.remove(tmp_pal_file)
            if gifsicle_path is not None:
                os.remove(convert_output_path)
        except:
            pass

    click.secho("Created %s" % (out_file, ), fg="yellow")


@click.command(options_metavar="[options]")
@click.argument("filename", type=click.Path(exists=False, writable=True, resolve_path=True), metavar="<filename>.<gif|mp4>")
@click.option('-i', '--input-file', type=str, help="Convert input mp4 file to optimized gif")
@click.option('-s', '--size', type=int, default=480, help="Size of the shortest side of the output gif/video. Defaults to 480.")
@click.option('-f', '--fps', type=int, help="Framerate of the output gif/video. Defaults to 15 for GIF and 60 for MP4.")
@click.option('-vq', '--video-quality', type=int, default=24, help="Video quality of the output video - the value is x264 CRF. Default is 24, lower number means better quality.")
@click.help_option()
@click.version_option(version=VERSION, prog_name="RoboGif")
def run(filename=None, input_file=None, size=None, fps=None, video_quality=None):
    """
    Records Android device screen to an optimized GIF or MP4 file. The type of the output is chosen depending on the file extension.
    """

    print("RoboGif Recorder v%s" % (VERSION,))
    check_requirements()
    output_video_mode = False

    if not (filename.lower().endswith(".mp4") or filename.lower().endswith(".gif")):
        print("Usage: %s [output filename].[mp4|gif]" % (sys.argv[0], ))
        click.echo(click.style("Filename must either end with", fg='red'), click.style("mp4", fg='green'), click.style("for video or", fg='red'), click.style("gif", fg='green'), click.style("for a GIF.", fg='red'))
        print
        sys.exit(-4)

    if filename.lower().endswith(".mp4"):
        output_video_mode = True

    if fps is None:
        if output_video_mode:
            fps = 60
        else:
            fps = 15

    # Convert file if input is passed
    if input_file is not None:
        if output_video_mode:
            click.secho("There's no point in converting video to video!", fg='red')
            sys.exit(-4)

        create_optimized_gif(input_file, filename, size, fps)
        sys.exit(0)

    # Show device chooser if more than one device is selected
    device_id = None
    devices = get_devices()
    if len(devices) == 0:
        click.secho("No adb devices found, connect one.", fg='red')
        sys.exit(-3)
    elif len(devices) == 1:
        device_id = list(devices.keys())[0]
    else:
        device_id = get_chosen_device(devices)

    click.secho("Starting recording on %s..." % (device_id, ), fg='green')
    click.secho("Press Ctrl+C to stop recording.", fg='yellow')

    recorder = subprocess.Popen([adb_bin(), "-s", device_id, "shell", "screenrecord", "--bit-rate", "8000000", "/data/local/tmp/tmp_record.mp4"])
    try:
        while recorder.poll() is None:
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass

    try:
        recorder.send_signal(signal.SIGTERM)
        recorder.wait()
    except OSError:
        print
        click.secho("Recording has failed, it's possible that your device does not support recording.", fg='red')
        click.echo("Recording is supported on devices running KitKat (4.4) or newer.")
        click.echo("Genymotion and stock emulator do not support it.")
        print
        sys.exit(-3)
    # We need to wait for MOOV item to be written
    time.sleep(2)

    click.secho("Recording done, downloading file....", fg='green')
    tmp_video_file = get_new_temp_file_path("mp4")

    # Download file and cleanup
    try:
        subprocess.check_call([adb_bin(), "-s", device_id, "pull", "/data/local/tmp/tmp_record.mp4", tmp_video_file])
        subprocess.check_call([adb_bin(), "-s", device_id, "shell", "rm", "/data/local/tmp/tmp_record.mp4"])

        if output_video_mode:
            create_optimized_video(tmp_video_file, filename, size, fps, video_quality)
        else:
            create_optimized_gif(tmp_video_file, filename, size, fps)

    except subprocess.CalledProcessError:
        click.secho("Could not download recording from the device.", fg='red')
        sys.exit(-1)
    finally:
        os.remove(tmp_video_file)

if __name__ == "__main__":
    run()
