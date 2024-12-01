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
- [ ] Web service for tag submisson with automatic anonymized data publishing to GitHub
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

We document here the most simple approach to get all required A-Keys and the data of the tag. The easiest way is to use the `fm11rf08s` script included in the Proxmark3 software.

### Proxmark3 fm11rf08s recovery script

In 2024, a new backdoor[^rfid-backdoor] was found that makes it much easier to obtain the data from the RFID tags. A script is included in the proxmark3 software since v4.18994 (nicknamed "Backdoor"), which allows us to utilize this backdoor. Before this script was implemented, the tag had to be sniffed by placing the spool in the AMS and sniffing the packets transferred between the tag and the AMS.

Place your reader on the tag, start proxmark3 (run `pm3`) and run the following command:

`script run fm11rf08s_recovery`

This script takes a bit of time, but once it is complete, you will receive a binary key file and a dump.

To visualize the data on the tag, run the following:

`script run fm11rf08_full -b`

### Sniffing the tag data (legacy method)

To read how to obtain the tag data using the legacy sniffing method, see the [corresponding document](./TagSniffing.md).

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

For ease of debugging and lowering the cost of failures, the RFID board is reverse-engineered. You can find complete production-ready gerber files and a bill of materials in [rfid-board](./rfid-board) folder.

[^rfid-backdoor]: https://eprint.iacr.org/2024/1275.pdf
