# RoboGif

A small utility to record Android device screen to an optimized GIF so you can paste it to GitHub or a simillar service.

## Requirements

* Python 2.7 or 3.x
* `adb` in path
* `ffmpeg` in path (has to be decently new to support `palettegen` and `paletteuse` filters and have `libx264` if you want video output)

### Optional

* `gifsicle` for further gif optimization

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
robogif demo.gif

RoboGif Recorder v1.1.2
Starting recording on <serial>...
Press Ctrl+C to stop recording.
Recording done, downloading file....
5679 KB/s (7036946 bytes in 1.209s)
Converting video to GIF...
Done!
Created demo.gif
```

Example of a recorded GIF:

![GIF example](https://izacus.github.io/RoboGif/images/demo.gif)

or to record a video:

```
robogif demo.mp4

RoboGif Recorder v1.1.2
Starting recording on 061ffcff0b107aef...
Press Ctrl+C to stop recording.
Recording done, downloading file....
7121 KB/s (1048401 bytes in 0.143s)
Optimizing video...
Done!
Created demo.mp4
```
