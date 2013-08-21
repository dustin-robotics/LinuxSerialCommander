#! /usr/bin/env python
""" Copyright (C) 2013  Dustin Reynolds - See license restrictions in source directory

    """

import subprocess
import serial
import socket
import glob
import sys
import getopt
import platform
from time import sleep

#Generic XTE escapes
CTRL = 'keydown Control_L\n'
nCTRL = 'keyup Control_L\n'
SHIFT = 'keydown Shift_L\n'
nSHIFT = 'keyup Shift_L\n'
ALT = 'keydown Alt_L\n'
nALT = 'keyup Alt_L\n'
WIN = 'keydown Super_L\n'
nWIN = 'keyup Super_L\n'

'''
Tmux shortcuts
  Menu Based, with shortcut action keys
  u - select pane up
  d - select pane down
  l - select pane to left
  r - select pane to right
s+u - split vert
s+d - split horz
s+l - previous window
s+r - next window
  Split screen vertically
  Split screen horizontally
  view sessions
'''
#TMUX VERBS
TMUX_ESC = CTRL + 'key A\n' + nCTRL
TMUX_DELAY = 'usleep 200\n'
TMUX_NEXT = TMUX_ESC + 'key Tab\n'
TMUX_PREV = TMUX_ESC + 'key 0x3b\n' #0x3b is ;
#TMUX_SPLIT_FOUR = TMUX_SPLIT_VERT + TMUX_SPLIT_HORZ + TMUX_NEXT + TMUX_SPLIT_HORZ + TMUX_PREV

#TMUX Menus
tmux =  "Pane Move udlr\n,Vert sel+UP\n"
tmuxs = "L prev Win\n,U Split vert\n"
tmux_menu = "Return\n,Pane Up\n,Pane Down\n,Pane Right\n,Pane Left\n,Split Vert\n,Split Horz\n,Exit Selected\n,Prev Win\n,Next Win\n,View Sessions\n"
TMUX_NUM = 6
TMUX_SEL_PANE_UP = TMUX_ESC + 'key k\n'
TMUX_SEL_PANE_DOWN = TMUX_ESC + 'key j\n'
TMUX_SEL_PANE_LEFT = TMUX_ESC + 'key h\n'
TMUX_SEL_PANE_RIGHT = TMUX_ESC + 'key l\n'
TMUX_SPLIT_VERT = TMUX_ESC + SHIFT + 'key 5\n' + nSHIFT
TMUX_SPLIT_HORZ = TMUX_ESC + SHIFT + 'key 0x27\n' + nSHIFT  #0x27 = '
TMUX_PREV_WIN = TMUX_ESC + 'key N\n'
TMUX_NEXT_WIN = TMUX_ESC + 'key P\n'
TMUX_VIEW_SESSIONS = TMUX_ESC + 'key S\n' + 'sleep 3\n' + 'key Return\n'
TMUX_EXIT = 'str exit\n' + 'key Return\n'
'''
Mplayer shortcuts
  Menu Based, with shortcut action keys to control selected mplayer session
  u - vol up
  d - vol down
  l - back 10 sec
  r - forward 10 sec
s+u - play/pause
s+d - mute/unmute
s+l - mplayer quit
s+r - mplayer fullscreen
s+s - return
  Prev song
  Next song

'''
#MPLAY VERBS - these match up with openbox's ~/.config/openbox/rc.xml
# See http://stray-notes.blogspot.com/2010/05/mplayer-on-debian.html
#  And http://www.keyxl.com/aaa2fa5/302/MPlayer-keyboard-shortcuts.htm
MPLAY_DELAY = 'usleep 200\n'
MPLAY_TOGGLE_MUTE = WIN + 'key 0\n' + nWIN
MPLAY_VOL_UP = 'key 0\n'
MPLAY_VOL_DOWN = 'key 9\n'
MPLAY_FWD_10SEC = 'key 0xff53\n'
MPLAY_RWD_10SEC = 'key 0xff51\n'
MPLAY_FWD_1MIN = 'key 0xff52\n'
MPLAY_RWD_1MIN = 'key 0xff54\n'
MPLAY_FULL_SCREEN = 'key F\n'
MPLAY_TOGGLE_PLAY = MPLAY_DELAY + 'key P\n' #space
MPLAY_QUIT = 'key q\n'
MPLAY_NEXT_SONG = SHIFT + 'key 0x2e\n' + nSHIFT # .
MPLAY_PREV_SONG = SHIFT + 'key 0x2c\n' + nSHIFT # ,

