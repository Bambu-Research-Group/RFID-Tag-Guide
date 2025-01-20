#!/usr/bin/env python3

import subprocess
import os
import re
import sys
from pathlib import Path
import argparse
import shutil
from traceKeyExtractor import run_command, testCommands, get_proxmark3_location

# Attempt to load crypto dependancies
try:
    from Cryptodome.Protocol.KDF import HKDF
    from Cryptodome.Hash import SHA256
    CRYPTO_INSTALLED=True
except Exception as e:
    print("=== WARNING: Please run 'pip install pycryptodomex' first to install required dependancies for full functionality ===")
    print(e)
    print()
    CRYPTO_INSTALLED=False

if not sys.version_info >= (3, 6):
   print("Python 3.6 or higher is required!")
   exit(-1)

#Global variables
#Default name of the dictionary file we create
#dictionaryFilename = "keys.dic"  #Arbitrary filename for storing dictionary file
DICTIONARY_FILEPATH = ""                     #Calculated. Absolute path to dictionary file
#dictionaryFile = ""                         #File object for writing keys
DICTIONARY_BIN_FILEPATH = ""                     #Calculated. Absolute path to dictionary file

PM3_LOCATION = None                          #Calculated. The location of Proxmark3
PM3_COMMAND = "bin/pm3"                      # The command that works to start proxmark3
BACKDOOR_SCRIPT = "share/proxmark3/pyscripts/mf_backdoor_dump.py" 

#trace = "";                 #Prompted during runtime. Trace filename that the user provides

def main(args):
    global PM3_LOCATION,DICTIONARY_FILEPATH,DICTIONARY_BIN_FILEPATH

    print("--------------------------------------------------------")
    print("RFID QuickDump v1.0")
    print("--------------------------------------------------------")
    print("This will dump the data from a Bambu filament tag")
    print("Requires a Proxmark3 to be plugged in")
    print("MAKE SURE YOU DO NOT HAVE ANY OTHER TERMINALS CONNECTED TO THE PROXMARK3")
    print("--------------------------------------------------------")
    print("")
    
    
    PM3_LOCATION = get_proxmark3_location()
    print()
    print("Reading basic card data...")
    uid, backdoor, stdout, stderr = getTagData()
    if uid == "":
        print("UID not found in output, probably error reading card. Exiting.")
        print(stdout.decode("utf-8"))
        print(stderr.decode("utf-8"))
        exit(1)
        
    print(f"Tag UID: {uid}")
    print(f"Tag backdoor key: {backdoor}")
    print()
    
    outDir = Path(args.output_dir).resolve()
    dictionaryFilename = f"{uid}_keys.dic"
    DICTIONARY_FILEPATH = str(outDir / dictionaryFilename)
    dictionaryBinFilename = dictionaryFilename + ".bin"
    DICTIONARY_BIN_FILEPATH = str(outDir / dictionaryBinFilename)
    #print(DICTIONARY_FILEPATH)
    #print(DICTIONARY_BIN_FILEPATH)
    
    if args.backdoor:
        dumpFromBackdoor()
        return
    
    if CRYPTO_INSTALLED:
        print("Deriving tag keys...")
        keysA, keysB = generateDicitonaries(args, uid)
        if len(keysA) != 16:
            pass
    else:
        print("=== WARNING: Missing dependancies, skipping key derivation and using backdoor key dump instead ===")
        dumpFromBackdoor()
        return
    
    print("Dumping tag data using derived keys...")
    out, err = dumpFromKeys()
    print()
    
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
        binOutname = f"{uid}_dump.bin"
        shutil.move(binOutPath, outDir / binOutname)
        print(f"SUCCESS! Binary dump saved to {outDir / binOutname}")
    else:
        print("ERROR: Didn't find dump file path in output:")
        print(out.decode("utf-8"))
        print(err.decode("utf-8"))
        exit(1)
    
    if len(jsonOutPath) > 0:
        jsonOutname = f"{uid}_dump.json"
        shutil.move(jsonOutPath, outDir / jsonOutname)
        print(f"SUCCESS! JSON dump saved to {outDir / jsonOutname}")
    else:
        print("ERROR: Didn't find JSON file path in output:")
        print(out.decode("utf-8"))
        print(err.decode("utf-8"))
        exit(1)
    
    print()
    print(f"Run 'python ./parse.py {outDir / binOutname}' to parse the dump")
        
    return

