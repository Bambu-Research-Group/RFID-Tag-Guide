# Bambulab RFID Tag Guide

This guide gives you a basic overview how you can decrypt and read your tags. Since we don't know how Bambulab will react on this guide and the general reverse engineering of the tags: **Please don't share you tag's UID and the related keys for now.**

We are currently working on a way to submit the tag data in a secure way so analysis on the data could be done.

#  Table of contents
<!--ts-->
   * [Todos/Timeline/Next steps](#todostimelinenext-steps)
   * [Required Equipment](#required-equipment)
      * [Proxmark3 compatible readers](#proxmark3-compatible-readers)
         * [Proxmark3 easy](#proxmark3-easy)
   * [Hacking a Bambulab Tag and readout of its data](#hacking-a-bambulab-tag-and-readout-of-its-data)
      * [Bambulab AMS RFID readers and sniffing](#bambulab-ams-rfid-readers-and-sniffing)
      * [Sniffing the data](#sniffing-the-data)
      * [Getting the other keys by analyzing the log file](#getting-the-other-keys-by-analyzing-the-log-file)
   * [Data Readout](#data-readout)
   * [Generate Keys based on random UID](#generate-keys-based-on-random-uid)
   * [Tag stucture](#tag-stucture)
      * [Overview](#overview)
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

## Todos/Timeline/Next steps

- [ ] Tool for automatic trace analysis
- [ ] Web service for tag submisson with automatic anonymized data publishing to github
- [ ] Tag content analysis


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


## Generate Keys based on random UID

**TODO**

## Tag stucture

The following infos are already known

### Overview

| sec | blk | Data                                                                                   |
|-----|-----|----------------------------------------------------------------------------------------|
|  0  |  0  | UID and Manufacturing Data - Tag specific                                              |
|  0  |  1  | [Block 1 Description](#block-1)                                                        |
|  0  |  2  | [Block 2 Description](#block-2)                                                        |
|  0  |  3  | A-Keys Sector 0 (6 bytes), Permission Sector 1 (4 bytes), B-Keys Sector 0 (6 bytes)    |
|  1  |  4  | [Block 4 Description](#block-4)                                                        |
|  1  |  5  | [Block 5 Description](#block-5)                                                        |
|  1  |  6  | [Block 6 Description](#block-6)                                                        |
|  1  |  7  | A-Keys Sector 1 (6 bytes), Permission Sector 1 (4 bytes), B-Keys Sector 1 (6 bytes)    |
|  2  |  8  | [Block 8 Description](#block-8)                                                        |
|  2  |  9  | [Block 9 Description](#block-9)                                                        |
|  2  | 10  | **Unknown binary data**                                                                |
|  2  | 11  | A-Keys Sector 2 (6 bytes), Permission Sector 2 (4 bytes), B-Keys Sector 2 (6 bytes)    |
|  3  | 12  | [Block 12 Description](#block-12)                                                      |
|  3  | 13  | **Unkown string data** could be part of production date/time                           |
|  3  | 14  | **Unkown binary data**                                                                 |
|  3  | 15  | A-Keys Sector 3 (6 bytes), Permission  Sector 3 (4 bytes), B-Keys Sector 3 (6 bytes)   |
|  4  | 16  | **Empty**                                                                              |
|  4  | 17  | **Empty**                                                                              |
|  4  | 18  | **Empty**                                                                              |
|  4  | 19  | A-Keys Sector 4 (6 bytes), Permission  Sector 4 (4 bytes), B-Keys Sector 4 (6 bytes)   |
|  5  | 20  | **Empty**                                                                              |
|  5  | 21  | **Empty**                                                                              |
|  5  | 22  | **Empty**                                                                              |
|  5  | 23  | A-Keys Sector 5 (6 bytes), Permission  Sector 5 (4 bytes), B-Keys Sector 5 (6 bytes)   |
|  6  | 24  | **Empty**                                                                              |
|  6  | 25  | **Empty**                                                                              |
|  6  | 26  | **Empty**                                                                              |
|  6  | 27  | A-Keys Sector 6 (6 bytes), Permission  Sector 6 (4 bytes), B-Keys Sector 6 (6 bytes)   |
|  7  | 28  | **Empty**                                                                              |
|  7  | 29  | **Empty**                                                                              |
|  7  | 30  | **Empty**                                                                              |
|  7  | 31  | A-Keys Sector 7 (6 bytes), Permission  Sector 7 (4 bytes), B-Keys Sector 7 (6 bytes)   |
|  8  | 32  | **Empty**                                                                              |
|  8  | 33  | **Empty**                                                                              |
|  8  | 34  | **Empty**                                                                              |
|  8  | 35  | A-Keys Sector 8 (6 bytes), Permission  Sector 8 (4 bytes), B-Keys Sector 8 (6 bytes)   |
|  9  | 37  | **Empty**                                                                              |
|  9  | 38  | **Empty**                                                                              |
|  9  | 39  | **Empty**                                                                              |
|  9  | 15  | A-Keys Sector 9 (6 bytes), Permission  Sector 9 (4 bytes), B-Keys Sector 9 (6 bytes)   |
| 10-15 | *  | **Unknown binary data** Maybe CRC                                                     |


The first part of the filament serial number seems to be the Tag UID.

LE = Little Endian


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

### Block 12

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| bytes | type     |  example data location                          | Description                       |
|-------|----------|-------------------------------------------------|----------------------------------------|
| 15-0  | string   | AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA | Production Date and Time in ASCII ?  `<year>_<month>_<day>_<hour>_<minute>`                           |



## Compatible RFID tags -  By generation

Gen 1 --> **Not compatible**(due to AMS checking if tag is unlockable with command 0x40)

Gen 2 --> **Works**

Gen 2 OTW --> **Not tested**

Gen 3 --> **Not tested**

Gen 4 --> **Not tested**(The best option but pricey and hard to source in small chip formfactor)
