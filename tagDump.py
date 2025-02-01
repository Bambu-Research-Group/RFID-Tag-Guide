#!/usr/bin/env python3

import subprocess
import os
import sys
from pathlib import Path
import argparse
import shutil
from traceKeyExtractor import run_command, testCommands, get_proxmark3_location

# Attempt to load crypto dependancies needed for key derivation
try:
    from Cryptodome.Protocol.KDF import HKDF
    from Cryptodome.Hash import SHA256
    CRYPTO_INSTALLED=True
except Exception as e:
    print(e)
    print("=== WARNING: Please run 'pip install pycryptodomex' first to install required dependancies for full functionality ===")
    print()
    CRYPTO_INSTALLED=False

if not sys.version_info >= (3, 6):
   print("Python 3.6 or higher is required!")
   exit(-1)

#Global variables
DICTIONARY_FILEPATH = ""            #Calculated based on the tag UID
DICTIONARY_BIN_FILEPATH = ""        #Calculated based on the tag UID

PM3_LOCATION = None                 #Calculated. The location of Proxmark3 as a Path object
PM3_COMMAND = "bin/pm3"             #The command that works to start proxmark3
PM3_COMMAND_FAST = "bin/proxmark3"  #Command to start the proxmark3 faster, but requires the correct UART port
UART_PORT = ""                      #Calculated during first connection to Proxmark3, speeds up future connections

def main(args):
    global PM3_LOCATION,DICTIONARY_FILEPATH,DICTIONARY_BIN_FILEPATH

    print("---------------------------------------------------------------------------------")
    print("Bambu Filament RFID Tag QuickDump")
    print("---------------------------------------------------------------------------------")
    print("This will quickly dump the data drectly from a Bambu filament tag")
    print("Requires a Proxmark3 to be plugged in")
    print("MAKE SURE YOU DO NOT HAVE ANY OTHER TERMINALS ACTIVELY CONNECTED TO THE PROXMARK3")
    print("---------------------------------------------------------------------------------")
    print("")


    PM3_LOCATION = get_proxmark3_location()
    testResult = testProxmarkConnection()
    if testResult != 0:
        exit(testResult)

    print()
    print("Reading basic card data...")
    uid, backdoorKey, stdout, stderr = getTagData()
    if uid == "":
        print("UID not found in output, probably error reading card. Exiting.")
        print(stdout.decode("utf-8"))
        print(stderr.decode("utf-8"))
        exit(1)

    print(f"Tag UID: {uid}")
    print(f"Tag backdoor key: {backdoorKey}")
    print()

    outDir = Path(args.output_dir).resolve()
    if not outDir.is_dir():
        print(f"Specified output dir '{args.output_dir}' is not a directory, exiting")
        exit(1)

    dictionaryFilename = f"hf-mf-{uid}-key.dic"
    DICTIONARY_FILEPATH = str(outDir / dictionaryFilename)
    dictionaryBinFilename = f"hf-mf-{uid}-key.bin"
    DICTIONARY_BIN_FILEPATH = str(outDir / dictionaryBinFilename)

    usedBackdoorMethod = False
    if args.backdoor:
        out, err = dumpFromBackdoor(backdoorKey)
        usedBackdoorMethod = True

    elif CRYPTO_INSTALLED:
        print("Deriving tag keys...")
        generateDicitonaries(uid)

        print("Dumping tag data using derived keys, this will take several seconds...")
        out, err = dumpFromKeys()
        print()

    else:
        print("=== WARNING: Missing crypto dependancies, skipping key derivation and using backdoor key dump instead ===")
        print()
        out, err = dumpFromBackdoor(backdoorKey)
        usedBackdoorMethod = True

    # Identify where the dump files were saved
    binOutPath = ""
    jsonOutPath = ""

    for line in out.splitlines():
        line = line.decode("utf-8") #Convert from byte array to string
        if "bytes to binary file" in line:
            binOutPath = line.split("`")[-2]
            continue

        if "Saved to json file" in line:
            jsonOutPath = line.split("`")[-2]
            continue

    # Move the dump files to the user's desired output dir
    if len(binOutPath) > 0:
        if usedBackdoorMethod:
            binOutname = f"hf-mf-{uid}-dump-nokeys.bin"
        else:
            binOutname = f"hf-mf-{uid}-dump.bin"

        shutil.move(binOutPath, outDir / binOutname)
        print(f"SUCCESS! Binary dump saved to {outDir / binOutname}")
    else:
        print("ERROR: Didn't find dump file path in output:")
        print(out.decode("utf-8"))
        print(err.decode("utf-8"))
        exit(1)

    if len(jsonOutPath) > 0:
        if usedBackdoorMethod:
            jsonOutname = f"hf-mf-{uid}-dump-nokeys.json"
        else:
            jsonOutname = f"hf-mf-{uid}-dump.bin"
        shutil.move(jsonOutPath, outDir / jsonOutname)
        print(f"SUCCESS! JSON dump saved to {outDir / jsonOutname}")
    else:
        print("ERROR: Didn't find JSON file path in output:")
        print(out.decode("utf-8"))
        print(err.decode("utf-8"))
        exit(1)

    print()
    print(f"You can now run 'python ./parse.py {outDir / binOutname}' to parse the dump")

    return

