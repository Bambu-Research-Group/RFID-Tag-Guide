# Bambu Lab RFID Tag Guide

This guide gives you a basic overview how you can decrypt and read your tags. Since we don't know how Bambu Lab will react on this guide and the general reverse engineering of the tags: **Please don't share you tag's UID and the related keys for now.**

We are currently working on a way to submit the tag data in a secure way so analysis on the data could be done.

[![Link to Discord](https://img.shields.io/badge/Discord-join_now-blue?style=flat-square&logo=discord&logoColor=white&label=Discord&color=blue)](https://discord.gg/zVfCVubwr7)

# Table of contents

<!--ts-->
   * [Project Summary](#project-summary)
      * [FAQs](#faqs)
      * [How to contribute](#how-to-contribute)
      * [Todos/Timeline/Next steps](#todostimelinenext-steps)
   * [Required Equipment](#required-equipment)
      * [Proxmark3 compatible readers](#proxmark3-compatible-readers)
         * [Proxmark3 Easy](#proxmark3-easy)
   * [Hacking a Bambu Lab Tag and readout of its data](#hacking-a-bambu-lab-tag-and-readout-of-its-data)
      * [Proxmark3 fm11rf08s recovery script](#proxmark3-fm11rf08s-recovery-script)
      * [Sniffing the tag data (legacy method)](#sniffing-the-tag-data-legacy-method)
   * [Tag Documentation](#tag-documentation)
   * [How do RFID tags work?](#how-do-rfid-tags-work)
   * [Compatible RFID tags - By generation](#compatible-rfid-tags---by-generation)
   * [Reverse engineering RFID Board](#reverse-engineering-rfid-board)
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

### How to contribute

If you have a Proxmark3 (or other RFID debugging tool), you can sniff and decrypt the contents of your Bambu Lab RFID tags and submit them via [Discord](https://discord.gg/zVfCVubwr7).
A lot of the contents have been deciphered, but the more data we have, the easier it is to compare differences to learn what each byte represents and double-check our answers.

### Todos/Timeline/Next steps

- [ ] Tool for automatic trace analysis
- [ ] Web service for tag submisson with automatic anonymized data publishing to GitHub
- [ ] Tag content analysis
- [ ] Generate keys based on an arbitrary UID

## Required Equipment

- Bambu Lab Filament spool **or** the related tags
- A Proxmark3-compatible RFID reader
- The [proxmark3 (Iceman fork) software](https://github.com/RfidResearchGroup/proxmark3)
  - Requires v4.18994 (codename "Backdoor") or higher
  - You MUST use the Iceman fork as the original version of the software is unmaintained; all instructions and scripts are written for the Iceman fork and will not work on the original version

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

This script takes about 15-20 minutes to complete. Once it has finished, you will receive a binary key file and a dump.

To visualize the data on the tag, run the following:

`script run fm11rf08_full -b`

### Sniffing the tag data (legacy method)

Before the above script was created, tag data had to be obtained by sniffing the data between the RFID tag and the AMS.

To read how to obtain the tag data using the legacy sniffing method, see the [TagSniffing.md](./TagSniffing.md).

## Tag Documentation

For a description of the blocks of a Bambu Lab RFID tag, see [BambuLabRfid.md](./BambuLabRfid.md).

For a description of an open-source standard proposal, see [OpenSourceRfid.md](./OpenSourceRfid.md).

## How do RFID tags work?

Here's a high-level summary of how everything works:

- Bambu Lab printers use MiFare 13.56MHZ RFID tags
  - These tags contain a unique ID that is not encrypted (called the UID)
  - In most cases UID is fixed (not-changable). Some "hackable" RFID tags allow you to set the UID to anything you want
- Blocks (Encrypted)
  - MiFare tags also contain "Blocks" of data. Each block contains info about the spool, such as Material, Color, Manufacturing Date, etc.
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
