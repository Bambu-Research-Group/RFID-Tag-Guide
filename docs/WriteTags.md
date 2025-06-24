# RFID Tag Cloning

This document serves as a guide for copying tag dumps onto new tags.
This guide is written for the Proxmark3, however this may also be performed with other devices like the Flipper Zero.

# Table of contents
<!--ts-->
   * [Compatible RFID tags - By generation](#compatible-rfid-tags---by-generation)
   * [Identifying Tag Type](#identifying-tag-type)
      * [Gen 2](#gen-2)
      * [Gen 4 FUID](#gen-4-fuid)
      * [Gen 4 UFUID](#gen-4-ufuid)
   * [Writing Tag Dumps](#writing-tag-dumps)
      * [Seal UFUID](#seal-ufuid)
<!--te-->

## Compatible RFID tags - By generation

There are tags known as "Magic Tags" which allow functionality that is not part of the classic MIFARE spec. One example is that most Magic Tags allow the UID to be changed, which is normally read-only on MIFARE tags. Magic tags are often referred to by their "generation", for example "Magic Gen 1", but some online sellers will use alternate names in their listings (denoted in parenthesis in the list below). Each newer generation increases the functionality, but tends to also be more expensive.

> [!TIP]
> If you purchased bare coil tags and have trouble reading them, try increasing the distance between them and your Proxmark3 to about 10mm.

- Gen 1 (UID) --> **Not compatible** (AMS checks if tag is unlockable with command 0x40)
- Gen 2 (CUID) --> **Inconsistent or No longer works** (AMS writes a winky face to block 0, "bricking" the tag)
- Gen 3 --> **Not tested**
- Gen 4 --> **Works** (The best option, but pricey and hard to source in a small chip formfactor)
  - FUID (Write-Once UID) --> **Works** (Functions similarly to a Gen 2 tag: once a UID is written, it cannot be changed)
  - UFUID (Sealable UID) --> **Works** (Functions similarly to a Gen 1 tag, until it is "sealed" by the user.)

More information on the use of magic cards can be found at https://github.com/RfidResearchGroup/proxmark3/blob/master/doc/magic_cards_notes.md#mifare-classic-uscuid

## Identifying Tag Type

To identify the type of tag you have, place your Proxmark3 on a tag, launch `pm3` in a terminal and run the following command:

```
hf mf info
```

The tag type can be identified based upon its magic capabilities.  Note that if the tag reports no magic capabilities, it is either incompatible or has already been locked.

### Gen 2

Gen 2 tags are marketed as "changeable unique identifier".  Their UID can be changed by the user.

### Gen 4 FUID

FUIDs are marketed as "write once UID".  They have a default UID of `AA55C396` and will allow writes to block 0 in this state. Once the UID is changed, the tag will be locked.

An unlocked tag will have the following magic capabilities:
- Gen 2 / CUID
- Gen 4 GDM / USCUID ( Gen4 Magic Wakeup )
- Write Once / FUID

### Gen 4 UFUID

UFUIDs are marketed as a "sealable UID", it will allow writes to the card until it is "sealed" by the user.

An unlocked tag will have the following magic capabilities:

- Gen 1a
- Gen 4 GDM / USCUID ( ZUID Gen1 Magic Wakeup )

> [!WARNING]
> UFUID tags must be sealed, which is a process that cannot be performed on the Flipper Zero; thus, UFUID tags are not compatible with the Flipper Zero for this use case.

## Writing Tag Dumps

> [!IMPORTANT]
> ALWAYS CHECK THAT YOU CAN CONSISTENTLY READ YOUR TAG USING THE INFO COMMAND BEFORE ATTEMPTING TO WRITE TO THEM.

To write a dump to the tag, run the following command in `pm3` (replace `/path/to/dump.bin` with the actual filepath of your dump):
```
hf mf restore --force -f /path/to/dump.bin -k /path/to/keys.bin
```

> [!NOTE]
> If you have a Gen 4 UFUID tag, it is recommended use the following command instead:
> ```
> hf mf cload -f /path/to/dump.bin
> ```

You can verify that the tag has been successfully written by running `hf mf info` again.  The UID should now match the UID of your dump.

If you wish to perform a full content verification, you can run the following command:
```
hf mf dump --ns
```

### Seal UFUID

Before you can use a UFUID tag on the AMS, you will need to seal the UFUID tag by issuing the following commands, otherwise it will respond to Magic Card Gen1 commands which the AMS will identify and ignore the tag. 

```
hf 14a raw -a -k -b 7 40
hf 14a raw -k 43
hf 14a raw -k -c e100
hf 14a raw -c 85000000000000000000000000000008
```

The tag should now display no magic capabilities when running `hf mf info`.  Your UFUID tag is now written, locked and ready to use.