#MPLAYER Menus
mplayer =  "R fwd 10 sec\n,Up vol up\n"
mplayers = "L quit R full\n,U pause D mute\n"
mplayer_menu = "Return\n,Volume Up\n,Volume Down\n,Toggle Mute\n,Toggle Play\n,Next Media\n,Prev Media\n,Fullscreen\n,Fwd 10 sec\n,Rev 10 sec\n,Fwd 1 min\n,Rev 1 min\n,Mplayer Quit\n"

'''
Normal shortcuts
  Menu Based, with shortcut action keys to control selected mplayer session
  u - vol up
  d - vol down
  l - lock screen
  r - mute
s+u - htop
s+d - folder
s+s - return

'''
#Normal VERBS - these match up with openbox's ~/.config/openbox/rc.xml
NORM_DELAY = 'usleep 200\n'
NORM_TOGGLE_MUTE = WIN + 'key 0\n' + nWIN
NORM_VOL_UP = WIN + 'key 0x3d\n' + nWIN
NORM_VOL_DOWN = WIN + 'key 0x2d\n' + nWIN
NORM_LOCK_SCREEN = WIN + 'key L\n' + nWIN
NORM_HTOP = WIN + 'key H\n' + nWIN
NORM_FOLDER = WIN + 'key E\n' + nWIN

#MPLAYER Menus
normal =  "U Vol - R Mute\n,L Lockscreen\n"
normals = "U htop d folder\n,L and R free\n"
normal_menu = "Return\n,Volume Up\n,Volume Down\n,Toggle Mute\n,Lock Screen\n,Htop\n,Folder\n"

#Menu index
hotkeys = "Return\n,Normal keys\n,Normal menu\n,tmux keys\n,tmux menu\n,mplayer keys\n,mplayer menu\n,cmus\n"

#from http://stackoverflow.com/questions/18101299/how-to-run-shortkeys-using-python
def keypress(sequence):
  p = subprocess.Popen(['xte'], stdin=subprocess.PIPE)
  p.communicate(input=sequence)

def hotkey_menu(ser,width_lcd, height_lcd):
  index = 0
  cursor = 0
  options = hotkeys.split(',')

  while 1:
    #show menu
    print "hotkey loop"
    ser.write('W')
    sleep(.1)
    ser.write(options[index])
    sleep(.1)
    ser.write(options[index+1])
    ser.write(chr(cursor))
    sleep(.1)

    #Now Ard sends us button presses
    ser.readline()
    sleep(.1)
    ser.write('B')
    while 1:
      sleep(.1)
      byte = ser.read()
      #byte = sys.stdin.read(1)

      #if byte == 'r': #Right
      if byte == 'u': #UP
        if cursor == 1:
          cursor = 0
        elif index > 0:
          index = index - 1
        break
      if byte == 'd': #Down
        if index < len(options) - height_lcd:
          index = index + 1
          cursor = 0
        else:
          cursor = 1
        break
      #if byte == 'l': #Left
      if byte == 's': #Select
        if options[index + cursor] == "Return\n":
          return
        if options[index + cursor] == "tmux keys\n":
          hotkey_tmux(ser,width_lcd, height_lcd)
          break
        if options[index + cursor] == "tmux menu\n":
          hotkey_tmux_menu(ser,width_lcd, height_lcd)
          break
        if options[index + cursor] == "mplayer keys\n":
          hotkey_mplayer(ser,width_lcd, height_lcd)
          break
        if options[index + cursor] == "mplayer menu\n":
          hotkey_mplayer_menu(ser,width_lcd, height_lcd)
          break
        if options[index + cursor] == "Normal keys\n":
          hotkey_normal(ser,width_lcd, height_lcd)
          break
        if options[index + cursor] == "Normal menu\n":
          hotkey_normal_menu(ser,width_lcd, height_lcd)
          break
        break


