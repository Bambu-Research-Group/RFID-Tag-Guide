# Bambu Lab RFID Tag Guide
This repository contains the collective research of the Bambu Lab Filament RFID Tags and serves as a guide to give you a basic overview how you can decrypt and read your tags.

Please visit the [Bambu Lab RFID Library Repository](https://github.com/queengooborg/Bambu-Lab-RFID-Library) to view our collection of tags.

[![Link to Discord](https://img.shields.io/badge/Discord-join_now-blue?style=flat-square&logo=discord&logoColor=white&label=Discord&color=blue)](https://discord.gg/zVfCVubwr7)

# Table of contents

<!--ts-->
   * [Project Summary](#project-summary)
      * [FAQs](#faqs)
      * [How to contribute](#how-to-contribute)
      * [Todos/Timeline/Next steps](#todostimelinenext-steps)
   * [Requirements](#requirements)
      * [Proxmark3 compatible readers](#proxmark3-compatible-readers)
         * [Proxmark3 Easy](#proxmark3-easy)
   * [Tag Documentation](#tag-documentation)
   * [How do RFID tags work?](#how-do-rfid-tags-work)
   * [Hacking a Bambu Lab Tag and readout of its data](#hacking-a-bambu-lab-tag-and-readout-of-its-data)
   * [RFID Tag Cloning](#rfid-tag-cloning)
   * [Reverse engineering RFID Board](#reverse-engineering-rfid-board)
<!--te-->

## Project Summary

This is a research group dedicated to documenting the data structures used by Bambu Lab 3D printers to identify filament data.

### FAQs

- **Can I create custom tags?**
  - No, tags are digitally signed. Even if you modify the contents, the printer will reject any tags without a valid RSA signature
  - An [Open Source RFID Tag](OpenSourceRfid.md) has been proposed to allow anyone to create / modify their own tags. This must be adopted by printer manufacturers, or you can mod your own printer for support
- **Can I clone tags?**
  - Yes, you can read and clone tags using a tool such as a Proxmark3. Check out our [collection of scanned tags](https://github.com/queengooborg/Bambu-Lab-RFID-Library)
- **What are the next steps for this project?**
  - Decyphering the rest of the unknown tag content
  - Custom AMS firmware that allows custom tags to be read while ignoring the signature
  - See [Todos/Timeline/Next steps](#todostimelinenext-steps) for more info

### How to contribute

If you have a Proxmark3 (or other RFID debugging tool), you can decrypt the contents of your Bambu Lab RFID tags and submit them via [Discord](https://discord.gg/zVfCVubwr7), or alternatively submit a Pull Request to the [Bambu Lab RFID Library Repository](https://github.com/queengooborg/Bambu-Lab-RFID-Library).

A lot of the contents have been deciphered, but the more data we have, the easier it is to compare differences to learn what each byte represents and double-check our answers.

### Todos/Timeline/Next steps

- [ ] Tool for automatic trace analysis
- [x] Tag content analysis
- [x] Generate keys based on an arbitrary UID

## Requirements

- Basic command line knowledge
- A computer running macOS or Linux, or a Windows computer with a WSL installation
- Python 3.6 or higher
- Bambu Lab Filament spool **or** the related tags
- An NFC/RFID reader that can read encrypted tags, such as...
  - A Proxmark3-compatible RFID reader (recommended)
    - The [proxmark3 (Iceman fork) software](https://github.com/RfidResearchGroup/proxmark3)
      - Requires v4.20469 or higher
      - You MUST use the Iceman fork as the original version of the software is unmaintained; all instructions and scripts are written for the Iceman fork and will not work on the original version
  - A Flipper Zero

### Proxmark3 compatible readers

#### Proxmark3 Easy

![](images/Proxmark3_easy.png)

A Proxmark3 Easy is sufficient for all the tasks that need to be done. You can buy a clone from Alixepress, Amazon or Dangerous Things.

## Tag Documentation

For a description of the blocks of a Bambu Lab RFID tag, see [docs/BambuLabRfid.md](./docs/BambuLabRfid.md).

For a description of the blocks of a Creality RFID tag, see [docs/CrealityRfid.md](./docs/CrealityRfid.md).

An open-source standard proposal, OpenTag, is being incubated in this repository.  For a description of the standard, see [docs/OpenTag.md](./docs/OpenTag.md).

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
  - This is very unlikely to happen, mostly due to the RSA signature. Only Bambu Lab has their "Private Key" which is used to digitally sign these tags.
  - To create a custom key, you need to know the following info:
    - RSA Signature Private Key. You'd have to get this from bambu, good luck
  - Since Bambu Lab will likely not remove the signature requirement, you would need custom AMS firmware to read tags and ignore the signature

## Hacking a Bambu Lab Tag and readout of its data

Please visit [ReadTags.md](./docs/ReadTags.md), where we documented all the approaches we discovered along the way to get all required keys and data out of the tag.

## RFID Tag Cloning

Please visit [WriteTags.md](./docs/WriteTags.md), where we documented all the current and past ways of cloning Bambu Lab filament RFID tags and compatible RFID tags used to clone them.

## Reverse engineering RFID Board

For ease of debugging and lowering the cost of failures, the RFID board is reverse-engineered. You can find complete production-ready gerber files and a bill of materials in [rfid-board](./rfid-board) folder.

[^rfid-backdoor]: https://eprint.iacr.org/2024/1275.pdf
