# RoboGif

A small utility to record Android device screen to an optimized GIF so you can paste it to GitHub or a simillar service.

## Requirements

* Python
* `adb` in path
* `ffmpeg` in path (has to be decently new, use `brew install ffmpeg` on OS X)

## Installation

```
pip install robogif
```

## Usage

To record a gif:

```
robogif mygif.gif

RoboGif Recorder v1.0
Starting recording on device...
Press Ctrl+C to stop recording.
Recording done, downloading file....
Converting video to GIF...
Done!
Created mygif.gif

```

or to record a video:

```
robogif myvideo.mp4
```
