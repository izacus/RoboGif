# RoboGif

A small utility to record Android device screen to an optimized GIF so you can paste it to GitHub or a similar service.

## Requirements

* Python 3.x
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

On Ubuntu 24.04, Debian or equivalent, you can just use `apt`:

```
apt-get install ffmpeg
```
 
##### Windows

```
scoop install ffmpeg
```

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

Example of a recorded GIF:

![GIF example](https://izacus.github.io/RoboGif/images/demo.gif)

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

### Connecting devices

`robogif` requires `adb` for accessing Android devices. Before recording a GIF or video, you need to connect the target device to your computer using a USB cable. The device must have "USB debugging" enabled. You can check if the device is properly connected by running `adb device` from your terminal. If your device shows up, you are ready to go.

```bash 
> adb devices -l
List of devices attached
CVH7N25B12003553       device usb:346594891X product:angler model:Nexus_6P device:angler
```