def hotkey_tmux_menu(ser,width_lcd, height_lcd):
  index = 0
  cursor = 0
  options = tmux_menu.split(',')

  while 1:
    #show menu
    ser.write('W')
    sleep(.1)
    ser.write(options[index])
    sleep(.1)
    ser.write(options[index+1])
    ser.write(chr(cursor))
    sleep(.1)

    #Now Ard sends us button presses
    ser.readline()
    sleep(.1)
    ser.write('B')
    while 1:
      sleep(.1)
      byte = ser.read()
      #byte = sys.stdin.read(1)

      #if byte == 'r': #Right
      if byte == 'u': #UP
        if cursor == 1:
          cursor = 0
        elif index > 0:
          index = index - 1
        break
      if byte == 'd': #Down
        if index < len(options) - height_lcd:
          index = index + 1
          cursor = 0
        else:
          cursor = 1
        break
      #if byte == 'l': #Left
      if byte == 's': #Select
        if options[index + cursor] == "Return\n":
          return
        if options[index + cursor] == "Pane Up\n":
          keypress(TMUX_SEL_PANE_UP)
          break
        if options[index + cursor] == "Pane Down\n":
          keypress(TMUX_SEL_PANE_DOWN)
          break
        if options[index + cursor] == "Pane Left\n":
          keypress(TMUX_SEL_PANE_LEFT)
          break
        if options[index + cursor] == "Pane Right\n":
          keypress(TMUX_SEL_PANE_RIGHT)
          break
        if options[index + cursor] == "Split Vert\n":
          keypress(TMUX_SPLIT_VERT)
          break
        if options[index + cursor] == "Split Horz\n":
          keypress(TMUX_SPLIT_HORZ)
          break
        if options[index + cursor] == "Exit Selected\n":
          keypress(TMUX_EXIT)
          break
        if options[index + cursor] == "Prev Win\n":
          keypress(TMUX_PREV_WIN)
          break
        if options[index + cursor] == "Next Win\n":
          keypress(TMUX_NEXT_WIN)
          break
        if options[index + cursor] == "View Sessions\n":
          keypress(TMUX_VIEW_SESSIONS)
          break



def hotkey_tmux(ser,width_lcd, height_lcd):
  index = 0
  cursor = 0
  sel_cnt = 0

  while 1:
    #show menu
    options = tmux.split(',')
    ser.write('F')
    sleep(.1)
    ser.write(options[index])
    sleep(.1)
    ser.write(options[index+1])
    sleep(.1)

    #Now Ard sends us button presses
    ser.readline()
    sleep(.1)
    ser.write('B')
    while 1:
      sleep(.1)
      byte = ser.read()
      #byte = sys.stdin.read(1)

      # Select + Arrow Keys
      if byte == 'u' and sel_cnt == 1:
        sel_cnt = 0
        keypress(TMUX_SPLIT_VERT)
        options = tmux.split(',')
        break
      if byte == 'd' and sel_cnt == 1:
        sel_cnt = 0
        keypress(TMUX_SPLIT_HORZ)
        options = tmux.split(',')
        break
      if byte == 'l' and sel_cnt == 1:
        sel_cnt = 0
        keypress(TMUX_PREV_WIN)
        options = tmux.split(',')
        break
      if byte == 'r' and sel_cnt == 1:
        sel_cnt = 0
        keypress(TMUX_NEXT_WIN)
        options = tmux.split(',')
        break
      # Arrow keys
      if byte == 'u': #UP
        keypress(TMUX_SEL_PANE_UP)
        break
      if byte == 'd': #Down
        keypress(TMUX_SEL_PANE_DOWN)
        break
      if byte == 'l': #Left
        keypress(TMUX_SEL_PANE_LEFT)
        break
      if byte == 'r': #Right
        keypress(TMUX_SEL_PANE_RIGHT)
        break
      if byte == 's': #Select
        if sel_cnt == 1:
          return
        sel_cnt = 1
        #Print custom menu?
        options = tmuxs.split(',')
        ser.write('F')
        sleep(.1)
        ser.write(options[index])
        sleep(.1)
        ser.write(options[index+1])
        sleep(.1)
        ser.readline()
        ser.write('B')