def getTagData():
    """getTagData obtains basic data about a tag.
    In particular, looks for the UID and any backdoor keys.

    return:
      uid: the tag's UID
      backdoorKey: the backdoor key that can be used to read the tag data, if found
      out: the stdout from running the command
      err: the stderr from running the command
    """
    argList = ["-c", "hf mf info"]
    result = runPM3Command(argList)
    out = result.stdout

    uid = ""
    backdoorKey = ""
    for line in out.splitlines():
        line = line.decode("utf-8") #Convert from byte array to string
        if "UID:" in line:
            uid = line.split("UID:")[1].replace(" ", "")
            continue

        if "Backdoor" in line:
            backdoorKey = line.split(".")[-1].replace(" ", "")

    return uid, backdoorKey, result.stdout, result.stderr

def deriveKeys(uid):
    """deriveKeys uses a Bambu tag's UID to derive its access keys; no proxmark connection required.

    uid: a tag's UID as a hexstring (NO preceding '0x')
    return: two arrays of 16 keys (bytes objects), for A and B keys
    """

    uidB = bytes.fromhex(uid)
    master = bytes.fromhex("9a759cf2c4f7caff222cb9769b41bc96")
    keysA = HKDF(uidB, 6, master, SHA256, 16, context=b"RFID-A\0")
    keysB = HKDF(uidB, 6, master, SHA256, 16, context=b"RFID-B\0")
    return keysA, keysB

def generateDicitonaries(uid):
    """generateDicitonaries builds binary key dictionary files for any Bambu tag based on its UID
    Dictionary files are saved to the locations specified by the global variables

    uid: a tag's UID as a hexstring (NO preceding '0x')
    return: two arrays of 16 keys (bytes objects), for A and B keys
    """
    keysA, keysB = deriveKeys(uid)
    with open(DICTIONARY_FILEPATH, "w") as dictionaryFile:
        print("Derived A Keys:")
        for key in keysA:
            print(f"\t{key.hex()}")
            dictionaryFile.write(f"{key.hex()}\n")

        print("Derived B Keys:")

        for key in keysB:
            print(f"\t{key.hex()}")
            dictionaryFile.write(f"{key.hex()}\n")

    print()

    with open(DICTIONARY_BIN_FILEPATH, "wb") as dictionaryBinFile:
        for key in keysA:
            dictionaryBinFile.write(key)

        # Note: If you don't have the B keys, you must write binary 0's as placeholders for them or the file will be invalid
        for key in keysB:
            #dictionaryBinFile.write(bytes.fromhex("000000000000"))
            dictionaryBinFile.write(key)

    return keysA, keysB

def dumpFromKeys():
    """dumpFromKeys uses saved binary key dictionary files to fully dump the data from a tag
    Saves the results to JSON and binary dump files.

    return: the stdout and stderr results from running the dump command
    """
    if len(DICTIONARY_BIN_FILEPATH) == 0:
        print("Binary dictionary filepath not set, unable to dump")
        exit(1)

    argList = ["-c", f"hf mf dump -k {DICTIONARY_BIN_FILEPATH}"]
    result = runPM3Command(argList)
    return result.stdout, result.stderr

