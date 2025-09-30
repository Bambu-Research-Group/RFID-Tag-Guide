# -*- coding: utf-8 -*-

# Python script to extract the keys from a Bambu Lab filament RFID tag, using a Proxmark3
# Created for https://github.com/Bambu-Research-Group/RFID-Tag-Guide

import subprocess
import os
import re
import sys
from pathlib import Path

from lib import strip_color_codes, get_proxmark3_location, run_command, testCommands

#Global variables
#Default name of the dictionary file we create
dictionaryFilename = "myKeyDictionary.dic"  #Arbitrary filename for storing dictionary file
dictionaryFilepath = ""                     #Calculated. Absolute path to dictionary file
dictionaryFile = ""                         #File object for writing keys

pm3Location = None                            #Calculated. The location of Proxmark3
pm3Command = "bin/pm3"                      # The command that works to start proxmark3
mfNonceBruteCommand = "share/proxmark3/tools/mf_nonce_brute" # The command to execute mfNonceBrute

def setup():
    global pm3Location,dictionaryFilepath

    pm3Location = get_proxmark3_location()
    if not pm3Location:
        exit(-1)

    #Create a dictionary file to store keys that we discover
    print(f"Creating dictionary file '{dictionaryFilename}'")
    dictionaryFile = open(dictionaryFilename, "w")
    dictionaryFile.close()
    dictionaryFilepath = os.path.abspath(dictionaryFilename)
    print(f"Saved dictionary to {dictionaryFilepath}")

def main():
    print("--------------------------------------------------------")
    print("RFID Key Extractor v0.2.1 - Bambu Research Group 2024")
    print("--------------------------------------------------------")
    print("This will extract the keys from a trace file")
    print("that was saved from sniffing communication between")
    print("the AMS and RFID tag.")
    print("")
    print("Instructions to sniff and save the trace can be found at")
    print("https://github.com/Bambu-Research-Group/RFID-Tag-Guide")
    print("--------------------------------------------------------")
    print("")

    # Run setup
    setup()

    if len(sys.argv) > 1:
        # If the user included an argument, assume it's the path to the tracefile
        trace = os.path.abspath(sys.argv[1])
    else:
        #Instruct the user to create a trace file
        print()
        print("Start by creating a trace file. In the proxmark terminal, execute command `hf 14a sniff -c -r`.")
        print("Then, place the Proxmark3 between the RFID reader and spool.")
        print("Load in filament and wait for the process to complete, then press the button on the Proxmark3.")
        print("Finally, in the proxmark terminal, execute command `trace save -f [FILEPATH]` to create the trace file.")
        print("See the GitHub repository for more details.")
        print()

        #Get the tracename/filepath from user
        trace = input("Enter trace name or full trace filepath: ")

    discoverKeys(trace)
    
    print("Keys obtained. Remove the spool from the AMS and place the Proxmark3 on the spool's tag.")
    print(f"In proxmark terminal, execute command `hf mf fchk -f {dictionaryFilepath} --dump` to create a keyfile from this dictionary.")
    print("Then, execute `hf mf dump` to dump the contents of the RFID tag.")


#Loop 16 times to attempt to extract all 16 keys from the tracefile
def discoverKeys(traceFilepath):

    print("PROGRAM: ", mfNonceBruteCommand)

    keyList = []

    # Run a max of 16 times.
    for i in range(16):
        loopNum = i+1
        print("----------------------")
        print(f"Loop {loopNum} of 16")

        #Run PM3 with the trace
        # -o means run without connecting to PM3 hardware
        # -c specifies commands within proxmark 3 software
        print(f"Viewing tracelog with {len(keyList)} discovered keys")
        output = run_command([pm3Location / pm3Command,"-o","-c", f"trace load -f {traceFilepath}; trace list -1 -t mf -f {dictionaryFilepath}"])

        #Loop over output, line by line to try to find a key
        #3 things we're looking for:
        #   - "key" a known key
        #   - "probable key" a key that should work
        #   - "mf_nonce_brute" a key we need to calculate
        for line in output.splitlines():
            if " key " in line or " key: " in line:

                #There's a lot of whitespace in this line
                #replace multiple whitespaces with a single space for readability
                line = ' '.join(line.split())

                print()
                print("Found line containing a key:")
                print(f"    {line}")
                # split the line into "words", which are whitespace separated
                words = line.split(" ")

                key = ""

                #find the word "key", and then grab the word directly after it
                for j in range(len(words)-1):
                    w = words[j]
                    if w == "key" or w == "key:":
                        key = words[j+1]  #Guaranteed to not be out of bounds because we loop to words length - 1
                        break

                #If we didn't find a key, skip this line
                if key == "":
                    continue
                
                #If key ends with a vertical bar |, remove it
                key = key.replace('|', '')
                key = key.upper()

                #Add this key to our keylist if it's new
                if key in keyList:
                    print(f"    Duplicate key, ignoring: {key}")
                    continue
                
                keyList.append(key)
                print(f"    Found new key: {key}")
                
            if "mf_nonce_brute" in line:
                print()
                print("Found line requiring decoding:")
                print(line)

                args = [] #Arguments passed into the brute force algorithm

                #Parse the command arguments#
                words = line.split(" ")
                for j in range(len(words)-1):
                    if "mf_nonce_brute" in words[j]:
                        #Add the rest of the line to our arguments
                        args = words[j+1:] #can't be out of bounds because we loop to len(words)-1
                        break

                key = bruteForce(args)

                #Remove color coding from string
                key = strip_color_codes(key)

                if key == "":
                    continue
                
                key = key.upper()

                #Add this key to our keylist if it's new
                if key in keyList:
                    print(f"    Duplicate key, ignoring: {key}")
                    continue
                
                keyList.append(key)
                print(f"    Found new key: {key}")
            
        #Print off all the keys we've found so far
        #Save them to our dictionary
        dictionaryFile = open(dictionaryFilename, "w")
        print()
        print("Found keys: ")
        for j in range(len(keyList)):
            print(f"    {j}: {keyList[j]}")
            dictionaryFile.write(keyList[j])
            dictionaryFile.write("\n")
        print()
        dictionaryFile.close()
    
    #Done! Show results
    print(f"{len(keyList)} keys saved to file: {dictionaryFilepath}")

#Run the mf_nonce_brute program with the provided arguments to decode a key
#Returns a key on success, "" otherwise
def bruteForce(args):
    print("Running bruteforce command:")
    output = run_command([pm3Location / mfNonceBruteCommand] + args)

    #Parse out the key
    for line in output.splitlines():
        #Search for the line that says valid key. Example: "Valid Key found [ 63654db94d97 ] - matches candidate"
        #In rare cases, multiple possible keys will be found. The "matches candidate" tag should indicate the right one
        if not ("Valid Key" in line and "matches candidate" in line):
            continue

        print(f"    {line}")

        #Parse out the key from within the brackets
        words = line.split(" ")
        for i in range(len(words)-1):
            if words[i] == "[":
                return words[i+1]
            
    return "" #Not found

if __name__ == "__main__":
    main() #Run main program