def hotkey_mplayer_menu(ser,width_lcd, height_lcd):
  index = 0
  cursor = 0
  options = mplayer_menu.split(',')
  play_toggle = 0

  while 1:
    #show menu
    ser.write('W')
    sleep(.1)
    ser.write(options[index])
    sleep(.1)
    ser.write(options[index+1])
    ser.write(chr(cursor))
    sleep(.1)

    #Now Ard sends us button presses
    ser.readline()
    sleep(.1)
    ser.write('B')
    while 1:
      sleep(.1)
      byte = ser.read()
      #byte = sys.stdin.read(1)

      #if byte == 'r': #Right
      if byte == 'u': #UP
        if cursor == 1:
          cursor = 0
        elif index > 0:
          index = index - 1
        break
      if byte == 'd': #Down
        if index < len(options) - height_lcd:
          index = index + 1
          cursor = 0
        else:
          cursor = 1
        break
      #if byte == 'l': #Left
      if byte == 's': #Select
        if options[index + cursor] == "Return\n":
          return
        if options[index + cursor] == "Volume Up\n":
          keypress(MPLAY_VOL_UP)
          break
        if options[index + cursor] == "Volume Down\n":
          keypress(MPLAY_VOL_DOWN)
          break
        if options[index + cursor] == "Toggle Mute\n":
          keypress(MPLAY_TOGGLE_MUTE)
          break
        if options[index + cursor] == "Toggle Play\n":
          if play_toggle == 1:
            play_toggle = 0
            keypress(MPLAY_TOGGLE_PLAY)
          else:
            play_toggle = 1
            keypress(MPLAY_VOL_UP)
            sleep(.1)
            keypress(MPLAY_VOL_DOWN)
            sleep(.1)
            keypress(MPLAY_VOL_DOWN)
          break
        if options[index + cursor] == "Next Media\n":
          keypress(MPLAY_NEXT_SONG)
          break
        if options[index + cursor] == "Prev Media\n":
          keypress(MPLAY_PREV_SONG)
          break
        if options[index + cursor] == "Fullscreen\n":
          keypress(MPLAY_FULL_SCREEN)
          break
        if options[index + cursor] == "Fwd 10 sec\n":
          keypress(MPLAY_FWD_10SEC)
          break
        if options[index + cursor] == "Rev 10 sec\n":
          keypress(MPLAY_RWD_10SEC)
          break
        if options[index + cursor] == "Fwd 1 min\n":
          keypress(MPLAY_FWD_1MIN)
          break
        if options[index + cursor] == "Rev 1 min\n":
          keypress(MPLAY_RWD_1MIN)
          break
        if options[index + cursor] == "Mplayer Quit\n":
          keypress(MPLAY_QUIT)
          break

def hotkey_mplayer(ser,width_lcd, height_lcd):
  index = 0
  cursor = 0
  sel_cnt = 0
  play_toggle = 0

  while 1:
    #show menu
    options = mplayer.split(',')
    ser.write('F')
    sleep(.1)
    ser.write(options[index])
    sleep(.1)
    ser.write(options[index+1])
    sleep(.1)

    ser.readline()
    sleep(.1)
    #Now Ard sends us button presses
    ser.write('B')
    while 1:
      sleep(.1)
      byte = ser.read()
      #byte = sys.stdin.read(1)

      # Select + Arrow Keys
      if byte == 'u' and sel_cnt == 1:
        sel_cnt = 0
        if play_toggle == 1:
          play_toggle = 0
          keypress(MPLAY_TOGGLE_PLAY)
        else:
          play_toggle = 1
          keypress(MPLAY_VOL_UP)
          sleep(.1)
          keypress(MPLAY_VOL_DOWN)
          sleep(.1)
          keypress(MPLAY_VOL_DOWN)
        options = mplayer.split(',')
        break
      if byte == 'd' and sel_cnt == 1:
        sel_cnt = 0
        keypress(MPLAY_TOGGLE_MUTE)
        options = mplayer.split(',')
        break
      if byte == 'l' and sel_cnt == 1:
        sel_cnt = 0
        keypress(MPLAY_QUIT)
        options = mplayer.split(',')
        break
      if byte == 'r' and sel_cnt == 1:
        sel_cnt = 0
        keypress(MPLAY_FULL_SCREEN)
        options = mplayer.split(',')
        break
      # Arrow keys
      if byte == 'u': #UP
        keypress(MPLAY_VOL_UP)
        break
      if byte == 'd': #Down
        keypress(MPLAY_VOL_DOWN)
        break
      if byte == 'l': #Left
        keypress(MPLAY_RWD_10SEC)
        break
      if byte == 'r': #Right
        keypress(MPLAY_FWD_10SEC)
        break
      if byte == 's': #Select
        if sel_cnt == 1:
          return
        sel_cnt = 1
        #Print custom menu?
        options = mplayers.split(',')
        ser.write('F')
        sleep(.1)
        ser.write(options[index])
        sleep(.1)
        ser.write(options[index+1])
        sleep(.1)
        ser.readline()
        ser.write('B')


