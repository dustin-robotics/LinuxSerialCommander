LinuxSerialCommander
====================

Linux Serial Commander

This project lets you use off-the-shelf parts (Arduino, 16x2 character
LCD/button backpack), to have full control of your Linux system.

It allows you to:

  1. Send keyboard shortcuts
  2. Navigate filesystem, running scripts, opening and playing music and movies with the ability to control them on LSC
  3. Browse wifi networks, I almost have WPA connection done, but it may be a while
  4. Python script controls the Arduino, telling it what to draw, telling it to wait for buttons, and providing a workable form entry for passwords

The principal idea behind the project is to allow you to control a Raspberry
Pi, without needing a LCD connected to it (just this character LCD).

Hotkeys
=======

Currently the following applications are supported:

 1. tmux
 2. mplayer
 3. normal (volume, mute, etc...)

I will be adding support for:

 1. VLC
 2. cmus
 3. deadbeef

Folder Navigation
=================

That's right, its called 'Run Programs', and it allows you to navigate the
entire filesystem, letting you open up:

 1. bash scripts
 2. video/music files (note, jumps to mplayer hotkey menu when you do this)
 3. Any generic script that will run (it will just give it a try anyways)

Wifi Connection
===============

Most of the code is there, except for the last bit of doing the actual
connection.  See the problem is that Rasbian is based on Debian 7, and Debian 7
doesn't have the latest nmcli (I need 0.9.6). Since nmcli version 0.9.6 does
WPA connection so well, I decided to wait to finish this feature.

 1. Browse available wifi networks
 2. Upon selection, allows you to enter password on Arduino
 3. Sends password to Python script running on server, which then exits that
    routine :)


