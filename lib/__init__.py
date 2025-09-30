# -*- coding: utf-8 -*-

# Common functions used throughout the project
# Created for https://github.com/Bambu-Research-Group/RFID-Tag-Guide

import subprocess
import os
import sys
import struct
from pathlib import Path
from datetime import datetime

if not sys.version_info >= (3, 6):
  raise Exception("Python 3.6 or higher is required!")

# Byte conversions
def bytes_to_string(data):
    return data.decode('ascii').replace('\x00', ' ').strip()

def bytes_to_hex(data, chunkify = False):
    output = data.hex().upper()
    return " ".join((output[0+i:2+i] for i in range(0, len(output), 2))) if chunkify else output

def bytes_to_int(data):
    return int.from_bytes(data, 'little')

def bytes_to_float(data):
    return struct.unpack('<f', data)[0]

def bytes_to_date(data):
    string = bytes_to_string(data)
    parts = string.split("_")
    if len(parts) < 5:
        return string # Not a date we can process, if it's a date at all
    return datetime(
        year=int(parts[0]),
        month=int(parts[1]),
        day=int(parts[2]),
        hour=int(parts[3]),
        minute=int(parts[4])
    )

#Some keys come surrounded in terminal color codes such as "[32m63654db94d97[0m"
#We need to remove these
def strip_color_codes(input_string):
    # Define the regular expression pattern to match ANSI escape sequences
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    # Use the sub method to replace the escape sequences with an empty string
    return ansi_escape.sub('', input_string)

def run_command(command, pipe=True):
    print(' '.join([str(c) for c in command]))
    try:
        # On Windows, use the shell=True argument to run the command
        result = subprocess.run(command, shell=os.name == 'nt', capture_output=pipe)
        # Check the return code to determine if the command was successful
        if result.returncode == 0 or result.returncode == 1:
            return result.stdout.decode("utf-8").strip() if pipe else ""
        return None
    except Exception as e:
        return None

def get_proxmark3_location():
    # Find a "pm3" command that works from a list of OS-specific possibilities
    print("Checking program: pm3")

    # Check PROXMARK3_DIR environment variable
    if os.environ.get('PROXMARK3_DIR'):
        if run_command(os.environ['PROXMARK3_DIR'] + "/bin/pm3", "--help"):
            return os.environ['PROXMARK3_DIR']
        else:
            print("Warning: PROXMARK3_DIR environment variable points to the wrong folder, ignoring")

    # Get Homebrew installation
    brew_install = run_command(["brew", "--prefix", "proxmark3"])
    if brew_install:
        print("Found installation via Homebrew!")
        return Path(brew_install)

    # Get global installation
    which_pm3 = run_command(["which", "pm3"])
    if which_pm3:
        which_pm3 = Path(which_pm3)
        pm3_location = which_pm3.parent.parent
        print(f"Found global installation ({pm3_location})!")
        return pm3_location

    # At this point, we've tried all the paths to find it
    print("Failed to find working 'pm3' command. You can set the Proxmark3 directory via the 'PROXMARK3_DIR' environment variable.")
    return None

# Test a list of commands to see which one works
# This lets us provide a list of OS-specific commands, test them
# and figure out which one works on this specific computer
# - Args: 
#       - commandList: An array of OS-specific commands (sometimes including absolute installation path)
#       - arguments: Optional arguments to be appended to the command. Useful for programs that don't exit on their own
# This returns the command (string) of the first working command we encounter
#
def testCommands(directories, command, arguments = ""):
    for directory in directories:
        if directory is None:
            continue

        #OPTIONAL: add arguments such as "--help" to help identify programs that don't exit on their own
        cmd_list = [directory+"/"+command, arguments]

        #Test if this program works
        print("Trying:", directory, end="...")
        if run_command(cmd_list):
            return Path(directory)
    
    return None #We didn't find any program that worked
