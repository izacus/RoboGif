# RoboGif

A small utility to record Android device screen to an optimized GIF so you can paste it to GitHub or a simillar service.

## Requirements

* Python 2
* `adb` in path
* `ffmpeg` in path (has to be decently new to support `palettegen` and `paletteuse` filters and have `libx264` if you want video output)

#### Getting ffmpeg

##### OS X

```
brew install ffmpeg
```

##### Linux

On Ubuntu 15.04 or equivalent, you can just use `apt`:

```
apt-get install ffmpeg
```

On Ubuntu 14.04 you can use [Ubuntu Multimedia for Trusty PPA](https://launchpad.net/~mc3man/+archive/ubuntu/trusty-media) to get new ffmpeg.
 
##### Windows
 
Windows support was not tested as of yet. [Zeranoe's static builds](http://ffmpeg.zeranoe.com/builds/) should work fine as long as they're named `ffmpeg.exe` in path. 


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
