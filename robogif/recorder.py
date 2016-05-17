#!/usr/bin/env python
from __future__ import print_function

import subprocess
import signal
import time
import sys
import os
import click
import blessings

try:
    # Python 3
    from .utilities import which
    from .utilities import get_new_temp_file_path
    from .adb import get_devices
    from .version import VERSION
except ValueError:
    # Python 2
    from utilities import which
    from utilities import get_new_temp_file_path
    from adb import get_devices
    from version import VERSION

t = blessings.Terminal()


def check_requirements():
    if which("adb") is None:
        print(t.red("This program requires adb executable to be in path."))
        sys.exit(-3)

    ffmpeg_path = which("ffmpeg")
    if ffmpeg_path is None:
        print(t.red("This program requires ffmpeg in path."))
        sys.exit(-4)

    # Check if ffmpeg supports all capabilities we need
    try:
        ffmpeg_p = subprocess.Popen([ffmpeg_path, "-codecs"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = ffmpeg_p.stdout.read().decode("utf-8")
        ffmpeg_p.communicate()

        if ffmpeg_p.returncode != 0:
            print(t.red("Incompatible ffmpeg version detected, please update to newest ffmpeg."))
            sys.exit(-4)

        if "gif" not in output:
            print(t.red("Missing GIF encoder in your installed ffmpeg, cannot create gifs."))
            sys.exit(-4)

        if "libx264" not in output:
            print(t.yellow("Missing libx264 encoder in your installed ffmpeg, will not be able to create videos."))

        ffmpeg_p = subprocess.Popen([ffmpeg_path, "-filters"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = ffmpeg_p.stdout.read().decode("utf-8")
        ffmpeg_p.communicate()
        if ffmpeg_p.returncode != 0:
            print(t.red("Incompatible ffmpeg version detected, please update to newest ffmpeg."))
            sys.exit(-4)

        if not("format" in output and "scale" in output and "palettegen" in output and "paletteuse" in output and "fps" in output):
            print(t.red("Missing required filters in installed ffmpeg, installed ffmpeg requires"), \
                  t.green("format, fps, scale, palettegen and paletteuse"), t.red("filters."))
            sys.exit(-4)
    except OSError:
        print(t.red("This program requires a newish ffmpeg in path."))
        sys.exit(-4)


def get_chosen_device(devices):
    # This is a shim to support raw_input on Python 2.x and 3.x
    global input
    try: input = raw_input
    except NameError: pass

    print(t.green("Multiple devices found, choose one: "))
    num = 0
    entry_dict = {}
    print(t.normal + "===============")
    for device_id in devices:
        print("{t.green}[{num}] {t.white}{model} - {t.yellow}{device_id}".format(t=t, num=num, model=devices[device_id]["model"] if "model" in devices[device_id] else "(unknown)", device_id=device_id))
        entry_dict[num] = device_id
        num += 1
    print(t.normal + "===============")
    entry = -1
    while entry not in entry_dict:
        inp = input(t.green(" Choose[0-%d]: " % (num - 1, )))
        try:
            entry = int(inp.strip())
        except ValueError:
            entry = -1

    print(t.normal)
    return entry_dict[entry]


def create_optimized_video(in_file, out_file, size, fps, video_quality):
    print(t.green("Optimizing video..."))

    FFMPEG_FILTERS = "format=pix_fmts=yuv420p,fps={fps},scale=w='if(gt(iw,ih),-2,{size})':h='if(gt(iw,ih),{size},-2)':flags=lanczos".format(fps=fps, size=size)
    FFMPEG_CONVERT = ["ffmpeg", "-v", "warning", "-i", in_file, "-codec:v", "libx264", "-preset", "slow", "-crf", str(video_quality), "-vf", FFMPEG_FILTERS, "-y", "-f", "mp4", out_file]

    try:
        subprocess.check_call(FFMPEG_CONVERT)
        print(t.green("Done!"))
    except:
        print(t.red("Could not optimize downloaded recording!"))
        raise

    print(t.yellow("Created " + out_file))


def create_optimized_gif(in_file, out_file, size, fps):
    print(t.green("Converting video to GIF..."))
    tmp_pal_file = get_new_temp_file_path("png")
    gifsicle_path = which("gifsicle")

    if gifsicle_path is not None:
        convert_output_path = get_new_temp_file_path("gif")
    else:
        convert_output_path = out_file

    FFMPEG_FILTERS = "fps={fps},scale=w='if(gt(iw,ih),-1,{size})':h='if(gt(iw,ih),{size},-1)':flags=lanczos".format(fps=fps, size=size)
    FFMPEG_PALLETE = ["ffmpeg", "-v", "warning", "-i", in_file, "-vf", FFMPEG_FILTERS + ",palettegen", "-y", tmp_pal_file]
    FFMPEG_CONVERT = ["ffmpeg", "-v", "warning", "-i", in_file, "-i", tmp_pal_file, "-lavfi", FFMPEG_FILTERS + "[x];[x][1:v]paletteuse=dither=floyd_steinberg", "-y", "-f", "gif", convert_output_path]
    GIFSICLE_OPTIMIZE = ["gifsicle", "-O3", convert_output_path, "-o", out_file]

    try:
        subprocess.check_call(FFMPEG_PALLETE)
        subprocess.check_call(FFMPEG_CONVERT)

        if gifsicle_path is not None:
            subprocess.check_call(GIFSICLE_OPTIMIZE)

        print(t.green("Done!"))
    except:
        print(t.red("Could not convert downloaded recording to GIF!"))
        raise
    finally:
        try:
            os.remove(tmp_pal_file)
            if gifsicle_path is not None:
                os.remove(convert_output_path)
        except:
            pass

    print(t.yellow("Created " + out_file))


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
        print(t.red("Filename must either end with"), t.green("mp4"), t.red("for video or"), t.green("gif"), t.red("for a GIF."))
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
            print(t.red("There's no point in converting video to video!"))
            sys.exit(-4)

        create_optimized_gif(input_file, filename, size, fps)
        sys.exit(0)

    # Show device chooser if more than one device is selected
    device_id = None
    devices = get_devices()
    if len(devices) == 0:
        print(t.red("No adb devices found, connect one."))
        sys.exit(-3)
    elif len(devices) == 1:
        device_id = list(devices.keys())[0]
    else:
        device_id = get_chosen_device(devices)

    print(t.green("Starting recording on %s..." % (device_id, )))
    print(t.yellow("Press Ctrl+C to stop recording."))

    recorder = subprocess.Popen(["adb", "-s", device_id, "shell", "screenrecord", "--bit-rate", "8000000", "/sdcard/tmp_record.mp4"])
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
        print(t.red("Recording has failed, it's possible that your device does not support recording."))
        print(t.normal + "Recording is supported on devices running KitKat (4.4) or newer.")
        print(t.normal + "Genymotion and stock emulator do not support it.")
        print
        sys.exit(-3)
    # We need to wait for MOOV item to be written
    time.sleep(2)

    print(t.green("Recording done, downloading file...."))
    tmp_video_file = get_new_temp_file_path("mp4")

    # Download file and cleanup
    try:
        subprocess.check_call(["adb", "-s", device_id, "pull", "/sdcard/tmp_record.mp4", tmp_video_file])
        subprocess.check_call(["adb", "-s", device_id, "shell", "rm", "/sdcard/tmp_record.mp4"])

        if output_video_mode:
            create_optimized_video(tmp_video_file, filename, size, fps, video_quality)
        else:
            create_optimized_gif(tmp_video_file, filename, size, fps)

    except subprocess.CalledProcessError:
        print(t.red("Could not download recording from the device."))
        sys.exit(-1)
    finally:
        os.remove(tmp_video_file)

if __name__ == "__main__":
    run()
