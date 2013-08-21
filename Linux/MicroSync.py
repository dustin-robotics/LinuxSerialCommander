#! /usr/bin/env python
""" MicroSync is a program which communicates with an ATMEGA168 with LCD and 5 buttons.
 The pair cooperate, allowing you to tell the Computer/RaspberryPi to do things for
 you, such as configuring a Wifi dongle to connect to a network. The script would
 need the appropriate permissions to access the commands, in which case you'd need
 to run the script under sudo.

 ArdSync communicates with the microprocessor to discover the size of screen the device has,
 then showing the appropriate menu items taylored to the particular screen (eg 16x2).

Copyright (C) 2013  Dustin Reynolds - See license restrictions at bottom


Usage: python MicroSync.py [options] [input file]

Options:
    -h,  --help          show this help
    -v,  --verbose       show additional information
    -i,   --interface    Specify serial interface to broadcast
                         firmware file over, default /dev/ttyUSB0

Examples:
    MicroSync.py -v -i /dev/ttyUSB0
    """
import subprocess
import serial
import socket
import glob
import sys
import getopt
import platform
from time import sleep

#custom libraries
import hotkey

menu = "Show Stats\n,Run Programs\n,Hotkey Comm\n,Connect WAN\n"

def scan():
    """scan for available ports. return a list of device names."""
    if is_windows:
        # scan for available ports. return a list of tuples (num, name)
        available = []
        for i in range(256):
            try:
                s = serial.Serial(i)
                available.append( (i, s.portstr))
                s.close()
            except serial.SerialException:
                pass
        return available
    else:
        return glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*')

def usage():
    print __doc__

