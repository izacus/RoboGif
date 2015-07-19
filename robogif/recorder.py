#!/usr/bin/env python2

import click
import blessings
import subprocess
import signal
import time
import sys
import os
from utilities import which
from utilities import get_new_temp_file_path
from adb import get_devices

t = blessings.Terminal()


def check_requirements():
    if which("adb") is None:
        print t.red("This program requires adb executable to be in path.")
        sys.exit(-3)
    if which("ffmpeg") is None:
        print t.red("This program requires ffmpeg in path.")
        sys.exit(-4)


def get_chosen_device(devices):
    print t.green("Multiple devices found, choose one: ")
    num = 0;
    entry_dict = {}
    print t.normal + "==============="
    for device_id in devices:
        print "{t.green}[{num}] {t.white}{model} - {t.yellow}{device_id}".format(t=t, num=num, model=devices[device_id]["model"], device_id=device_id)
        entry_dict[num] = device_id
        num += 1
    print t.normal + "==============="
    entry = -1
    while not entry in entry_dict:
        inp = raw_input(t.green(" Choose[0-%d]: " % (num - 1, )))
        try:
            entry = int(inp.strip())
        except ValueError:
            entry = -1    

    print t.normal
    return entry_dict[entry]


def create_optimized_video(in_file, out_file, size, fps):
    print t.green("Optimizing video...")

    FFMPEG_FILTERS = "format=pix_fmts=yuv420p,fps={fps},scale=w='if(gt(iw,ih),-2,{size})':h='if(gt(iw,ih),{size},-2)':flags=lanczos".format(fps=fps, size=size)
    FFMPEG_CONVERT = ["ffmpeg", "-v", "warning", "-i", in_file, "-codec:v", "libx264", "-preset", "slow", "-crf", "24", "-vf", FFMPEG_FILTERS, "-y", "-f", "mp4", out_file]

    try:
        subprocess.check_call(FFMPEG_CONVERT)
        print t.green("Done!")
    except:
        print t.red("Could not optimize downloaded recording!")
        raise

    print t.yellow("Created " + out_file)


def create_optimized_gif(in_file, out_file, size, fps):
    print t.green("Converting video to GIF...")
    tmp_pal_file = get_new_temp_file_path("png")

    FFMPEG_FILTERS = "fps={fps},scale=w='if(gt(iw,ih),-1,{size})':h='if(gt(iw,ih),{size},-1)':flags=lanczos".format(fps=fps, size=size)
    FFMPEG_PALLETE = ["ffmpeg", "-v", "warning", "-i", in_file, "-vf", FFMPEG_FILTERS + ",palettegen", "-y", tmp_pal_file]
    FFMPEG_CONVERT = ["ffmpeg", "-v", "warning", "-i", in_file, "-i", tmp_pal_file, "-lavfi", FFMPEG_FILTERS + "[x];[x][1:v]paletteuse=dither=floyd_steinberg", "-y", "-f", "gif", out_file]

    try:
        subprocess.check_call(FFMPEG_PALLETE)
        subprocess.check_call(FFMPEG_CONVERT)
        print t.green("Done!")
    except:
        print t.red("Could not convert downloaded recording to GIF!")
        raise
    finally:
        try:
            os.remove(tmp_pal_file)
        except: pass

    print t.yellow("Created " + out_file)


@click.command(options_metavar="[options]")
@click.argument("filename", type=click.Path(exists=False, writable=True, resolve_path=True), metavar="<filename>.<gif|mp4>")
@click.option('-s', '--size', type=int, default=480, help="Size of the shortest side of the output gif/video. Defaults to 480.")
@click.option('-f', '--fps', type=int, help="Framerate of the output gif/video. Defaults to 15 for GIF and 60 for MP4.")
@click.help_option()
@click.version_option(version="1.1", prog_name="RoboGif")
def run(filename=None, size=None, fps=None):
    """
    Records Android device screen to an optimized GIF or MP4 file. The type of the output is chosen depending on the file extension.
    """

    print "RoboGif Recorder v1.0"
    check_requirements()
    output_video_mode = False

    if not (filename.lower().endswith(".mp4") or filename.lower().endswith(".gif")):
        print "Usage: %s [output filename].[mp4|gif]" % (sys.argv[0], )
        print "Filename must either end with mp4 for video or gif for a GIF"
        print
        sys.exit(-4)

    if filename.lower().endswith(".mp4"):
        output_video_mode = True

    if fps is None:
        if output_video_mode:
            fps = 60
        else:
            fps = 15

    # Show device chooser if more than one device is selected
    device_id = None
    devices = get_devices()
    if len(devices) == 0:
        print t.red("No adb devices found, connect one.")
        sys.exit(-3)
    elif len(devices) == 1:
        device_id = devices.keys()[0]
    else:
        device_id = get_chosen_device(devices)

    print t.green("Starting recording on %s..." % (device_id, ))
    print t.yellow("Press Ctrl+C to stop recording.")

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
        print t.red("Recording has failed, it's possible that your device does not support recording.")
        print t.normal + "Recording is supported on devices running KitKat (4.4) or newer."
        print t.normal + "Genymotion and stock emulator do not support it."
        print 
        sys.exit(-3)

    print t.green("Recording done, downloading file....")

    # We need to wait for MOOV item to be written
    time.sleep(2)

    tmp_video_file = get_new_temp_file_path("mp4")

    # Download file and cleanup
    try:
        subprocess.check_call(["adb", "-s", device_id, "pull", "/sdcard/tmp_record.mp4", tmp_video_file])
        subprocess.check_call(["adb", "-s", device_id, "shell", "rm", "/sdcard/tmp_record.mp4"])

        if output_video_mode:
            create_optimized_video(tmp_video_file, filename, size, fps)
        else:    
            create_optimized_gif(tmp_video_file, filename, size, fps)

    except subprocess.CalledProcessError:
        print t.red("Could not download recording from the device.");
        sys.exit(-1)
    finally:
        os.remove(tmp_video_file)

if __name__ == "__main__":
    run()
