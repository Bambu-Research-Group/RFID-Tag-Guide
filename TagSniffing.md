# Sniffing the tag data

> [!NOTE]
> This document describes the legacy method for obtaining Bambu Lab RFID tag data. See the [Readme](./README.md#proxmark3-fm11rf08s-recovery-script) for instructions on the new method.

To obtain the data from an RFID tag on a Bambu Lab spool, the user used to have to sniff the data transferred between the tag and the AMS reader to obtain the encryption keys used to decrypt the tag data. This document explains how to sniff the data.

## Proxmark3 placement for sniffing

For sniffing, you will need to place the Proxmark in between the RFID tag and the reader on the AMS. As there is not much clearance, it is recommended to temporarily remove the low frequency radio (the topmost piece) if you can, as it will not be used in this process.

Make sure that spool rotates so that the RFID tag moves away from the reader, otherwise the AMS will assume that it is reading the tag from its neighboring slot and attempt to rewind it until it cannot see the RFID tag.

> [!TIP]
> Proxmark3 Easy users: as there is not much clearance, it may be helpful to disassemble the Proxmark3 Easy and remove the top and middle layers. For this particular process, you will only need the bottom-most layer.

### Bambu Lab AMS RFID Reader Location (for X1/P1 series)

The Bambu Lab AMS RFID readers are located between slots 1&2 and slots 3&4.

![](images/filament-slots.jpg)

It is recommended to place your Proxmark3 device between the reader and the spool, but you may place it on the other side (for example, load the spool into slot 1 and place the Proxmark3 against the reader in slot 2).

### Bambu Lab AMS Lite RFID Reader Location (for A1 series)

The Bambu Lab AMS Lite RFID readers are located at the base of each spool holder.

You must place your Proxmark3 device between the reader and the spool.

## Key Derivation

As of 2024-11-19, keys can now be derived from the UID of a tag.

```python
from Cryptodome.Protocol.KDF import HKDF
from Cryptodome.Hash import SHA256

uid = bytes([0x02,0x3b,0x44,0x74]) # Replace this with the tag's UID
master = bytes([0x9a,0x75,0x9c,0xf2,0xc4,0xf7,0xca,0xff,0x22,0x2c,0xb9,0x76,0x9b,0x41,0xbc,0x96])

keys = HKDF(uid, 6, master, SHA256, 16, context=b"RFID-A\0")

print([a.hex() for a in keys])
```

## Dump RFID Contents (.bin)

1. **Run ProxMark3 Software**

   In a terminal, run `pm3` to start the Proxmark3 Software

2. **Sniff Communication**

   - Start sniffing with: `hf 14a sniff -c -r`<br>
     (hf=High Frequency, 14a=Tag Type, Sniff=command, -c and -r mean "capture on triggers instead of continuously)

   - Place your Proxmark3 between the tag and the AMS. Recommended: Use tape to hold it in place.
   - Load a strand of filament into the AMS. This is what triggers the AMS to attempt to read the RFID tag.
   - Press the button on the ProxMark to end capture after the filament has completed loading

3. **Obtain the Keys**

   1. **Automatic** (recommended)

      1. Save the trace results to a file with: `trace save -f [FILENAME]`

      2. Open a new terminal window and run the trace key extractor script in this repository with Python 3: `python3 traceKeyExtractor.py`

      3. Input the trace results filepath or drag and drop it into the terminal window

      4. After the keys are extracted, return to the Proxmark3 software

      5. Remove the spool from the AMS and hold the Proxmark3 against the RFID tag of the spool

      6. Run `hf mf fchk -f [dictionaryFilepath] --dump` to create a key file

         - The program will report the destination of the key file that it saved. Copy this filepath to your clipboard.

           - Example:

             ```
             [+] Found keys have been dumped to /Users/mitch/hf-mf-75066B1D-key.bin
             ```

   2. **Manual** (not recommended)

      1. **Create a Key Dictionary**

         - We will discover keys one at a time and save them to a dictionary file.
         - Navigate to your Proxmark3 software installation directory. This will be specific to your Operating System and Installation.
           - macOS (via Homebrew) Example: `cd $(brew --prefix proxmark3)/share/proxmark3/`
           - Linux Eample: `/usr/local/proxmark3/4.17768/share/proxmark3/`
           - Windows Example: TBD
         - Open a text editor and save a blank file called `myDictionary.dic` into the `dictionaries/` folder of your Proxmark3 software installation directory.

           (You can call this file anything you want, but for the rest of this example, we will refer to it as "myDictionary")

         - Leave this file open, we will continue to add keys to it in the next step

      2. **Extract Keys From Trace**

         - Run `trace list -t mf -f myDictionary` to view the trace that was recorded from sniffing in the previous step.

           This uses the key dictionary `myDictionary.dic` that we created in step 3.

         - Read the output and look for anything that mentions a key.
           - Three Possible Formats:
             - `key E0B50731BE27 prng WEAK` - Follow Step 5
             - `nested probable key: 50B0318A4FE7` - Follow Step 6
             - `Nested authentication detected.` - Follow Step 7
           - Each of these 3 entries can provide us with a valid key. Follow step 5, 6, or 7 depending on which type of key you encounter.

      3. **First Key - Plain Text**
         - Example: `key E0B50731BE27 prng WEAK`
         - This is the first key that was discovered by sniffing AMS traffic.
         - Copy/paste this key into the `myDictionary.dic` file that you created in step 3, then save the file.
      4. **Nested Probable Key**
         - Example: `nested probable key: 50B0318A4FE7`
         - Copy/paste this key into the `myDictionary.dic` file that you created in step 3, then save the file.
      5. **Nested Authentication Key**
         - Example:
           ```
           Nested authentication detected.
           tools/mf_nonce_brute/mf_nonce_brute 75066b1d 4db2f2ac 0101 70fcdd3d 328eb1e6 1101 28b75cfd 0010 5196401C
           ```
         - Open a second terminal window, ensuring you are still in the Proxmark3 installation directory.
         - CD into the tools folder `cd tools/`
         - Copy the command from ProxMark starting at `mf_nonce_brute`, including all the arguments (random letters/numbers) after it, and run the program from the `tools/` directory.
           - Example (macOS/Linux): `./mf_nonce_brute 75066b1d 4db2f2ac 0101 70fcdd3d 328eb1e6 1101 28b75cfd 0010 5196401C`
           - Example (Windows): `mf_nonce_brute.exe 75066b1d 4db2f2ac 0101 70fcdd3d 328eb1e6 1101 28b75cfd 0010 5196401C`
         - The program will discover a key. Copy/paste this key into your `myDictionary.dic` file, and SAVE IT.
           - Example Output:
             ```
             Valid Key found [ 202efd3dcdfd ]
             ```
      6. **Check Keys (Optional)**

         - If you want to check how many valid keys you've discovered, you can do this test
         - This is optional, and you can choose to wait until you have discovered all of the keys
         - **WARNING**: Performing a key check will erase the trace that you recorded during step 2, and will require you to re-sniff data (repeat step 2)

           - If you want to save your trace to avoid re-sniffing, use `trace save -f <trace-name>` and `trace load -f <trace-name>`

         - Run `hf mf fchk --1k -f myDictionary` to test your keys
           - Example Output (showing 11/16 keys discovered):
             ```
             [+] found keys:

             [+] -----+-----+--------------+---+--------------+----
             [+]  Sec | Blk | key A        |res| key B        |res
             [+] -----+-----+--------------+---+--------------+----
             [+]  000 | 003 | E0B50731BE27 | 1 | ------------ | 0
             [+]  001 | 007 | 63654DB94D97 | 1 | ------------ | 0
             [+]  002 | 011 | 387C06EFFDC8 | 1 | ------------ | 0
             [+]  003 | 015 | 38963E577E43 | 1 | ------------ | 0
             [+]  004 | 019 | 8A3EA2564692 | 1 | ------------ | 0
             [+]  005 | 023 | 935E0F11857A | 1 | ------------ | 0
             [+]  006 | 027 | EBC8F7D23A06 | 1 | ------------ | 0
             [+]  007 | 031 | DD6128F13D4C | 1 | ------------ | 0
             [+]  008 | 035 | ------------ | 0 | ------------ | 0
             [+]  009 | 039 | 4E470B09521F | 1 | ------------ | 0
             [+]  010 | 043 | 50EB8811A69C | 1 | ------------ | 0
             [+]  011 | 047 | 4BDD25091824 | 1 | ------------ | 0
             [+]  012 | 051 | ------------ | 0 | ------------ | 0
             [+]  013 | 055 | ------------ | 0 | ------------ | 0
             [+]  014 | 059 | ------------ | 0 | ------------ | 0
             [+]  015 | 063 | ------------ | 0 | ------------ | 0
             [+] -----+-----+--------------+---+--------------+----
             [+] ( 0:Failed / 1:Success )
             ```

      7. **Find Remaining Keys**

         - Repeat step 4 until all 16 keys are discovered
         - Your dictionary may be larger than 16 entries if you accidentally copied a duplicate key or an invalid key. These invalid entries are fine, and you can ignore them
         - **Recommended**: When you think you have discovered all 16 keys, perform step 8 to verify that your keys are correct.

      8. **Convert Dictionary to Key File**

         - Remove the spool from the AMS and hold the Proxmark3 against the RFID tag of the spool
         - Run `hf mf fchk --1k -f myDictionary --dump` to create a key file
         - The program will report the destination of the key file that it saved. Copy this filepath to your clipboard
           - Example:
             ```
             [+] Found keys have been dumped to /current/directory/hf-mf-75066B1D-key.bin
             ```

4. **Dump RFID Contents**

   - Run `hf mf dump -k [path-to-keyfile]` while the Proxmark3 is on the spool's RFID tag to dump the contents of the tag using the 16 keys we discovered
   - There should be no errors
   - The output should tell you where your `.bin` file is saved
     - Example:
       ```
       [+] saved 1024 bytes to binary file /current/directory/hf-mf-75066B1D-dump.bin
       ```