def hotkey_normal_menu(ser,width_lcd, height_lcd):
  index = 0
  cursor = 0
  options = normal_menu.split(',')
  play_toggle = 0

  while 1:
    #show menu
    ser.write('W')
    sleep(.1)
    ser.write(options[index])
    sleep(.1)
    ser.write(options[index+1])
    ser.write(chr(cursor))
    sleep(.1)

    #Now Ard sends us button presses
    ser.readline()
    sleep(.1)
    ser.write('B')
    while 1:
      sleep(.1)
      byte = ser.read()
      #byte = sys.stdin.read(1)

      #if byte == 'r': #Right
      if byte == 'u': #UP
        if cursor == 1:
          cursor = 0
        elif index > 0:
          index = index - 1
        break
      if byte == 'd': #Down
        if index < len(options) - height_lcd:
          index = index + 1
          cursor = 0
        else:
          cursor = 1
        break
      #if byte == 'l': #Left
      if byte == 's': #Select
        if options[index + cursor] == "Return\n":
          return
        if options[index + cursor] == "Volume Up\n":
          keypress(NORM_VOL_UP)
          break
        if options[index + cursor] == "Volume Down\n":
          keypress(NORM_VOL_DOWN)
          break
        if options[index + cursor] == "Toggle Mute\n":
          keypress(NORM_TOGGLE_MUTE)
          break
        if options[index + cursor] == "Lock Screen\n":
          keypress(NORM_LOCK_SCREEN)
          break
        if options[index + cursor] == "Htop\n":
          keypress(NORM_HTOP)
          break
        if options[index + cursor] == "Folder\n":
          keypress(NORM_FOLDER)
          break

def hotkey_normal(ser,width_lcd, height_lcd):
  index = 0
  cursor = 0
  sel_cnt = 0

  while 1:
    #show menu
    options = normal.split(',')
    ser.write('F')
    sleep(.1)
    ser.write(options[index])
    sleep(.1)
    ser.write(options[index+1])
    sleep(.1)

    ser.readline()
    sleep(.1)
    #Now Ard sends us button presses
    ser.write('B')
    while 1:
      sleep(.1)
      byte = ser.read()
      #byte = sys.stdin.read(1)

      # Select + Arrow Keys
      if byte == 'u' and sel_cnt == 1:
        sel_cnt = 0
        keypress(NORM_HTOP)
        options = normal.split(',')
        break
      if byte == 'd' and sel_cnt == 1:
        sel_cnt = 0
        keypress(NORM_FOLDER)
        options = normal.split(',')
        break
      if byte == 'l' and sel_cnt == 1:
        sel_cnt = 0
        #keypress(MPLAY_RWD_1MIN)
        options = normal.split(',')
        break
      if byte == 'r' and sel_cnt == 1:
        sel_cnt = 0
        #keypress(MPLAY_FWD_1MIN)
        options = normal.split(',')
        break
      # Arrow keys
      if byte == 'u': #UP
        keypress(NORM_VOL_UP)
        break
      if byte == 'd': #Down
        keypress(NORM_VOL_DOWN)
        break
      if byte == 'l': #Left
        keypress(NORM_LOCK_SCREEN)
        break
      if byte == 'r': #Right
        keypress(NORM_TOGGLE_MUTE)
        break
      if byte == 's': #Select
        if sel_cnt == 1:
          return
        sel_cnt = 1
        #Print custom menu?
        options = normals.split(',')
        ser.write('F')
        sleep(.1)
        ser.write(options[index])
        sleep(.1)
        ser.write(options[index+1])
        sleep(.1)
        ser.readline()
        ser.write('B')




