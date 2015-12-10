#!/usr/bin/env python

from robogif.version import VERSION
from distutils.core import setup

setup(name='robogif',
      version=VERSION,
      description='Simple Android screen recorder',
      long_description='RoboGif allows you to simply record the screen of your 4.4+ Android device and then convert the recording to high-quality GIF or video.\n Requires adb and ffmpeg to be installed on the system.',
      author='Jernej Virag',
      license="Apache",
      author_email='jernej@virag.si',
      packages=['robogif'],
      install_requires=['blessings==1.6', 'Click==4.1.0'],
      entry_points='''
        [console_scripts]
        robogif=robogif.recorder:run
      ''',
      url="https://github.com/izacus/RoboGif",
      classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Utilities"
      ]
     )