class FileProc:
    "File processing utilities"

    def __init__(self):
        """Main processing occurs within the FileProc class"""
        #define global variables modified in this def

        #self.setArc()
        #pfile = self.parse(fileloc)
        #if _parsed_file == 0:
        #    print "Problem parsing hex file, please check file again"
        #    sys.exit()

        #file parsed successfully, initiate remote reset
        #print "Attempting to start communication"
        if _verbose == 1:  print "Open port " + _iface + ' with baud rate = 19200, 8 data bits, 1 stop bit, 1 sign bit with a 1 second timeout'

        ser = serial.Serial(_iface, 19200, timeout = 1 )

        ser.setDTR(0)
        sleep(0.1)                  #wait 100ms
        #ser.setRTS(1)             #Clear RTS
        ser.setDTR(1)
        sleep(2)

        ser.read()

        ser.write('H') # send hello

        #Read response
        line = ser.readline()

        s = line.split(",")
        if(len(s) < 3):
          print s
          ser.close()
          sys.exit()

        name = s[0]
        width = s[1]
        height = s[2]
        index = 0
        options = menu.split(',')
        cursor = 0
        ser.readline()

        #Now that we know who we are talking to, loop here, interacting with arduino
        while 1:
          #display desired menu
          print "new loop"
          ser.write('W')
          sleep(.1)
          ser.write(options[index])
          sleep(.1)
          ser.write(options[index+1])
          ser.write(chr(cursor))
          sleep(.1)

          ser.readline()
          sleep(.1)
          #Now Ard sends us button presses
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
              if index < len(options) - 2:
                index = index + 1
                cursor = 0
              else:
                cursor = 1
              break
            #if byte == 'l': #Left
            if byte == 's': #Select
              if options[index + cursor] == "Show Stats\n":
                # Get IP address
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("ritobocs.info",80))
                known_ip = s.getsockname()[0] + '\n'
                s.close()

                # Get CPU, MEM
                p = subprocess.Popen("bash scripts/stats.sh", stdout=subprocess.PIPE, shell=True)
                (output, err) = p.communicate()
                #write it out now
                ser.write('F')
                sleep(.1)
                ser.write(known_ip)
                sleep(.1)
                ser.write(output)
                sleep(3)
                ser.readline()
                break
              if options[index + cursor] == "Run Programs\n":
                self.run_programs(ser,int(width),int(height))
                break
              if options[index + cursor] == "Hotkey Comm\n":
                hotkey.hotkey_menu(ser,int(width),int(height))
                break

              if options[index + cursor] == "Connect WAN\n":
                #perform wireless scan
                p = subprocess.Popen("iwlist wlan0 scan | grep 'ESSID' | sed -e 's/^\s*//' -e '/^$/d'", stdout=subprocess.PIPE, shell=True)
                (output, err) = p.communicate()
                if len(output) == 0:
                  break
                output = output.replace('\\','')
                output = output.replace('"','')
                proc = output.split('\n')
                proc = [x for x in proc if not len(x) < 7]

                #print len(proc)

                (essid,password) = self.wlan_config(ser,proc)
                print essid
                print password
                #Wont work because we have WPA, not WEP.  Look at WPA links, waiting for nm-cli v 9.6+
                #http://unix.stackexchange.com/questions/80126/how-to-connect-to-internet-using-nmcli
                #https://github.com/vikjon0/qfpynm
                #https://mail.gnome.org/archives/networkmanager-list/2012-May/msg00053.html
                #http://crunchbang.org/forums/viewtopic.php?id=16624
                #p = subprocess.Popen("iwconfig wlan0 essid " + str(essid) + " key " + str(password) + " ", stdout=subprocess.PIPE, shell=True)
                #(output2,err2) = p.communicate()
                #print "output2 = "
                #print output2
                #print "err2 = "
                #print err2
              break

    def run_programs(self,ser,width_lcd,height_lcd):
      global _scriptdir

      #Get pwd if _scriptdir not provided
      if len(_scriptdir) == 0:
        p = subprocess.Popen("pwd", stdout=subprocess.PIPE, shell=True)
        (pwd,err) = p.communicate()
        pwd = pwd.strip()
      else:
        pwd = _scriptdir

      # Need to loop through getting file information, showing ../ as top
      # folder
      #  scroll through files, if folder selected, navigate into it
      # if script chosen, attempt to run it
      # Sel + up - navigate up
      # Sel + down - navigate into folder
      # Sel + left - quit
      # Sel + right - execute?
      # Sel + sel - Execute?

      index = 0
      cursor = 0
      sel_cnt = 0
      cutoff = width_lcd - height_lcd; # 0 - FileManager (C, D, etc), 1 - Cursor

      p = subprocess.Popen("cd " + pwd + " && ls -F --group-directories-first", stdout=subprocess.PIPE, shell=True)
      (ls1,err) = p.communicate()
      ls2 = ls1.split('\n')
      ls2.insert(0,'../')

      while 1:
        #show files in directory
        ser.write('W')
        sleep(.1)
        if len(ls2[index]) > cutoff:
          ser.write(ls2[index][:cutoff-6] + "~" + ls2[index][-6:] + '\n')
        else:
          ser.write(ls2[index] + '\n')

        sleep(.1)

        if len(ls2[index+1]) > cutoff:
          ser.write(ls2[index+1][:cutoff-6] + "~" + ls2[index+1][-6:] + '\n')
        else:
          ser.write(ls2[index+1] + '\n')

        ser.write(chr(cursor))
        sleep(.1)

        print ls2[index]
        ser.readline()
        sleep(.1)
        #read Ok\n
        #Now Ard sends us button presses
        ser.write('B')
        while 1:
          sleep(.1)
          byte = ser.read()
          #byte = sys.stdin.read(1)

          if byte == 'u' and sel_cnt == 0: #UP
            if cursor == 1:
              cursor = 0
            elif index > 0:
              index = index - 1
            break
          if byte == 'u' and sel_cnt == 1: #navigate up
            sel_cnt = 0
            pwd = pwd + '/' + '../'
            index = 0;
            cursor = 0;
            p = subprocess.Popen("cd " + pwd + " && pwd", stdout=subprocess.PIPE, shell=True)
            (pwd,err) = p.communicate()
            pwd = pwd.strip()
            p = subprocess.Popen("cd " + pwd + " && ls -F --group-directories-first", stdout=subprocess.PIPE, shell=True)
            (ls1,err) = p.communicate()
            ls2 = ls1.split('\n')
            ls2.insert(0,'../')
            break
          if byte == 'd': #Down
            sel_cnt = 0
            if index < len(ls2) - 3:
              index = index + 1
              cursor = 0
            else:
              cursor = 1
            break
          if byte == 'l': #Left
            return
            break
          if byte == 'r' and sel_cnt == 1: #Right
            #to make it here, select would have to be pushed twice
            sel_cnt = 0
            #if folder, cd to it
            if ls2[index+cursor][-1:] == '/':
              pwd = pwd + '/' + ls2[index+cursor]
              index = 0;
              cursor = 0;
              print pwd
              p = subprocess.Popen("cd " + pwd + " && pwd", stdout=subprocess.PIPE, shell=True)
              (pwd,err) = p.communicate()
              pwd = pwd.strip()
              p = subprocess.Popen("cd " + pwd + " && ls -F --group-directories-first", stdout=subprocess.PIPE, shell=True)
              (ls1,err) = p.communicate()
              ls2 = ls1.split('\n')
              ls2.insert(0,'../')
              break
            else:
              if ls2[index+cursor][-1:] == '*':
                p = subprocess.Popen("cd " + pwd + " && ./" + ls2[index+cursor][:-1] + " & exit", stdout=subprocess.PIPE, shell = True)
                sleep(5)
                if p.poll() is None:
                  p.kill()
                  print 'timed out'
              else:
                if ls2[index+cursor][-4:-1] == '.mp': #if an mp4, open up in mplayer
                  p = subprocess.Popen("cd " + pwd + " && terminator -x mplayer " + pwd + "/" + ls2[index+cursor] + " ", stdout=subprocess.PIPE, shell = True)
                  hotkey.hotkey_mplayer(ser,int(width_lcd),int(height_lcd))
                  if p.poll() is None:
                    p.kill()
                else:
                  p = subprocess.Popen("cd " + pwd + " && ./" + ls2[index+cursor] + " & exit", stdout=subprocess.PIPE, shell = True)
                  sleep(5)
                  if p.poll() is None:
                    p.kill()
                    print 'timed out'
              (cmd1,err1) = p.communicate()
              print err1
              sleep (3)
              if cmd1 and len(cmd1) > 0:
                #show the output from the command
                cmd2 = cmd1.split('\n')
                #write it out now
                ser.write('F')
                sleep(.1)
                ser.write(self.resize_string(cmd2[0], cutoff + 1))
                sleep(.1)
                ser.write(self.resize_string(cmd2[1], cutoff + 1))
                sleep(3)
                ser.readline()
              elif err1 and len(err1) > 0:
                #show the output from the error
                cmd2 = cmd1.split('\n')
                #write it out now
                ser.write('F')
                sleep(.1)
                ser.write(resize_string(cmd2[0], cutoff + 1))
                sleep(.1)
                ser.write(resize_string(cmd2[1], cutoff + 1))
                sleep(3)
                ser.readline()
            break
          if byte == 's': #Select
            if sel_cnt == 0:
              sel_cnt = 1
              break
            #to make it here, select would have to be pushed twice
            sel_cnt = 0
            break


    def resize_string(self,phrase,cutoff):
      if len(phrase) > cutoff:
        return str(phrase[:cutoff-6] + "~" + phrase[-6:])
      else:
        return str(phrase)

    def sanitize_string(self,phrase):
      #print str(phrase.replace(" ","\ "))
      return str(phrase.replace(" ","\ "))

    def wlan_config(self,ser, proc):
      index = 0
      cursor = 0
      while 1:
        #show menu for each WLAN ESSID
        ser.write('W')
        sleep(.1)
        ser.write(proc[index].rsplit(':',1)[1] + '\0' + '\n')
        sleep(.1)
        ser.write(proc[index+1].rsplit(':',1)[1] + '\0' + '\n')
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
            if index < len(proc) - 2:
              index = index + 1
              cursor = 0
            else:
              cursor = 1
            break
          #if byte == 'l': #Left
          if byte == 's': #Select
            #Selected ESSID, now prompt for password
            ser.write('P')
            while(1):
              password = ser.readline();
              if(len(password) != 0):
                password = password.strip();
                return (proc[index+cursor].rsplit(':',1)[1] + '\0', password)
            return

