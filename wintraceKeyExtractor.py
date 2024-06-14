#########################
# CONFIGURATION (Begin) #
#########################
# Change these variables to match the install locations for your specific computer
# Some examples are provided, and you can comment/uncomment specific lines, or
# manually type them in if your computer differs from the examples

# -----------
# PM3 Program
# -----------
#The main proxmark program, for most installations, proxmark3 can be started
# with the command "pm3" in the terminal.
# If your computer doesn't recognize this, you may need to navigate to the actual
# installation directory

#List of possible commands to try
pm3 = [
    #"pm3",                                #Default installation location
    #"/usr/local/opt/proxmark3/bin/pm3",   #MAC Installataion - using BREW
    "proxmark3.exe"                                    #Windows specific install location TBD
   ]

# ---------------------------------
# Brute Force Tool (mf_nonce_brute)
# ---------------------------------
# This is a tool that comes with the PM3 program
# It is located in the "tools" directory of your PM3 installation location
mfNonceBrute = [
   # "/usr/local/opt/proxmark3/share/proxmark3/tools/mf_nonce_brute",  #MAC Install, using Brew
    "tools\mf_nonce_brute\mf_nonce_brute.exe"                                                                  #Windows TBD
]


#########################
# CONFIGURATION (End)   #
#########################
# Do not modify anything beyond this point, unless you're a developer


#Global variables
#Default name of the dictionary file we create
dictionaryFilename = "myKeyDictionary.dic"  #Arbitrary filename for storing dictionary file
dictionaryFilepath = ""                     #Calculated. Absolute path to dictionary file
dictionaryFile = ""                         #File object for writing keys

pm3Command = "";            #Calculated. The command that works to start proxmark3
mfNonceBruteCommand = ""    #Calculated. The command to execute mfNonceBrute

trace = "";                 #Prompted during runtime. Trace filename that the user provides

import subprocess
import os
import re

def main():
    global pm3Command, mfNonceBruteCommand,dictionaryFilepath,trace

    print("--------------------------------------------------------")
    print("RFID Key Extractor v0.1 - Bambu Research Group 2024")
    print("--------------------------------------------------------")
    print("This will extract the keys from a trace file")
    print("that was saved from sniffing communication between")
    print("the AMS and RFID tag.")
    print("");
    print("Instructions to sniff and save the trace can be found at")
    print("https://github.com/Bambu-Research-Group/RFID-Tag-Guide");
    print("--------------------------------------------------------")
    print("")

    # Find a "pm3" command that works from a list of OS-specific possibilities
    print("Checking program: pm3")
    pm3Command = testCommands(pm3,"--help"); #Execute "pm3 --help" to test if the install location works
    if pm3Command is None:
        print("Failed to find working PM3 command. Modify the \"pm3\" variable in this program to match your installation location")
        return; #Halt program

    # Find a "mf_nonce_brute" command that works from a list of OS-specific possibilities
    print("Checking program: mf_nonce_brute")
    mfNonceBruteCommand = testCommands(mfNonceBrute,""); #Execute "mf_nonce_brute" to test if the install location works
    if mfNonceBruteCommand is None:
        print("Failed to find working mf_nonce_brute command. Modify the \"mf_nonce_brute\" variable in this program to match your installation location")
        return; #Halt program

    #Create a dictionary file to store keys that we discover
    print(f"Creating dictionary file '{dictionaryFilename}'")
    dictionaryFile = open(dictionaryFilename, "w")
    dictionaryFile.close();
    dictionaryFilepath = os.path.abspath(dictionaryFilename)
    print(f"Saved dictionary to {dictionaryFilepath}")

    #Get the tracename/filepath from user
    print("");
    trace = input("Enter trace name or full trace filepath: ")

    discoverKeys();
    
    print(f"In proxmark terminal, execute command `hf mf fchk -f {dictionaryFilepath} --dump`")
    print(" to create a keyfile from this dictionary")
    print()
    print("Then execute `hf mf dump` to dump the contents of the RFID tag")