def dumpFromBackdoor(backdoorKey = ""):
    """dumpFromBackdoor uses known backdoor keys to read the data from tags.
    Only displays the data, does not create dumps.

    backdoorKey: a known-working backdoor key for the tag; if not specified, uses the known key for 1k tags
    return: the stdout and stderr results from running the dump command
    """

    print("Starting Backdoor key dump")
    print("Dumps created with this method do NOT contain any of the correct access keys needed to properly clone/emulate a tag")

    if backdoorKey == "":
        backdoorKey = "A396EFA4E24F" # It's probably this key

    argList = ["-c", f"hf mf ecfill --1k -c 4 -k {backdoorKey}"]
    result = runPM3Command(argList)
    if "[+] Fill ( ok )" not in result.stdout.decode("utf-8"):
        print("Backdoor dump failed")
        print(result.stdout.decode("utf-8"))
        print(result.stderr.decode("utf-8"))
        return

    argList = ["-c", f"hf mf esave --1k"]
    result = runPM3Command(argList)
    return result.stdout, result.stderr

# Add the quotes needed to make this a valid copy-able command
def printCmdList(cmd_list):
    """printCmdList prints formatted command lists, adding quotes where needed so the command can be copied and ran directly.
    """

    cmdList = cmd_list[:] #make a copy so we don't mess up the original; passed by pointer
    for i, c in enumerate(cmdList):
        if i != 0 and " " in c: #any args with spaces that aren't the program name should be in quotes
            cmdList[i] = f"\"{c}\""

    print(f"{' '.join(cmdList)}")

def testProxmarkConnection():
    """testProxmarkConnection tests that we can establish a working connection to a Proxmark3. Prints an error if not.
    Also identifies the correct UART_PORT if it wasn't already set so that future connection can be made faster.

    return: The exit code of the subprocess that was started to test the connection. 0 means success.
    """
    global UART_PORT

    argList = ["-c", "help"]
    print("Verifying connection to Proxmark3, this will take a few seconds...")

    #UART_PORT is not set yet
    if UART_PORT == "":
        result = runPM3Command(argList, False)
        code = result.returncode
        if code != 0:
            print("ERROR: Unable to properly connect to Proxmark3.")
            print(f"Please ensure that running `{PM3_LOCATION / PM3_COMMAND}` works and then try this script again.")
            Print(f"Exit code: {code}")
            print(result.stdout.decode("utf-8"))
            print(result.stderr.decode("utf-8"))
            return code

        # If connection worked, note the UART port that was used.
        out = result.stdout.decode("utf-8")
        portSearch = "[+] Using UART port "
        if portSearch in out:
            port = out.split(portSearch)[1].split("\n")[0]
            print(f"Succesfully connected to Proxmark3 on {port}")
            UART_PORT = port

    # UART_PORT has been set
    if UART_PORT != "":
        result = runPM3Command(argList, False)
        code = result.returncode
        if code != 0:
            print("ERROR: Unable to properly connect to Proxmark3 using the fast method, will use the slower method instead.")

    print()
    return code

def runPM3Command(argList, printCmd=True):
    """runPM3Command runs commands on a Proxmark3.
    If the correct UART port has NOT been set, uses a slower method that will find the right port
    If the correct UART port has been set, uses it directly to establish the connection faster.

    return: the result object returned by subprocess.run()
    """

    if UART_PORT == "":
        # Use the slow but reliable method
        cmdList = [str(PM3_LOCATION / PM3_COMMAND)]
    else:
        # Use the fast method, connecting immediately to the known port
        cmdList = [str(PM3_LOCATION / PM3_COMMAND_FAST), UART_PORT]

    for a in argList:
        cmdList.append(a)

    if printCmd:
        printCmdList(cmdList)

    return subprocess.run(cmdList, shell=os.name == 'nt', stdout=subprocess.PIPE, stderr=subprocess.PIPE)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Dump the contents of a Bambu filament RFID tag using a Proxmark3")

    parser.add_argument("-o", "--output-dir", help="Directory to save output files to; default is CWD", default=".")
    parser.add_argument("-b", "--backdoor", help="Read the tag data using the backdoor key instead of deriving the correct keys", action="store_true")

    args = parser.parse_args()

    main(args)
