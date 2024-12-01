# Bambu Lab RFID Tag Guide

This guide gives you a basic overview how you can decrypt and read your tags. Since we don't know how Bambu Lab will react on this guide and the general reverse engineering of the tags: **Please don't share you tag's UID and the related keys for now.**

We are currently working on a way to submit the tag data in a secure way so analysis on the data could be done.

[![Link to Discord](https://img.shields.io/badge/Discord-join_now-blue?style=flat-square&logo=discord&logoColor=white&label=Discord&color=blue)](https://discord.gg/zVfCVubwr7)

# Table of contents

<!--ts-->

- [Project Summary](#project-summary)
  - [FAQs](#faqs)
  - [How do RFID tags work?](#how-do-rfid-tags-work)
  - [How to contribute](#how-to-contribute)
- [Todos/Timeline/Next steps](#todostimelinenext-steps)
- [Required Equipment](#required-equipment)
  - [Proxmark3 compatible readers](#proxmark3-compatible-readers)
    - [Proxmark3 Easy](#proxmark3-easy)
- [Hacking a Bambu Lab Tag and readout of its data](#hacking-a-bambu-lab-tag-and-readout-of-its-data)
  - [Proxmark3 fm11rf08s recovery script](#proxmark3-fm11rf08s-recovery-script)
  - [Bambu Lab AMS RFID reader location](#bambu-lab-ams-rfid-reader-location)
  - [Bambu Lab AMS Lite RFID reader location (legacy)](#bambu-lab-ams-lite-rfid-reader-location-legacy)
  - [Proxmark3 placement for sniffing (legacy)](#proxmark3-placement-for-sniffing-legacy)
  - [Key Derivation](#key-derivation)
  - [Dump RFID Contents (.bin) (legacy)](#dump-rfid-contents-bin-legacy)
- [Tag Documentation](#tag-documentation)
  - [Block Overview](#block-overview)
  - [MIFARE Encryption Keys](#mifare-encryption-keys)
  - [Block 0](#block-0)
  - [Block 1](#block-1)
  - [Block 2](#block-2)
  - [Block 4](#block-4)
  - [Block 5](#block-5)
  - [Block 6](#block-6)
  - [Block 8](#block-8)
  - [Block 9](#block-9)
  - [Block 10](#block-10)
  - [Block 12](#block-12)
  - [Block 13](#block-13)
  - [Block 14](#block-14)
  - [Block 16](#block-16)
  - [Block 17](#block-17)
- [Compatible RFID tags - By generation](#compatible-rfid-tags----by-generation)
- [Reverse engineering RFID Board](#reverse-engineering-rfid-board)
<!--te-->

## Project Summary

This is a research group dedicated to documenting the data structures used by Bambu Lab 3D printers to identify filament data.

### FAQs

- **Can I clone tags?**
  - Yes, you can read and clone tags using a tool such as a Proxmark3
- **Can I create custom tags?**
  - No, tags are digitally signed. Even if you modify the contents, the printer will reject any tags without a valid RSA signature
  - An [Open Source RFID Tag](OpenSourceRfid.md) has been proposed to allow anyone to create / modify their own tags. This must be adopted by printer manufacturers, or you can mod your own printer for support
- **What are the next steps for this project?**
  - Decyphering the rest of the unknwn tag content
  - Custom AMS firmware that allows custom tags to be read while ignoring the signature
  - See [Todos/Timeline/Next steps](#todostimelinenext-steps) for more info

### How do RFID tags work?

Here's a high-level summary of how everything works:

- Bambu Lab printers use MiFare 13.56MHZ RFID tags
  - These tags contain a unique ID that is not encrypted (called the UID)
  - In most cases UID is fixed (not-changable). Some "hackable" rfid tags allow you to set the UID to anything you want
- Blocks (Encrypted)
  - MiFare tags also contain "Blocks" of data. Each block contains info about the spool, such as Material, Color, Manufacturing Date, etc. See [Tag stucture](#tag-stucture) section for details
  - The blocks are encrypted, meaning that you need to have a KEY to decipher them
  - Each block is encrypted with a different key
- Encryption Keys
  - Keys are unique to each RFID tag. Even if you discover the key for one tag, that doesn't mean you can use that same key to unlock a different tag.
  - As of 11/19/24, keys can be derived from the UID. After reading the UID from the tag, the KDF (key derivation function) can be used to derive the 16 keys.
  - (Outdated, sniffing is no longer required now that the KDF is known) Keys can be sniffed by using a device (such as a ProxMark 3) to listen in on the communication between the AMS and the rfid tag.
  - Once the keys have been sniffed, they can be saved and used to read the contents of the tag directly (without an AMS). (Reminder, the saved keys will ONLY work for the tag they were sniffed from)
- RSA Signature
  - One of the blocks contains a 2048-bit RSA Signature
  - RSA signatures are a way to digitally sign / certify authenticity of content, and they are effectively un-breakable (this is how things like cryptocurrency remain secure)
  - RSA signatures encompass all of the data of the RFID tag. Changing a single byte somewhere else in the tag would require a completely different signature to be considered genuine
  - Bambu printers check the content of the tag and then check if the signature is valid. If the signature is invalid, it rejects the tag
- Cloning Tags
  - Even though there is a signature, a tag can be cloned
  - To clone a tag, it must have the same UID, identical content from the data blocks, and the identical RSA signature
  - Changing even one byte will cause the signature to be invalid, and the tag will be rejected
- Custom Tags
  - This is very unlikely to happen, mostly due to the RSA signature. Only Bambu has their "Private Key" which is used to digitally sign these tags.
  - To create a custom key, you need to know the following info:
    - RSA Signature Private Key. You'd have to get this from bambu, good luck
  - Since Bambu Lab will likely not remove the signature requirement, you would need custom AMS firmware to read tags and ignore the signature

### How to contribute

If you have a Proxmark3 (or other RFID debugging tool), you can sniff and decrypt the contents of your tags and submit them for review.
The more data we have, the easier it is to compare differences to learn what each byte represents. A lot of the contents have been deciphered (see [Tag stucture](#tag-stucture)), but there is still more unknown data still left.

## Todos/Timeline/Next steps

- [ ] Tool for automatic trace analysis
- [ ] Web service for tag submisson with automatic anonymized data publishing to github
- [ ] Tag content analysis
- [ ] Generate keys based on an arbitrary UID

## Required Equipment

- Bambu Lab 3D Printer with AMS or AMS Lite
- Bambu Lab Filament spool **or** the related tags
- A Proxmark3-compatible RFID reader
- The [proxmark3 (Iceman fork) software](https://github.com/RfidResearchGroup/proxmark3)
  - Make sure you are using the Iceman fork as the original version of the software is unmaintained; all instructions are written for the Iceman fork and will not work on the original version

### Proxmark3 compatible readers

#### Proxmark3 Easy

![](images/Proxmark3_easy.png)

A Proxmark3 Easy is sufficient for all the tasks that need to be done. You can buy a clone from Alixepress, Amazon or Dangerous Things.

## Hacking a Bambu Lab Tag and readout of its data

We document here the most simple approach to get all required A-Keys and the data of the tag.
The easiest way is to sniff the data.

Update November 2024: In 2024 a new backdoor was found which requires no sniffing. Details can be found [here](https://eprint.iacr.org/2024/1275.pdf). Overall this makes it much easier get the keys and the tags data.

### Proxmark3 fm11rf08s recovery script

This script is included in proxmarx3 since its release "Backdoor" and later.

Place your reader on the tag, start proxmark3 and run the following command.

`script run fm11rf08s_recovery`

This requires some time but once done you receive a binary key file and a dump.

To visualize the data on the tag you can run now:

`script run fm11rf08_full -b`

### Bambu Lab AMS RFID reader location

The Bambu Lab AMS RFID readers are located between slots 1&2 and slots 3&4.

![](images/filament-slots.jpg)

### Bambu Lab AMS Lite RFID reader location (legacy)

The Bambu Lab AMS Lite RFID readers are located at the base of each spool holder.

For sniffing, you will need to place the Proxmark in between the RFID tag and the reader on the AMS. As there is not much clearance, it is recommended to temporarily remove the low frequency radio (the topmost piece) if you can, as it will not be used in this process.

### Proxmark3 placement for sniffing (legacy)

For sniffing, you will need to place the Proxmark3 against the reader. On the AMS lite, you must place it in between the reader and the spool. On the AMS, it is recommended to place it between the reader and the spool, but you may place it on the other side (for example, load the spool into slot 1 and place the Proxmark3 against the reader in slot 2).

> [!TIP]
> As there is not much clearance, it may be helpful to disassemble the Proxmark3 Easy and remove the top and middle layers. For this particular process, you will only need the bottom-most layer.

If you place the Proxmark in between the AMS reader and the spool, make sure that spool rotates so that the RFID tag moves away from the reader, otherwise the AMS will assume that it is reading the tag from its neighboring slot and attempt to rewind it until it cannot see the RFID tag.

### Key Derivation

As of 2024-11-19, keys can now be derived from the UID of a tag.

```python
from Cryptodome.Protocol.KDF import HKDF
from Cryptodome.Hash import SHA256

uid = bytes([0x02,0x3b,0x44,0x74])
master = bytes([0x9a,0x75,0x9c,0xf2,0xc4,0xf7,0xca,0xff,0x22,0x2c,0xb9,0x76,0x9b,0x41,0xbc,0x96])

keys = HKDF(uid, 6, master, SHA256, 16, context=b"RFID-A\0")

print([a.hex() for a in keys])
```

### Dump RFID Contents (.bin) (legacy)

1. **Run ProxMark3 Software**

   In a terminal, run `pm3` to start the Proxmark3 Software

2. **Sniff Communication**

   - Start sniffing with: `hf 14a sniff -c -r`<br>
     (hf=High Frequency, 14a=Tag Type, Sniff=command, -c and -r mean "capture on triggers instead of continuously)

   - Place your Proxmark3 between the tag and the AMS. Recommended: Use tape to hold it in place.
   - Load a strand of filament into the AMS. This is what triggers the AMS to attempt to read the RFID tag.
   - Press the button on the ProxMark to end capture after the filament has completed loading

3. **Extract the Keys**

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
           - macOS (Intel) Example: `/usr/local/Cellar/proxmark3/4.17768/share/proxmark3/`
           - macOS (ARM) Eample: `/opt/homebrew/Cellar/proxmark3/4.17768/share/proxmark3/`
           - Windows Example: TBD
           - Linux Example: TBD
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
         - Open a second terminal window, and change directories into your Proxmark3 software installation directory. This is specific to your OS and PM3 installation.
           - macOS/Linux: `cd $(brew --prefix proxmark3)/share/proxmark3/`
           - Windows: TBD
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
             [+] Found keys have been dumped to /Users/mitch/hf-mf-75066B1D-key.bin
             ```

4. **Dump RFID Contents**

   - Run `hf mf dump -k [path-to-keyfile]` while the Proxmark3 is on the spool's RFID tag to dump the contents of the tag using the 16 keys we discovered
   - There should be no errors
   - The output should tell you where your `.bin` file is saved
     - Example:
       ```
       [+] saved 1024 bytes to binary file /Users/mitch/hf-mf-75066B1D-dump.bin
       ```

## Tag Documentation

This contains documentation for the known and unknown data that is contained in each block on the RFID tag.

### Block Overview

Summary of what kind of data is stored in each block. Detailed info for each block is documented below.
| sec | blk | Data |
|-----|-----|----------------------------------------------------------------------------------------|
| 0 | 0 | [Block 0](#block-0) UID and Tag Manufacturer Data |
| 0 | 1 | [Block 1](#block-1) Tray Info Index |
| 0 | 2 | [Block 2](#block-2) Filament Type |
| 0 | 3 | [Block 3](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 1 | 0 | [Block 4](#block-4) Detailed Filament Type |
| 1 | 1 | [Block 5](#block-5) Spool Weight, Color Code, Filament Diameter |
| 1 | 2 | [Block 6](#block-6) Temperatures and Drying Info |
| 1 | 3 | [Block 7](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 2 | 0 | [Block 8](#block-8) X Cam Info, Nozzle Diameter |
| 2 | 1 | [Block 9](#block-9) Tray UID |
| 2 | 2 | [Block 10](#block-10) Spool Width |
| 2 | 3 | [Block 11](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 3 | 0 | [Block 12](#block-12) Production Date/Time |
| 3 | 1 | [Block 13](#block-13) Short Production Date/Time |
| 3 | 2 | [Block 14](#block-14) Filament Length |
| 3 | 3 | [Block 15](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 4 | 0 | [Block 16](#block-16) Extra Color Info |
| 4 | 1 | [Block 17](#block-17) **Unknown** |
| 4 | 2 | **Empty** |
| 4 | 3 | [Block 19](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 5 | 0 | **Empty** |
| 5 | 1 | **Empty** |
| 5 | 2 | **Empty** |
| 5 | 3 | [Block 23](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 6 | 0 | **Empty** |
| 6 | 1 | **Empty** |
| 6 | 2 | **Empty** |
| 6 | 3 | [Block 27](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 7 | 0 | **Empty** |
| 7 | 1 | **Empty** |
| 7 | 2 | **Empty** |
| 7 | 3 | [Block 31](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 8 | 0 | **Empty** |
| 8 | 1 | **Empty** |
| 8 | 2 | **Empty** |
| 8 | 3 | [Block 35](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 9 | 0 | **Empty** |
| 9 | 1 | **Empty** |
| 9 | 2 | **Empty** |
| 9 | 3 | [Block 39](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 10-15 | \* | **RSA-2048 Signature** |

The first part of the filament serial number seems to be the Tag UID.

> [!NOTE]
> All numbers are encoded as Little Endian (LE).

### MIFARE Encryption Keys

Every 4th block (eg Sector X, Block 3) contains encryption keys that are part of the MIFARE RFID standard.
This has nothing to do with Bambu Lab's memory format.
All Bambu Lab tags use the same Permission Bits (Access Control)

Example Data:
`AA AA AA AA AA AA PP PP PP PP BB BB BB BB BB BB`

| position | length | type    | Description                                                                    |
| -------- | ------ | ------- | ------------------------------------------------------------------------------ |
| 0 (AA)   | 6      | RAW Bin | A-Key                                                                          |
| 6 (PP)   | 4      | RAW Bin | Permission Bits (Access Control)<br>ALWAYS `87 87  87 69` (hex) for Bambu Tags |
| 10 (BB)  | 6      | RAW Bin | B-Key (always `00 00 00 00 00 00` for Bambu tags)                              |

### Block 0

Note: Block 0 is Read-only. The contents are set by the tag manufacturer.

Example Data:
`AA AA AA AA BB BB BB BB BB BB BB BB BB BB BB BB`

| position | length | type    | Description           |
| -------- | ------ | ------- | --------------------- |
| 0 (AA)   | 4      | string  | Tag UID               |
| 4 (BB)   | 12     | RAW Bin | Tag Manufacturer Data |

### Block 1

Example Data:
`AA AA AA AA AA AA AA AA BB BB BB BB BB BB BB BB`

| position | length | type   | Description                                   |
| -------- | ------ | ------ | --------------------------------------------- |
| 0 (AA)   | 8      | string | Tray Info Index - Material Variant Identifier |
| 8 (BB)   | 16     | string | Tray Info Index - Unique Material Identifier  |

### Block 2

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| position | length | type   | Description   |
| -------- | ------ | ------ | ------------- |
| 0 (AA)   | 16     | string | Filament Type |

### Block 4

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| position | length | type   | description            |
| -------- | ------ | ------ | ---------------------- |
| 0 (AA)   | 16     | string | Detailed Filament Type |

Known Values:

- PLA Basic
- PLA Matte
- PLA Silk
- PLA Galaxy
- PLA Sparkle
- Support for PLA (prev. Support W)
- PLA-CF (prev. PLA Tough)
- PETG Basic

### Block 5

Example Data:
`AA AA AA AA BB BB __ __ CC CC CC CC __ __ __ __`

| position | length | type        | Description                                |
| -------- | ------ | ----------- | ------------------------------------------ |
| 0 (AA)   | 4      | RGBA        | Color in hex RGBA                          |
| 4 (BB)   | 2      | uint16 (LE) | Spool Weight in grams (`E8 03` --> 1000 g) |
| 8 (CC)   | 8      | float (LE)  | Filament Diameter in milimeters            |

### Block 6

Example Data:
`AA AA BB BB CC CC DD DD EE EE FF FF __ __ __ __`

| position | length | type        | Description                             |
| -------- | ------ | ----------- | --------------------------------------- |
| 0 (AA)   | 2      | uint16 (LE) | Drying Temperature in °C                |
| 2 (BB)   | 2      | uint16 (LE) | Drying time in hours                    |
| 4 (CC)   | 2      | uint16 (LE) | Bed Temerature Type **(types unknown)** |
| 6 (DD)   | 2      | uint16 (LE) | Bed Temperature in °C                   |
| 8 (EE)   | 2      | uint16 (LE) | Max Temperature for Hotend in °C        |
| 10 (FF)  | 2      | uint16 (LE) | Min Temperature for Hotend in °C        |

### Block 8

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA BB BB BB BB`

| position | length | type       | description             |
| -------- | ------ | ---------- | ----------------------- |
| 0 (AA)   | 12     | RAW Bin    | X Cam info              |
| 12 (BB)  | 4      | float (LE) | **Nozzle Diameter...?** |

### Block 9

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| position | length | type   | Description |
| -------- | ------ | ------ | ----------- |
| 0 (AA)   | 16     | string | Tray UID    |

### Block 10

Example Data:
`__ __ __ __ AA AA __ __ __ __ __ __ __ __ __ __`

| position | length | type        | Description                                         |
| -------- | ------ | ----------- | --------------------------------------------------- |
| 4 (AA)   | 2      | uint16 (LE) | Spool Width in µm (`E1 19` --> 6625µm --> 66.25mm ) |

### Block 12

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| position | length | type   | Description                                                                |
| -------- | ------ | ------ | -------------------------------------------------------------------------- |
| 0 (AA)   | 16     | string | Production Date and Time in ASCII (`<year>_<month>_<day>_<hour>_<minute>`) |

### Block 13

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| position | length | type   | Description                        |
| -------- | ------ | ------ | ---------------------------------- |
| 0 (AA)   | 16     | string | **Short Production Date/Time...?** |

### Block 14

Example Data:
`__ __ __ __ AA AA __ __ __ __ __ __ __ __ __ __`

| position | length | type        | Description                       |
| -------- | ------ | ----------- | --------------------------------- |
| 4 (AA)   | 2      | uint16 (LE) | **Filament length in meters...?** |

### Block 16

Example Data:
`AA AA BB BB CC CC CC CC __ __ __ __ __ __ __ __`

| position | length | type        | Description                        |
| -------- | ------ | ----------- | ---------------------------------- |
| 0 (AA)   | 2      | uint16 (LE) | Format Identifier                  |
| 2 (BB)   | 2      | uint16 (LE) | Color Count                        |
| 4 (CC)   | 4      | RGBA        | Second color in _reverse_ hex ABGR |

Known Format Identifiers:

- 00 00 = Empty
- 02 00 = Color Info

### Block 17

Example Data:
`AA AA __ __ __ __ __ __ __ __ __ __ __ __ __ __`

| position | length | type        | Description |
| -------- | ------ | ----------- | ----------- |
| 0 (AA)   | 2      | **Unknown** | **Unknown** |

## Compatible RFID tags - By generation

There are tags known as "Magic Tags" which allow functionality that's not part of the classic MIFARE spec.
One example is that most Magic Tags allow the UID to be changed, which is normally read-only on MIFARE tags.
Magic tags are often refered to by their "generation", eg "Magic Gen 1". Each newer generation increases the functionality, but tends to also be more expensive)

Gen 1 --> **Not compatible**(due to AMS checking if tag is unlockable with command 0x40)

Gen 2 --> **Works**

Gen 2 OTW --> **Not tested**

Gen 3 --> **Not tested**

Gen 4 --> **Not tested**(The best option but pricey and hard to source in small chip formfactor)

FUID --> **Works** "Fused UID" aka "write-once UID". Once a UID is written, it cannot be changed

## Reverse engineering RFID Board

For ease of debugging and lowering the cost of failures the RFID board is reverse engineered. You can find complete production ready gerber files and bill of materials in rfid-board folder

As a nice to benefit to have is that you can manufacture boards in different colors.
![](rfid-board/Photo_PCB_BBL-RFID.jpg)
