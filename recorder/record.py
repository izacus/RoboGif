#!/usr/bin/env python

import blessings
import subprocess
import signal
import time
import sys
import os
import pyperclip

t = blessings.Terminal()
print "ADB Recorder v0.1"
print t.green("Starting recording on device...")

recorder = subprocess.Popen(["adb", "shell", "screenrecord", "--bit-rate", "8000000", "/sdcard/tmp_record.mp4"])
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
    subprocess.check_call(["adb", "pull", "/sdcard/tmp_record.mp4", "./tmp_record.mp4"])
    subprocess.check_call(["adb", "shell", "rm", "/sdcard/tmp_record.mp4"])
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

