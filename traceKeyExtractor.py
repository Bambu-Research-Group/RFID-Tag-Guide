import subprocess
import os
import re
import sys
from pathlib import Path

if not sys.version_info >= (3, 6):
   print("Python 3.6 or higher is required!")
   exit(-1)

# List of possible directories for Proxmark3 to try
# XXX Populate with results for Windows
pm3_dirs = []

#Global variables
#Default name of the dictionary file we create
dictionaryFilename = "myKeyDictionary.dic"  #Arbitrary filename for storing dictionary file
dictionaryFilepath = ""                     #Calculated. Absolute path to dictionary file
dictionaryFile = ""                         #File object for writing keys

pm3Location = None                            #Calculated. The location of Proxmark3
pm3Command = "bin/pm3"                      # The command that works to start proxmark3
mfNonceBruteCommand = "share/proxmark3/tools/mf_nonce_brute" # The command to execute mfNonceBrute

trace = "";                 #Prompted during runtime. Trace filename that the user provides

def main():
    global pm3Location,dictionaryFilepath,trace

    print("--------------------------------------------------------")
    print("RFID Key Extractor v0.2 - Bambu Research Group 2024")
    print("--------------------------------------------------------")
    print("This will extract the keys from a trace file")
    print("that was saved from sniffing communication between")
    print("the AMS and RFID tag.")
    print("");
    print("Instructions to sniff and save the trace can be found at")
    print("https://github.com/Bambu-Research-Group/RFID-Tag-Guide");
    print("--------------------------------------------------------")
    print("")

    pm3Location = get_proxmark3_location()

    #Create a dictionary file to store keys that we discover
    print(f"Creating dictionary file '{dictionaryFilename}'")
    dictionaryFile = open(dictionaryFilename, "w")
    dictionaryFile.close();
    dictionaryFilepath = os.path.abspath(dictionaryFilename)
    print(f"Saved dictionary to {dictionaryFilepath}")

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

    discoverKeys()
    
    print("Keys obtained. Remove the spool from the AMS and place the Proxmark3 on the spool's tag.")
    print(f"In proxmark terminal, execute command `hf mf fchk -f {dictionaryFilepath} --dump` to create a keyfile from this dictionary.")
    print("Then, execute `hf mf dump` to dump the contents of the RFID tag.")


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
        # -o means run without connecting to PM3 hardware
        # -c specifies commands within proxmark 3 software
        cmd_list = [pm3Location / pm3Command,"-o","-c", f"trace load -f {trace}; trace list -1 -t mf -f {dictionaryFilepath}; exit"];
        print(f"Viewing tracelog with {len(keyList)} discovered keys")
        print(f"pm3 {' '.join(cmd_list[1:])}")
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
    cmd_list = [pm3Location / mfNonceBruteCommand] + args
    print("    Running bruteforce command:")
    print("    ",end = "")
    print(f"tools/mf_nonce_brute {' '.join(cmd_list[1:])}")
    result = subprocess.run(cmd_list, shell=os.name == 'nt', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #Parse out the key
    output = result.stdout
    for line in output.splitlines():
        line = line.decode("utf-8") #Convert from byte array to string

        #Search for the line that says valid key. Example: "Valid Key found [ 63654db94d97 ] - matches candidate"
        #In rare cases, multiple possible keys will be found. The "matches candidate" tag should indicate the right one
        if not ("Valid Key" in line and "matches candidate" in line):
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

    # Check pm3_dirs paths
    pm3_dirs_result = testCommands(pm3_dirs, "bin/pm3", "--help")
    if pm3_dirs_result:
        print(f"Found installation in {pm3_dirs_result}!")
        return pm3_dirs_result

    # At this point, we've tried all the paths to find it
    print("Failed to find working 'pm3' command. You can set the Proxmark3 directory via the 'PROXMARK3_DIR' environment variable.")
    exit(-1) # Halt program

def run_command(command):
    try:
        # On Windows, use the shell=True argument to run the command
        result = subprocess.run(command, shell=os.name == 'nt', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Check the return code to determine if the command was successful
        if result.returncode == 0 or result.returncode == 1:
            return result.stdout.decode("utf-8").strip()
        return None
    except Exception as e:
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
        print("    Trying:", directory, end=" ... ")
        if run_command(cmd_list):
            return Path(directory)
    
    return None #We didn't find any program that worked



main(); #Run main program
