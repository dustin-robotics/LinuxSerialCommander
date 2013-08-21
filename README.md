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

Development Environment
=======================

This set of programs was developed in Crunchbang Linux (Debian 7 stable,
openbox, tint2). To program the Arduino, I used Arduino-mk in combination with
my Lscreamer python script. LScreamer lets you flash over unreliable networks
(wireless, wifi, ethernet).

Arduino-mk: https://github.com/sudar/Arduino-Makefile/

LScreamer: http://sourceforge.net/projects/lscreamer/files/bin/

The hotkeys are matched with an ~/.config/openbox/rc.xml, which can be found in
this repo.

How to get started
==================

 1. Get arduino + LCD character backpack as shown on my blog,
    http://mecharobotics.wordpress.com.
 2. Using the Arduino software on your PC, load CPUduino.ino.  Program it to
    the Arduino + LCD board (you could use arduino-mk + LScreamer for this as
well)
 3. Install python 2.7+, python-serial, xautomation on the host.
 4. Run "python MicroSync.py -i /dev/ttyXXXX -s ~/start/filebrowser/here
      Note: XXXX for me was USB0, for you it may be different.
 5. Compare hotkeys.py with the hotkeys defined in your ~/.config/???.xml file
      Note: ??? for me was rc, my rc.xml is included as a reference.
 6. Now your running!

Links
=====

My Blog: http://mecharobotics.wordpress.com

Video of it in action: https://vimeo.com/72785300

Arduino-mk: https://github.com/sudar/Arduino-Makefile/

LScreamer: http://sourceforge.net/projects/lscreamer/files/bin/