def getTagData():
    cmd_list = [str(PM3_LOCATION / PM3_COMMAND), "-c", "hf mf info"]
    printCmdList(cmd_list)
    result = subprocess.run(cmd_list, shell=os.name == 'nt', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = result.stdout
    
    uid = ""
    backdoor = ""
    for line in out.splitlines():
        line = line.decode("utf-8") #Convert from byte array to string
        if "UID:" in line:
            uid = line.split("UID:")[1].replace(" ", "")
            continue
        
        if "Backdoor" in line:
            backdoor = line.split(".")[-1].replace(" ", "")
        
    return uid, backdoor, result.stdout, result.stderr

def deriveKeys(uid):
    """deriveKeys uses a tag's UID to derive its access keys. 

    uid: a tag's UID as a hexstring (NO preceding '0x')
    return: an array of 16 keys (bytes objects)
    """
    
    uidB = bytes.fromhex(uid)
    master = bytes.fromhex("9a759cf2c4f7caff222cb9769b41bc96")
    keysA = HKDF(uidB, 6, master, SHA256, 16, context=b"RFID-A\0")
    keysB = HKDF(uidB, 6, master, SHA256, 16, context=b"RFID-B\0")
    return keysA, keysB

def generateDicitonaries(args, uid):
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
    return keysA, keysB
    
    with open(DICTIONARY_BIN_FILEPATH, "wb") as dictionaryBinFile:
        for key in keys:
            dictionaryBinFile.write(key)
        
        # Note: If you don't have the B keys, you must write binary 0's as placeholders for them or the file will be invalid
        for key in keysB:
            dictionaryBinFile.write(key)

def dumpFromKeys():
    if len(DICTIONARY_BIN_FILEPATH) == 0:
        print("Binary dictionary filepath not set, unable to dump")
        exit(1)
    
    cmd_list = [str(PM3_LOCATION / PM3_COMMAND), "-c", f"hf mf dump -k {DICTIONARY_BIN_FILEPATH}"]
    printCmdList(cmd_list)
    result = subprocess.run(cmd_list, shell=os.name == 'nt',stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout, result.stderr

def dumpFromBackdoor():
    print("Starting Backdoor key dump")
    print("Proxmark firmware doesn't currently support exporting this to a dump file, only displaying the data")
    
    cmd_list = [str(PM3_LOCATION / PM3_COMMAND), "--py", str(PM3_LOCATION / BACKDOOR_SCRIPT)]
    printCmdList(cmd_list)
    result = subprocess.run(cmd_list, shell=os.name == 'nt', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = result.stdout.decode("utf-8")
    
    print(out)
    if "downloading emulator memory" not in out:
        print("Possible error:")
        print(result.stderr.decode("utf-8"))

# Add the quotes needed to make this a valid copy-able command
def printCmdList(cmd_list):
    cmdList = cmd_list[:] #make a copy so we don't mess up the original; passed by pointer
    foundC = False
    for i, c in enumerate(cmdList):
        if c == "-c":
            foundC = True
            continue
        
        if foundC and " " in c:
            cmdList[i] = f"\"{c}\""
    
    print(f"{' '.join(cmdList)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Dump the contents of a Bambu filament RFID tag using a Proxmark3")

    #parser.add_argument("-q", "--quiet", help="Only print error messages")
    parser.add_argument("-o", "--output-dir", help="Directory to save output files to; default is CWD", default=".")
    parser.add_argument("-b", "--backdoor", help="Read the tag data using the backdoor key instead of deriving the correct keys", action="store_true")

    # Parse arguments
    args = parser.parse_args()
    
    main(args)
