# RFID Tag Cloning

This serves as a guide on making a clone or your own dump or one from this library, and assumes you have a Proxmark3 and using ProxSpace. As there are plenty of guides online that can better explain how to set this up and therefore it will not be within the scope of this guide.

## Table of contents
<!--ts-->
* [Compatible RFID tags - By generation](#compatible-rfid-tags---by-generation)
* [Writing to Blank tags](#writing-to-blank-tags)
  * [FUID](#fuid)
  * [UFUID](#ufuid)
<!--te-->

## Compatible RFID tags - By generation

There are tags known as "Magic Tags" which allow functionality that's not part of the classic MIFARE spec.
One example is that most Magic Tags allow the UID to be changed, which is normally read-only on MIFARE tags.
Magic tags are often refered to by their "generation", eg "Magic Gen 1". Each newer generation increases the functionality, but tends to also be more expensive)

Name inside the brackets are alternative names these tags are generally named under in various marketplaces such as AliExpress

- Gen 1 (UID) --> **Not compatible** (AMS checks if tag is unlockable with command 0x40)
- Gen 2 (CUID) --> **Inconsistent or No longer works** (AMS writes a winky face to block 0, thereby "bricking" the tag)
- Gen 3 --> **Not tested**
- Gen 4 --> **Works** (The best option but pricey and hard to source in small chip formfactor)
  - FUID --> **Works** Marketed as "Write-once UID". Functions similarly to a Gen 2 tag, once a UID is written, it cannot be changed.
  - UFUID --> **Works** Marketed as "Sealable UID". Functions similarly to a Gen 1 tag, until it is "sealed" by the user.

More information on the use of magic cards can be found at https://github.com/RfidResearchGroup/proxmark3/blob/master/doc/magic_cards_notes.md#mifare-classic-uscuid

## Writing to Blank tags
⚠ *If you purchased bare coil tags and have trouble reading them, try spacing them away from your Proxmark 3 (10mm worked for me).* ⚠

⚠ *ALWAYS CHECK THAT YOU CAN CONSISTENTLY READ YOUR TAG USING THE INFO COMMAND BEFORE ATTEMPTING TO WRITE TO THEM.* ⚠

⚠ *To ease frustrations caused by typos when issuing commands, I encourage you to use the copy button on the right, especially when multiple commands are issued using the same line.* ⚠

### FUID
FUIDs are marketed as "write once UID", it has a default UID of `AA55C396` and will allow writes to block 0 in this state. It will lock once written to.

#### Identify
You can identify the tag by issuing the following commands and will show these expected results
```
hf mf info
```
For an unlocked card the following will show,
```
[usb] pm3 --> hf mf info
[=] --- ISO14443-a Information ---------------------
[+]  UID: AA 55 C3 96
[=] --- Magic Tag Information
[+] Magic capabilities... Gen 2 / CUID
[+] Magic capabilities... Gen 4 GDM / USCUID ( Gen4 Magic Wakeup )
[+] Magic capabilities... Write Once / FUID
```
For an locked card the following will show,
```
[=] --- Magic Tag Information
[=] <n/a>
```

#### Write FUID
For simplity, you need to copy the desired source dump file (hf-mf-XXXXXXXX-dump.bin) and it's key file (hf-mf-XXXXXXXX-key.bin) into the `pm3` folder of `ProxSpace` wherever this maybe on your computer.

To write to the FUID tag, we will issue the following command (replace hf-mf-XXXXXXXX-dump.bin with the file name of your source dump file)
```
hf mf restore --force -u XXXXXXXX
```
Expected Output:
```
[+] Loaded binary key file `hf-mf-5AF731B5-key.bin`
[=] Using key file `hf-mf-5AF731B5-key.bin`
[+] Loaded 1024 bytes from binary file `hf-mf-5AF731B5-dump.bin`

Wall of write messages omitted ending in ( ok )

[=] Done!
```
You can verify that the tag has been successfully written by again running `hf mf info`, the UID should now be different to the first time you ran this command and matches that of the source dump file.
```
[usb] pm3 --> hf mf info
[=] --- ISO14443-a Information ---------------------
[+]  UID: XX XX XX XX
```
You can additionally verify the content of the tag by issuing the command,
```
hf mf dump --ns
```
Your FUID tag is now written, locked and ready to use.



### UFUID
UFUIDs are marketed as a "sealable UID", it will allow writes to the card until it is "sealed" by the user.

#### Identify
You can identify the tag by issuing the following command:
```
hf mf info
```
For an unlocked card the following will show,
```
[=] --- Magic Tag Information
[+] Magic capabilities... Gen 1a
[+] Magic capabilities... Gen 4 GDM / USCUID ( ZUID Gen1 Magic Wakeup )
```
For an locked card the following will show,
```
[=] --- Magic Tag Information
[+] Magic capabilities... Gen 4 GDM / USCUID ( Gen4 Magic Wakeup )
```

#### Write UFUID
For simplity, you need to copy the desired source dump file (hf-mf-XXXXXXXX-dump.bin) and it's key file (hf-mf-XXXXXXXX-key.bin) into the `pm3` folder of `ProxSpace` wherever this maybe on your computer.

To write to the UFUID tag, we will issue the following gen1a command (replace hf-mf-XXXXXXXX-dump.bin with the file name of your source dump file)
```
hf mf cload -f hf-mf-XXXXXXXX-dump.bin
```
Expected Output:
```
[+] Loaded 1024 bytes from binary file `hf-mf-XXXXXXXX-dump.bin`
[=] Copying to magic gen1a MIFARE Classic 1K
[=] .................................................................
[+] Card loaded 64 blocks from file
[=] Done!
```
You can verify that the tag has been successfully written by again running `hf mf info`, the UID should now be different to the first time you ran this command and matches that of the source dump file.
```
[usb] pm3 --> hf mf info
[=] --- ISO14443-a Information ---------------------
[+]  UID: XX XX XX XX
```
You can additionally verify the content of the tag by issuing the command,
```
hf mf dump --ns
```

#### Seal UFUID
Before you can use this tag, you will need to seal the UFUID tag by issuing the following commands, otherwise it will respond to Magic Card Gen1 commands which the AMS will identify and ignore the tag. 

⚠ *Please use the copy button on the right, as this procedure depends on you issuing the chain of commands succesively and completing the full set within a very short period of time.* ⚠
```
hf 14a raw -a -k -b 7 40;hf 14a raw -k 43;hf 14a raw -k -c e100;hf 14a raw -c 85000000000000000000000000000008
```
Expected Output:
```
[usb] pm3 --> hf 14a raw -a -k -b 7 40;hf 14a raw -k 43;hf 14a raw -k -c e100;hf 14a raw -c 85000000000000000000000000000008
[+] 0A
[+] 0A
[+] 0A
[+] 0A
```
Now, when you issue the command `hf mf info`, it should now look like this,
```
[=] --- Magic Tag Information
[=] <n/a>
```
Your UFUID tag is now written, locked and ready to use.
