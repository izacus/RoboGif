# RoboGif

A small utility to record Android device screen to an optimized GIF so you can paste it to GitHub or a simillar service.

![Demo recorded GIF](/images/demo.gif)

## Requirements

* Python 3
* `adb` in path
* `ffmpeg` in path (has to be decently new to support `palettegen` and `paletteuse` filters and have `libx264` if you want video output)

#### Getting ffmpeg

##### OS X

```
brew install ffmpeg
```

##### Linux

On Ubuntu 24.04 or equivalent, you can just use `apt`:

```
apt-get install ffmpeg
```
 
##### Windows
 
```
scoop install ffmpeg
```

Any other approach will work as long as you end up with ffmpeg.exe.

## Installation

```
pip install robogif
```

## Usage

To record a gif:

```
robogif demo.gif

RoboGif Recorder v1.4.0
Starting recording on <serial>...
Press Ctrl+C to stop recording.
Recording done, downloading file....
5679 KB/s (7036946 bytes in 1.209s)
Converting video to GIF...
Done!
Created demo.gif
```

or to record a video:

```
robogif demo.mp4

RoboGif Recorder v1.4.0
Starting recording on 061ffcff0b107aef...
Press Ctrl+C to stop recording.
Recording done, downloading file....
7121 KB/s (1048401 bytes in 0.143s)
Optimizing video...
Done!
Created demo.mp4
```
