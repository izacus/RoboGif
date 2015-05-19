#!/usr/bin/env python

import blessings
import subprocess
import signal
import time
import sys
import os
import pyperclip

from adb import get_devices

t = blessings.Terminal()

def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

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
    print "==============="
    for device_id in devices:
        print "{t.green}[{num}] {t.white}{model} - {t.yellow}{device_id}".format(t=t, num=num, model=devices[device_id]["model"], device_id=device_id)
        entry_dict[num] = device_id
        num += 1
    print "==============="
    entry = -1
    while not entry in entry_dict:
        inp = raw_input(t.green(" Choose[0-%d]: " % (num - 1, )))
        try:
            entry = int(inp.strip())
        except ValueError:
            entry = -1    

    return entry_dict[entry]


print "ADB Recorder v0.1"
check_requirements()

# Show device chooser if more than one device is selected
device_id = None
devices = get_devices()
if len(devices) == 1:
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

recorder.send_signal(signal.SIGTERM)
recorder.wait()

print t.green("Recording done, downloading file....")

# We need to wait for MOOV item to be written
time.sleep(2)

# Download file and cleanup
try:
    subprocess.check_call(["adb", "-s", device_id, "pull", "/sdcard/tmp_record.mp4", "./tmp_record.mp4"])
    subprocess.check_call(["adb", "-s", device_id, "shell", "rm", "/sdcard/tmp_record.mp4"])
except subprocess.CalledProcessError:
    print t.red("Could not download recording from the device.");
    sys.exit(-1)

print t.green("Converting video to GIF...")
FFMPEG_FILTERS = "fps=15,scale=480:-1:flags=lanczos"
FFMPEG_PALLETE = ["ffmpeg", "-v", "warning", "-i", "tmp_record.mp4", "-vf", FFMPEG_FILTERS + ",palettegen", "-y", "tmp_palette.png"]
FFMPEG_CONVERT = ["ffmpeg", "-v", "warning", "-i", "tmp_record.mp4", "-i", "tmp_palette.png", "-lavfi", FFMPEG_FILTERS + "[x];[x][1:v]paletteuse=dither=floyd_steinberg", "-y", "video.gif"]

try:
    subprocess.check_call(FFMPEG_PALLETE)
    subprocess.check_call(FFMPEG_CONVERT)
    print t.green("Done!")
except:
    print t.red("Could not convert downloaded recording to GIF!")
    sys.exit(-2)
finally:
    os.remove("tmp_palette.png")
    os.remove("tmp_record.mp4")

pyperclip.copy("file://" + unicode(os.path.abspath("./video.gif")))
print t.yellow("Path to GIF was copied to clipboard.")