def main(argv):
    #determine OS
    global is_windows
    is_windows = (platform.system().lower().find("win") > -1)

    try:
        #To test this in python, do args = '-hvp ATMEGA168 /home/test'.split()
        #then do getopt.getopt(argv,  "hvp:", ["help", "--verbose"])
        opts,  args = getopt.getopt(argv,  'hvi:s:', ['help', 'verbose', 'interface', 'scriptdir'])
        #detect if no inputs are given
    except getopt.GetoptError:
        usage()
        print "\nThe available interfaces are: " + str(scan()) + "\n"
        sys.exit(2)
    #setup global variables
    global _verbose ; _verbose = 0
    global _iface ; _iface = '/dev/ttyUSB0'
    global _scriptdir; _scriptdir = ''

    for opt,  arg in opts:
        if opt in ("-h",  "--help"):
          usage()
          sys.exit(2)
        if opt in ('-v', '--verbose'):
          _verbose = 1
        if opt in ('-i', '--interface'):
          _iface = arg
        if opt in ('-s', '--scriptdir'):
          _scriptdir = arg

    FileProc()


if __name__=='__main__':
    main(sys.argv[1:])
"""
 * This program is free software; you can redistribute it and/or modify it     *
 * under the terms of the GNU General Public License as published by the Free  *
 * Software Foundation; either version 3 of the License, or (at your option)   *
 * any later version.                                                          *
 *                                                                             *
 * This program is distributed in the hope that it will be useful, but WITHOUT *
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    *
 * more details.                                                               *
 *                                                                             *
 * You should have received a copy of the GNU General Public License along     *
 * with this program; if not, see <http://www.gnu.org/licenses/>.              *"""