#Loop 16 times to attempt to extract all 16 keys from the tracefile
def discoverKeys():

    print("PROGRAM: ", mfNonceBruteCommand)

    keyList = [];

    # Run a max of 16 times.
    for i in range(16):
        loopNum = i+1;
        print("----------------------")
        print(f"Loop {loopNum} of 16")

        #Run PM3 with the trace
        # -o means run without connecting to PM3 hardware (mac)
        # -c specifies commands within proxmark 3 software
        cmd_list = [pm3Command,"-c", f"trace load -f {trace}; trace list -1 -t mf -f {dictionaryFilepath}; exit"]; #win
        print(f"Viewing tracelog with {len(keyList)} discovered keys")
        print(" ".join(cmd_list))
        result = subprocess.run(cmd_list, shell=os.name == 'nt',stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout;



        #print(output)

        #Loop over output, line by line to try to find a key
        #3 things we're looking for:
        #   - "key" a known key
        #   - "probable key" a key that should work
        #   - "mf_nonce_brute" a key we need to calculate
        for line in output.splitlines():
            line = line.decode("utf-8") #Convert from byte array to string

            if " key " in line or " key: " in line:

                #There's a lot of whitespace in this line
                #replace multiple whitespaces with a single space for readability
                line = ' '.join(line.split())

                print()
                print("Found line containing a key:")
                print(f"    {line}")
                # split the line into "words", which are whitespace separated
                words = line.split(" ");

                key = ""

                #find the word "key", and then grab the word directly after it
                for j in range(len(words)-1):
                    w = words[j];
                    if w == "key" or w == "key:":
                        key = words[j+1];  #Guaranteed to not be out of bounds because we loop to words length - 1
                        break

                #If we didn't find a key, skip this line
                if key == "":
                    continue;
                
                #If key ends with a vertical bar |, remove it
                key = key.replace('|', '')
                key = key.upper()

                #Add this key to our keylist if it's new
                if key in keyList:
                    print(f"    Duplicate key, ignoring: {key}")
                    continue;
                
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
                        break;

                key = bruteForce(args)

                #Remove color coding from string
                key = strip_color_codes(key)

                if key == "":
                    continue;
                
                key = key.upper()

                #Add this key to our keylist if it's new
                if key in keyList:
                    print(f"    Duplicate key, ignoring: {key}")
                    continue;
                
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
            dictionaryFile.write("\n");
        print()
        dictionaryFile.close();
    
    #Done! Show results
    print(f"{len(keyList)} keys saved to file: {dictionaryFilepath}")

#Run the mf_nonce_brute program with the provided arguments to decode a key
#Returns a key on success, "" otherwise
def bruteForce(args):
    cmd_list = [mfNonceBruteCommand] + args
    print("    Running bruteforce command:")
    print("    ",end = "")
    print(" ".join(cmd_list))
    result = subprocess.run(cmd_list, shell=os.name == 'nt', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #Parse out the key
    output = result.stdout
    for line in output.splitlines():
        line = line.decode("utf-8") #Convert from byte array to string

        #Search for the line that says valid key. Example: "Valid Key found [ 63654db94d97 ]
        if "Valid Key" not in line:
            continue

        print(f"    {line}")

        #Parse out the key from within the brackets
        words = line.split(" ");
        for i in range(len(words)-1):
            if words[i] == "[":
                return words[i+1]
            
    return "" #Not found

#Some keys come surrounded in terminal color codes such as "[32m63654db94d97[0m"
#We need to remove these
def strip_color_codes(input_string):
    # Define the regular expression pattern to match ANSI escape sequences
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    # Use the sub method to replace the escape sequences with an empty string
    return ansi_escape.sub('', input_string)

# Test a list of commands to see which one works
# This lets us provide a list of OS-specific commands, test them
# and figure out which one works on this specific computer
# - Args: 
#       - commandList: An array of OS-specific commands (sometimes including absolute installation path)
#       - arguments: Optional arguments to be appended to the command. Useful for programs that don't exit on their own
# This returns the command (string) of the first working command we encounter
#
def testCommands(commandList, arguments = ""):

    for command in commandList:

        #OPTIONAL: add arguments such as "--help" to help identify programs that don't exit on their own
        cmd_list = [command, arguments]

        #Test if this program works
        print("    Trying:", command, end=" ... ")
        try:
            # On Windows, use the shell=True argument to run the command
            result = subprocess.run(cmd_list, shell=os.name == 'nt', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Check the return code to determine if the command was successful
            if result.returncode == 0 or result.returncode == 1:
                print(" SUCCESS!")
                return command
        except Exception as e:
            #print(e) #DEBUG
            print(" FAIL");
            continue
    
    return None #We didn't find any program that worked



main(); #Run main program
