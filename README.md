# Bambulab RFID Tag Guide

This guide gives you a basic overview how you can decrypt and read your tags. Since we don't know how Bambulab will react on this guide and the general reverse engineering of the tags: **Please don't share you tag's UID and the related keys for now.**

We are currently working on a way to submit the tag data in a secure way so analysis on the data could be done.

#  Table of contents
<!--ts-->
   * [Project Summary](#project-summary)
      * [FAQs](#faqs)
      * [How do RFID tags work?](#how-do-rfid-tags-work)
      * [How to contribute](#how-to-contribute)
   * [Todos/Timeline/Next steps](#todostimelinenext-steps)
   * [Required Equipment](#required-equipment)
      * [Proxmark3 compatible readers](#proxmark3-compatible-readers)
         * [Proxmark3 easy](#proxmark3-easy)
   * [Hacking a Bambulab Tag and readout of its data](#hacking-a-bambulab-tag-and-readout-of-its-data)
      * [Bambulab AMS RFID readers and sniffing](#bambulab-ams-rfid-readers-and-sniffing)
      * [Sniffing the data](#sniffing-the-data)
      * [Getting the other keys by analyzing the log file](#getting-the-other-keys-by-analyzing-the-log-file)
   * [Data Readout](#data-readout)
   * [Tag Documentation](#tag-documentation)
      * [Block Overview](#block-overview)
      * [Block 1](#block-1)
      * [Block 2](#block-2)
      * [Block 4](#block-4)
      * [Block 5](#block-5)
      * [Block 6](#block-6)
      * [Block 8](#block-8)
      * [Block 9](#block-9)
      * [Block 12](#block-12)
   * [Compatible RFID tags -  By generation](#compatible-rfid-tags----by-generation)
<!--te-->

## Project Summary
This is a research group dedicated to documenting the data structures used by Bambulab 3D printers to identify filament data.

### FAQs
 * **Can I clone tags?**
   * Yes, you can read and clone tags using a tool such as a ProxMark3
 * **Can I create custom tags?**
   * No, tags are digitally signed. Even if you modify the contents, the printer will reject any tags without a valid RSA signature
   * An [Open Source RFID Tag](OpenSourceRfid.md) has been proposed to allow anyone to create / modify their own tags. This must be adopted by printer manufacturers, or you can mod your own printer for support
 * **What are the next steps for this project?**
   * Decyphering the rest of the unknwn tag content
   * Custom AMS firmware that allows custom tags to be read while ignoring the signature
   * See [Todos/Timeline/Next steps](#todostimelinenext-steps) for more info

### How do RFID tags work?
Here's a high-level summary of how everything works:
* BambuLab printers use MiFare 13.56MHZ RFID tags
   * These tags contain a unique ID that is not encrypted (called the UID)
   * In most cases UID is fixed (not-changable).  Some "hackable" rfid tags allow you to set the UID to anything you want
* Blocks (Encrypted)
   * MiFare tags also contain "Blocks" of data. Each block contains info about the spool, such as Material, Color, Manufacturing Date, etc. See [Tag stucture](#tag-stucture) section for details
   * The blocks are encrypted, meaning that you need to have a KEY to decipher them
   * Each block is encrypted with a different key
* Encryption Keys
   * Keys are unique to each RFID tag. Even if you discover the key for one tag, that doesn't mean you can use that same key to unlock a different tag.
   * Keys are likely derived from the UID. The UID goes through an algorithm (known only by Bambu) to reveal a set of keys for each block
   * Keys can be sniffed by using a device (such as a ProxMark 3) to listen in on the communication between the AMS and the rfid tag.
   * Once the keys have been sniffed, they can be saved and used to read the contents of the tag directly (without an AMS). (Reminder, the saved keys will ONLY work for the tag they were sniffed from)
* RSA Signature
   * One of the blocks contains a 2048-bit RSA Signature
   * RSA signatures are a way to digitally sign / certify authenticity of content, and they are effectively un-breakable (this is how things like cryptocurrency remain secure)
   * RSA signatures encompass all of the data of the RFID tag. Changing a single byte somewhere else in the tag would require a completely different signature to be considered genuine
   * Bambu printers check the content of the tag and then check if the signature is valid.  If the signature is invalid, it rejects the tag
* Cloning Tags
   * Even though there is a signature, a tag can be cloned
   * To clone a tag, it must have the same UID, identical content from the data blocks, and the identical RSA signature
   * Changing even one byte will cause the signature to be invalid, and the tag will be rejected
* Custom Tags
   * This is very unlikely to happen, mostly due to the RSA signature.  Only Bambu has their "Private Key" which is used to digitally sign these tags.
   * To create a custom key, you need to know the following info:
      * UUID -> Encryption Key algorithm (or just use known UID + Key pairs)
      * RSA Signature Private Key. You'd have to get this from bambu, good luck
   * Since Bambulab will likely not remove the signature requirement, you would need custom AMS firmware to read tags and ignore the signature

### How to contribute
If you have a ProxMark3 (or other RFID debug tool), you can sniff and decrypt the contents of your tags and submit them for review.
The more data we have, the easier it is to compare differences to learn what each byte represents. A lot of the contents have been decypher (see [Tag stucture](#tag-stucture)), but there is still more unknown data still left to decypher.

## Todos/Timeline/Next steps

- [ ] Tool for automatic trace analysis
- [ ] Web service for tag submisson with automatic anonymized data publishing to github
- [ ] Tag content analysis
- [ ] Generate keys based on an arbitrary UID


## Required Equipment

- Bambulab 3D Printer with AMS
- Bambulab Filament spool **or** the related tags
- A proxmark3 compatible rfid reader
- proxmark3 installed on your computer

### Proxmark3 compatible readers

#### Proxmark3 easy
![](images/Proxmark3_easy.png)

A Proxmark 3 easy is sufficient for all the tasks that need to be done. You can buy a clone from alixepress, amazon or dangerous things.


## Hacking a Bambulab Tag and readout of its data
We document here the most simple approach to get all required A-Keys and the data of the tag.
The easiest way is to sniff the data.

### Bambulab AMS RFID readers and sniffing
The Bambulab AMS RFID readers are locate between slot 1&2 and slot 3&4

![](images/filament-slots.jpg)

For sniffing you can place a bambulab spool in slot 1 and place the reader next to the AMS reader.
If you have already a single tag you need to place a spool **without a tag** in slot one and tape a tag on the top side of the reader and hold the proxmark3 next to the reader in such a way that the proxmark3 reader's bottom side is directed to the AMS reader so the proxmark3 reader is between the tag and the AMS reader. It is recommended to rotate the proxmark3 reader similar to the spool. Details can be found in the next steps.

### Sniffing the data

To start the sniffing connect your rfid reader and open your proxmark3. 
Start sniffing with:

`hf 14a sniff -c -r`

Hold the proxmark3 reader next to the AMS reader and load the filament, or if already loaded tap the update icon on the screen.

When you are done, you can press the button on the side of the Proxmark3 to stop the trace. To visualize the trace you just enter:

`trace list -t mf`

You should be able to already see the first keys. Until you see a message:
"Nested authentication detected." with some bruteforce command: `tools/mf_nonce_brute/mf_nonce_brute <parameters>`

Execute this command in the proxmark3 directory in an other terminal and write down or save the found key.

Check the date for crc errors and if it's fine save the trace with the following command.

`trace save -f <trace-name>`

You can now record all your tags. If you want to load the traces later

`trace load -f <trace-name>`

To view the loaded trace just enter the following command.

`trace list -1 -t mf`

If you are using traces in the next steps you need to add the `-1` option when you analyze the traces.

### Getting the other keys by analyzing the log file

Remove the spool/tag from the printer and place it on the reader so we can check all the keys.

Now a dictionary (`*.dic`) file with all the already found and bruteforced keys must be created.

Enter the keys line by line into that file.

The next steps need to be repeated until you have all the keys. (A script for this is already WIP)

1. `trace list -t mf -f <dic_file>`
2. bruteforce the new keys with the displayed command in a separate terminal and add all new keys to the dict file
3. verify the keys: `hf mf fchk --1k -f <dic_file>`
4. Go to 1 until you found all keys

## Data Readout

Before the data can be read we need to generate a key file

`hf mf fchk --1k -f <dic_file> --dump`

The output is a binary key file: `hf-mf-<TAG UID>-key.bin`

Dump now the data:

`hf mf dump --1k --keys hf-mf-<TAG UID>-key.bin`

This can be viewed now in a hex or binary editor or you can view it with:

`hf mf view -f hf-mf-<TAG UID>-dump.bin`


## Tag Documentation
This contains documentation for the known and unknown data that is contained in each block on the RFID tag.
### Block Overview
Summary of what kind of data is stored in each block. Detailed info for each block is documented below.
| sec | blk | Data                                                                                   |
|-----|-----|----------------------------------------------------------------------------------------|
|  0  |  0  | [Block 0](#block-0) UID and Tag Manufacturer Data                                      |
|  0  |  1  | [Block 1](#block-1) Tray Info Index                                                    |
|  0  |  2  | [Block 2](#block-2) Filament Type                                                      |
|  0  |  3  | [Block 3](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to BambuLab       |
|  1  |  0  | [Block 4](#block-4) Detailed Filament Type                                             |
|  1  |  1  | [Block 5](#block-5) Spool Weight, Color Code                                           |
|  1  |  2  | [Block 6](#block-6) Min/Max Hotend, Bed Temp, Bed Temp Type, Drying Time, Drying Temp  |
|  1  |  3  | [Block 7](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to BambuLab       |
|  2  |  0  | [Block 8](#block-8) X Cam Info                                                         |
|  2  |  1  | [Block 9](#block-9) Tray UID                                                           |
|  2  |  2  | [Block 10](#block-10) **Unknown**                                                      |
|  2  |  3  | [Block 11](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to BambuLab      |
|  3  |  0  | [Block 12](#block-12) Production Date/Time                                             |
|  3  |  1  | [Block 13](#block-13) **Unknown**                                                      |
|  3  |  2  | [Block 14](#block-14) **Unknown**                                                      |
|  3  |  3  | [Block 15](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to BambuLab      |
|  4  |  0  | **Empty**                                                                              |
|  4  |  1  | **Empty**                                                                              |
|  4  |  2  | **Empty**                                                                              |
|  4  |  3  | [Block 19](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to BambuLab      |
|  5  |  0  | **Empty**                                                                              |
|  5  |  1  | **Empty**                                                                              |
|  5  |  2  | **Empty**                                                                              |
|  5  |  3  | [Block 23](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to BambuLab      |
|  6  |  0  | **Empty**                                                                              |
|  6  |  1  | **Empty**                                                                              |
|  6  |  2  | **Empty**                                                                              |
|  6  |  3  | [Block 27](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to BambuLab      |
|  7  |  0  | **Empty**                                                                              |
|  7  |  1  | **Empty**                                                                              |
|  7  |  2  | **Empty**                                                                              |
|  7  |  3  | [Block 31](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to BambuLab      |
|  8  |  0  | **Empty**                                                                              |
|  8  |  1  | **Empty**                                                                              |
|  8  |  2  | **Empty**                                                                              |
|  8  |  3  | [Block 35](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to BambuLab      |
|  9  |  0  | **Empty**                                                                              |
|  9  |  1  | **Empty**                                                                              |
|  9  |  2  | **Empty**                                                                              |
|  9  |  3  | [Block 39](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to BambuLab      |
| 10-15 | *  | **RSA-2048 Signature**                                                                |


The first part of the filament serial number seems to be the Tag UID.

LE = Little Endian

### MIFARE Encryption Keys
Every 4th block (eg Sector X, Block 3) contains encryption keys that are part of the MIFARE RFID standard.
This has nothing to do with BambuLab's memory format.
All BambuLab tags use the same Permission Bits (Access Control)

Example Data:
`AA AA AA AA AA AA PP PP PP PP BB BB BB BB BB BB`

| bytes   | type     |  example data location   | Description                                   |
|---------|----------|--------------------------|-----------------------------------------------|
|  5-0    | RAW Bin  | AA AA AA AA AA AA        | A-Key                                         |
|  9-6    | RAW Bin  | PP PP PP PP              | Permission Bits (Access Control) ALWAYS `87 87  87 69` (hex) for Bambu Tags |
|  15-10  | RAW Bin  | BB BB BB BB BB BB        | B-Key (always `00 00 00 00 00 00` for Bambu tags) |

### Block 0

Note: Block 0 is Read-only. The contents are set by the tag manufacturer.

Example Data:
`AA AA AA AA BB BB BB BB BB BB BB BB BB BB BB BB`

| bytes | type     |  example data location              | Description                                   |
|-------|----------|-------------------------------------|-----------------------------------------------|
|  7-0  | string   | AA AA AA AA                         | Tag UID                                       |
| 15-8  |  string  | BB BB BB BB BB BB BB BB BB BB BB BB | Tag Manufacturer Data (Bin)                   |

### Block 1

Example Data:
`AA AA AA AA AA AA AA AA BB BB BB BB BB BB BB BB`

| bytes | type     |  example data location   | Description                                   |
|-------|----------|--------------------------|-----------------------------------------------|
|  7-0  | string   | BB BB BB BB BB BB BB BB  | Tray Info Index - Unique Material Identifier  |
| 15-8  |  string  | AA AA AA AA AA AA AA AA  | **Unkown**                                    |

### Block 2

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| bytes | type     |  example data location                          | Description                       |
|-------|----------|-------------------------------------------------|-----------------------------------|
|  15-0  | string  | AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA | Filament type                     |


### Block 4

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| bytes | type     |  example data location                          |description                      |
|-------|----------|-------------------------------------------------|---------------------------------|
|  15-0  | string  | AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA | detailed Filament type          |

Known Values:
- PLA Basic

### Block 5

Example Data:
`AA AA AA AA BB BB CC CC CC CC CC CC CC CC CC CC`

| bytes | type                 |  example data location         | Description                             |
|-------|----------------|--------------------------------|-----------------------------------------------|
|  9-0 | **Unkown**      | CC CC CC CC CC CC CC CC CC CC  | **Unkown**                                    |
| 11-10  |  uint16 (LE)  | BB BB                          | Spool Weight in g  HEX: E803 --> 1000 g       |
| 15-12  |  RGBA in HEX  | AA AA AA AA                    | Color in hex RBGA                             |

### Block 6

Example Data:
`AA AA BB BB CC CC DD DD EE EE FF FF GG GG GG GG`

| bytes | type          |  example data location   | Description                             |
|-------|---------------|--------------------------|-----------------------------------------------|
|  3-0  | **Unused?**   | GG GG GG GG              | **Unkown**                                    |
|  5-4  | uint16 (LE)   | FF FF                    | Min- or Maxtemperature for Hotend             |
|  7-6  | uint16 (LE)   | EE EE                    | Min- or Maxtemperature for Hotend             |
|  9-8  | uint16 (LE)   | DD DD                    | Bed Temperatur in °C                          |
| 11-10 | uint16 (LE)   | CC CC                    | Bed Temerature Type                           |
| 13-12 | uint16 (LE)   | BB BB                    | Drying time in h                              |
| 15-14 | uint16 (LE)   | AA AA                    | Drying temp in °C                             |


### Block 8

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA BB BB BB BB`

| bytes | type       |  example data location              |description                      |
|-------|------------|-------------------------------------|---------------------------------|
|  3-0  | **Unkown** | BB BB BB BB                         | **Unkown**                      |
| 15-4  | RAW Bin    | AA AA AA AA AA AA AA AA AA AA AA AA | X Cam info                      |

### Block 9

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| bytes | type     |  example data location                          | Description                       |
|-------|----------|-------------------------------------------------|-----------------------------------|
| 15-0  | UID      | AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA | TrayUID                           |

### Block 10

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| bytes | type     |  example data location                          | Description                       |
|-------|----------|-------------------------------------------------|-----------------------------------|
| 15-0  | Unknown  | AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA | **Unknown** (binary data)             |

### Block 12

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| bytes | type     |  example data location                          | Description                       |
|-------|----------|-------------------------------------------------|----------------------------------------|
| 15-0  | string   | AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA | Production Date and Time in ASCII ?  `<year>_<month>_<day>_<hour>_<minute>`                           |

### Block 13

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| bytes | type     |  example data location                          | Description                       |
|-------|----------|-------------------------------------------------|-----------------------------------|
| 15-0  | Unknown  | AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA | **Unknown** (ASCII data)             |

### Block 14

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| bytes | type     |  example data location                          | Description                       |
|-------|----------|-------------------------------------------------|-----------------------------------|
| 15-0  | Unknown  | AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA | **Unknown** (binary data)             |


## Compatible RFID tags -  By generation

Gen 1 --> **Not compatible**(due to AMS checking if tag is unlockable with command 0x40)

Gen 2 --> **Works**

Gen 2 OTW --> **Not tested**

Gen 3 --> **Not tested**

Gen 4 --> **Not tested**(The best option but pricey and hard to source in small chip formfactor)
