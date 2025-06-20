# Hacking a Bambu Lab Tag and readout of its data

 We have documented here all the approaches we discovered along the way to get all required keys and data out of the tag. Instructions here are mainly focused on using the _**Proxmark 3**_, as this is what we have and use. There are many other devices capable of doing this, if you have discovered other ways of doing this and would like to contribute to it's documentation, please feel free to submit a pull request.
 
Currently, the easiest way is using the built-in function of the latest version of Proxmark3 (Iceman fork).

## Table of contents
<!--ts-->
* [Dumping Tags using Proxmark3](#dumping-tags-using-proxmark3-iceman-fork)
* [Deriving the keys](#deriving-the-keys)
* [Proxmark3 fm11rf08s recovery script](#proxmark3-fm11rf08s-recovery-script)
* [Sniffing the tag data with a Proxmark3 (legacy method)](#sniffing-the-tag-data-with-a-proxmark3-legacy-method)
<!--te-->

### Dumping Tags using Proxmark3 (Iceman fork)
As of 29th of May 2025, [pelrun](https://github.com/pelrun) has implemented functions into pm3 which allows for a much faster and simpler process to generate the keys and dump files from Bambu Lab filament RFID tags. Please update your copy of pm3 by running 
```git pull```
To replicate your own tags or contribute to the library, you can easily make dump and key files of your own tags by running the following commands, after placing the tag on your Proxmark 3,
```
hf mf bambukeys -r -d;hf mf dump
```
or
```
hf mf bambukeys -r -d
hf mf dump
```
This process should only take a few seconds with an expected output similar to below, (to keep things short, dumps of key and data were omitted)
```
[=] -----------------------------------
[=]  UID 4b... XX XX XX XX
[=] -----------------------------------

[+] Saved 192 bytes to binary file `C:\Users\exiom\Desktop\ProxSpace\pm3/hf-mf-XXXXXXXX-key.bin`
[+] Loaded binary key file `C:\Users\exiom\Desktop\ProxSpace\pm3/hf-mf-XXXXXXXX-key.bin`
[=] Reading sector access bits...
[=] .................
[+] Finished reading sector access bits
[=] Dumping all blocks from card...
[-] Sector... 15 block... 3 ( ok )
[+] Succeeded in dumping all blocks

[+] time: 10 seconds

[=] -----+-----+-------------------------------------------------+-----------------
[=]  sec | blk | data                                            | ascii
[=] -----+-----+-------------------------------------------------+-----------------

[+] Saved 1024 bytes to binary file `C:\Users\exiom\Desktop\ProxSpace\pm3/hf-mf-XXXXXXXX-dump.bin`
[+] Saved to json file C:\Users\exiom\Desktop\ProxSpace\pm3/hf-mf-XXXXXXXX-dump.json
```
Once the above command is completed you will see that the data dump and keys will have been saved to the working folder of PM3.

You can find out what each block of data means here, [Bambu Lab Filament Tag Documentation](./docs/BambuLabRfid.md)

Below continues with more technical explainations and legacy methods. If that doesn't interests you, your instructions are complete here.

### Deriving the keys

A way to derive the keys from the UID of an RFID tag was discovered, which unlocked the ability to scan and scrape RFID tag data without sniffing, as well as with other devices like the Flipper Zero. A script is included in the repository to derive the keys from the UID of a tag.

First, obtain the tag's UID:

- Proxmark3
  1. Run the Proxmark3 software by running `pm3` in the terminal
  2. Place the Proxmark3 device on the RFID tag of the spool
  3. Run `hf mf info` and look for the UID line item
- Flipper Zero
  1. Open the NFC app and scan the tag
  2. The Flipper will attempt to decrypt the tag, but you can skip the "Nested Dictionary (Backdoor)" step for speed
  3. The UID of the tag will appear on-screen
- Bambu Lab AMS
  1. Load the spool into an AMS slot and wait for it to finish loading
  2. View the spool's details on the printer's touchscreen, Bambu Studio or Bambu Handy
  3. The UID is the first eight characters of the spool's serial number

Next, run the key derivation script and pipe its output to a file by running `python3 deriveKeys.py [UID] > ./keys.dic`.

Then, use the keys file to extract the data from the RFID tag:

- Proxmark3
  1. Run the Proxmark3 software by running `pm3` in the terminal
  2. Place the Proxmark3 device on the RFID tag of the spool
  3. Run `hf mf dump -k ./keys.dic` to dump the RFID tag's contents
- Flipper Zero
  1. Open the qFlipper program and connect your Flipper to your computer
    - You may also connect the SD card directly to your computer
  2. Navigate to `SD Card/nfc/assets/`
  3. Copy the `mf_classic_dict_user.nfc` file to your computer
  4. Copy the contents of `keys.dic` to `mf_classic_dict_user.nfc`
  5. Copy `mf_classic_dict_user.nfc` back onto your Flipper
  6. Use the NFC app to scan your tag

### Proxmark3 fm11rf08s recovery script

In 2024, a new backdoor[^rfid-backdoor] was found that makes it much easier to obtain the data from the RFID tags. A script is included in the proxmark3 software since v4.18994 (nicknamed "Backdoor"), which allows us to utilize this backdoor. Before this script was implemented, the tag had to be sniffed by placing the spool in the AMS and sniffing the packets transferred between the tag and the AMS.

Place your reader on the tag, start proxmark3 (run `pm3`) and run the following command:

`script run fm11rf08s_recovery`

This script takes about 15-20 minutes to complete. Once it has finished, you will receive a binary key file and a dump.

To visualize the data on the tag, run the following:

`script run fm11rf08_full -b`

### Sniffing the tag data with a Proxmark3 (legacy method)

Before the above methods were developed, tag data had to be obtained by sniffing the data between the RFID tag and the AMS using a Proxmark3-compatible device.

To read how to obtain the tag data using the legacy sniffing method, see the [TagSniffing.md](./docs/TagSniffing.md).
