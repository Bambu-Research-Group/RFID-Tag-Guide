# Hacking a Bambu Lab Tag and readout of its data

This document describes the various approaches for scanning Bambu Lab RFID tags.
If you have a Proxmark3 device, the easiest way to scan tags is using the built-in `bambukeys` function. Otherwise, if you have another RFID scanning device like a Flipper Zero, a Python script is provided in order to derive the keys from the UID of the tag.

> [!NOTE]
> Please consider submitting your scanned tags to the [Bambu Lab RFID Library](https://github.com/queengooborg/Bambu-Lab-RFID-Library) repository!

# Table of contents

<!--ts-->
      * [Dumping Tags using Proxmark3](#dumping-tags-using-proxmark3)
      * [Deriving the keys](#deriving-the-keys)
      * [Proxmark3 fm11rf08s recovery script (legacy method)](#proxmark3-fm11rf08s-recovery-script-legacy-method)
      * [Sniffing the tag data with a Proxmark3 (legacy method)](#sniffing-the-tag-data-with-a-proxmark3-legacy-method)
<!--te-->

### Dumping Tags using Proxmark3

As of Proxmark3 v4.20469, a new command has been implemented to scan a Bambu Lab RFID tag and automatically derive the keys, offering a fast, one-command way to scan tags.

To scan a tag with this method, place the Proxmark3 device on the tag and run `pm3` in the terminal. Then, in the `pm3` prompt, run:

```
hf mf bambukeys -r -d
hf mf dump
```

This process should only take a few seconds. Once the process is complete, the dump will be saved to your current working directory.

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

### Proxmark3 fm11rf08s recovery script (legacy method)

In 2024, a new backdoor[^rfid-backdoor] was found that makes it much easier to obtain the data from the RFID tags. A script is included in the proxmark3 software since v4.18994 (nicknamed "Backdoor"), which allows us to utilize this backdoor. Before this script was implemented, the tag had to be sniffed by placing the spool in the AMS and sniffing the packets transferred between the tag and the AMS.

Place your reader on the tag, start proxmark3 (run `pm3`) and run the following command:

`script run fm11rf08s_recovery`

This script takes about 15-20 minutes to complete. Once it has finished, you will receive a binary key file and a dump.

To visualize the data on the tag, run the following:

`script run fm11rf08s_full -b`

### Sniffing the tag data with a Proxmark3 (legacy method)

Before the above methods were developed, tag data had to be obtained by sniffing the data between the RFID tag and the AMS using a Proxmark3-compatible device.

To read how to obtain the tag data using the legacy sniffing method, see the [TagSniffing.md](./TagSniffing.md).
