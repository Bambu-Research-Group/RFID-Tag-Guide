# -*- coding: utf-8 -*-

# Python script to generate keys for Bambu Lab RFID tags
# Created for https://github.com/Bambu-Research-Group/RFID-Tag-Guide
# Written by thekakester (https://github.com/thekakester) and Vinyl Da.i'gyu-Kazotetsu (www.queengoob.org), 2024

import sys
from Cryptodome.Protocol.KDF import HKDF
from Cryptodome.Hash import SHA256

if not sys.version_info >= (3, 6):
   print("Python 3.6 or higher is required!")
   exit(-1)

def kdf(uid):
    master = bytes([0x9a,0x75,0x9c,0xf2,0xc4,0xf7,0xca,0xff,0x22,0x2c,0xb9,0x76,0x9b,0x41,0xbc,0x96])
    return HKDF(uid, 6, master, SHA256, 16, context=b"RFID-A\0")

if __name__ == '__main__':
    uid = bytes.fromhex(sys.argv[1])
    keys = kdf(uid)

    output = [a.hex().upper() for a in keys]
    print("\n".join(output))
