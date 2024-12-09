# -*- coding: utf-8 -*-

# Python script to parse Bambu Lab RFID tag data
# Created for https://github.com/Bambu-Research-Group/RFID-Tag-Guide
# Written by Vinyl Da.i'gyu-Kazotetsu (www.queengoob.org), 2024

import sys
import struct
import re
from datetime import datetime
from pathlib import Path

if not sys.version_info >= (3, 6):
   print("Python 3.6 or higher is required!")
   exit(-1)

COMPARISON_BLOCKS = [1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14]
IMPORTANT_BLOCKS = [0] + COMPARISON_BLOCKS

BYTES_PER_BLOCK = 16
BLOCKS_PER_TAG = [64, 72] # 64 = 1KB, 72 = Output from Proxmark fm11rf08 script
TOTAL_BYTES = [blocks * BYTES_PER_BLOCK for blocks in BLOCKS_PER_TAG]

# Byte conversions
def bytes_to_string(data):
    return data.decode('ascii').replace('\x00', ' ').strip()

def bytes_to_hex(data, chunkify = False):
    output = data.hex().upper()
    return " ".join((output[0+i:2+i] for i in range(0, len(output), 2))) if chunkify else output

def bytes_to_int(data):
    return int.from_bytes(data, 'little')

def bytes_to_float(data):
    return struct.unpack('<f', data)[0]

def bytes_to_date(data):
    string = bytes_to_string(data)
    parts = string.split("_")
    if len(parts) < 5:
        return string # Not a date we can process, if it's a date at all
    return datetime(
        year=int(parts[0]),
        month=int(parts[1]),
        day=int(parts[2]),
        hour=int(parts[3]),
        minute=int(parts[4])
    )

# Flipper Helper
def strip_flipper_data(string):
    # Remove comments
    pattern = re.compile(r"^[\w\s]+: [\w\s\d?]+$", re.M)
    data = dict([x.split(": ") for x in pattern.findall(string.decode())])
    
    # Ensure the scan file is for the proper type of tag
    assert(data.get("Version") == "4")
    assert(data.get("Data format version") == "2")
    assert(data.get("Device type") == "Mifare Classic")
    assert(data.get("Mifare Classic type") == "1K")

    output = b""

    for key in data:
        if key.startswith("Block "):
            output += bytes.fromhex(data[key].replace("??", "00"))

    return output

# Classes

class TagLengthMismatchError(TypeError):
    def __init__(self, actual_length):
        super().__init__(f"The data does not appear to be a valid MIFARE 1K RFID tag (received {actual_length} bytes / {int(actual_length / BYTES_PER_BLOCK)} blocks, expected {TOTAL_BYTES} bytes / {BLOCKS_PER_TAG} blocks).")

class Unit():
    def __init__(self, value, unit):
        self.value = value
        self.unit = unit

    def __str__(self):
        return str(self.value) + ("º" if self.unit in ["C", "F"] else "") + self.unit

    def __get_comparison_values(self, other):
        if type(other) in [int, float]:
            return [self.value, other]
        if type(other) != Unit:
            raise TypeError(f"Type {type(other)} cannot be compared with type Unit")
        if self.unit != other.unit:
            raise TypeError(f"Unit type {other.unit} is not identical to {self.unit}")
        return [self.value, other.value]

    def __eq__(self, other):
        values = self.__get_comparison_values(self, other)
        return values[0] == values[1]

    def __lt__(self, other):
        values = self.__get_comparison_values(self, other)
        return values[0] < values[1]

    def __gt__(self, other):
        values = self.__get_comparison_values(self, other)
        return values[0] > values[1]

class ColorList(list):
    def __init__(self, value):
        if type(value) in [list, tuple]:
            super().__init__(value)
        else:
            super().__init__([value])

    def __str__(self):
        return " / ".join("#" + c for c in self)

    def __setitem__(self, index, item):
        super().__setitem__(index, str(item))

    def insert(self, index, item):
        super().insert(index, str(item))

    def append(self, item):
        super().append(str(item))

    def extend(self, other):
        if isinstance(other, type(self)):
            super().extend(other)
        else:
            super().extend(str(item) for item in other)

class Tag():
    def __init__(self, filename, data):
        # Check to make sure the data is 1KB or a known alternative
        if data.startswith(b"Filetype: Flipper NFC"):
            # Flipper NFC dump
            data = strip_flipper_data(data)
        if len(data) not in TOTAL_BYTES:
            raise TagLengthMismatchError(len(data))

        # Store the raw data
        self.filename = filename
        self.blocks = list(data[0+i:BYTES_PER_BLOCK+i] for i in range(0, len(data), BYTES_PER_BLOCK))

        self.warnings = []

        # Check for blank blocks
        for bi in IMPORTANT_BLOCKS:
            if self.blocks[bi] == b'\x00' * BYTES_PER_BLOCK:
                self.warnings.append(f"Block {bi} is blank!")

        # Parse the data
        has_extra_color_info = self.blocks[16][0:2] == b'\x02\x00'
        
        self.data = {
            "uid": bytes_to_hex(self.blocks[0][0:4]),
            "filament_type": bytes_to_string(self.blocks[2]),
            "detailed_filament_type": bytes_to_string(self.blocks[4]),
            "filament_color_count": bytes_to_int(self.blocks[16][2:4]) if has_extra_color_info else 1,
            "filament_color": "#" + bytes_to_hex(self.blocks[5][0:4]),
            "spool_weight": Unit(bytes_to_int(self.blocks[5][4:6]), "g"),
            "filament_length": Unit(bytes_to_int(self.blocks[14][4:6]), "m"),
            "filament_diameter": Unit(bytes_to_float(self.blocks[5][8:12]), "mm"),
            "spool_width": Unit(bytes_to_int(self.blocks[10][4:6]) / 100, "mm"),
            "material_id": bytes_to_string(self.blocks[1][8:16]),
            "variant_id": bytes_to_string(self.blocks[1][0:8]),
            "nozzle_diameter": Unit(round(bytes_to_float(self.blocks[8][12:16]), 1), "mm"),
            "temperatures": {
                "min_hotend": Unit(bytes_to_int(self.blocks[6][10:12]), "C"),
                "max_hotend": Unit(bytes_to_int(self.blocks[6][8:10]), "C"),
                "bed_temp": Unit(bytes_to_int(self.blocks[6][6:8]), "C"),
                "bed_temp_type": bytes_to_int(self.blocks[6][4:6]),
                "drying_time": Unit(bytes_to_int(self.blocks[6][2:4]), "h"),
                "drying_temp": Unit(bytes_to_int(self.blocks[6][0:2]), "C"),
            },
            "x_cam_info": self.blocks[8][0:12],
            "tray_uid": self.blocks[9],
            "production_date": bytes_to_date(self.blocks[12]),
            "unknown_1": bytes_to_string(self.blocks[13]), # Appears to be some sort of date -- on some tags, this is identical to the production date, but not always
            "unknown_2": self.blocks[17][0:2], # Only been "0100" on the PLA Silk Dual Color, "0000" otherwise
        }

        # Check for a second color
        if self.data["filament_color_count"] == 2:
            self.data["filament_color"] += " / #" + bytes_to_hex(self.blocks[16][4:8][::-1])

        # Check for any data in bits that are expected to be blank
        expected_to_be_blank = {
            5: [*range(6,8),*range(12,16)],
            6: range(12,16),
            10: [*range(0,4), *range(6,16)],
            14: [*range(0,4), *range(6,16)],
            17: range(2,16)
        }
        for block in range(18,39):
            if block % 4 == 3:
                continue # Skip MIFARE encryption key blocks
            expected_to_be_blank[block] = list(range(0,16))

        for block in expected_to_be_blank:
            for pos in expected_to_be_blank[block]:
                byte = self.blocks[block][pos]
                if byte != 0:
                    self.warnings.append(f"Data found in block {block}, position {pos} that was expected to be blank (received {byte})")

    def __str__(self, blocks_to_output = IMPORTANT_BLOCKS):
        result = ""

        for key in self.data:
            if type(self.data[key]) == dict:
                result += f"- {key}:\n"
                for tkey in self.data[key]:
                    result += f"  - {tkey}: {self.data[key][tkey]}\n"
            else:
                result += f"- {key}: {bytes_to_hex(self.data[key]) if type(self.data[key]) == bytes else self.data[key]}\n"

        if len(self.warnings):
            result += "- Warnings:\n"
            for warning in self.warnings:
                result += f"  - {warning}\n"

        return result[:-1]

    def print_blocks(self, blocks_to_output = IMPORTANT_BLOCKS):
        for b in range(len(self.blocks)):
            if b not in blocks_to_output:
                continue
            print(f"Block {b:02d}: {bytes_to_hex(self.blocks[b], True)} ({self.blocks[b]})")

    def compare(self, other, blocks_to_compare = COMPARISON_BLOCKS):
        cmp_result = [[False for i in range(BYTES_PER_BLOCK)] for b in blocks_to_compare]

        # Compare all of the blocks
        for bi in range(len(blocks_to_compare)):
            b = blocks_to_compare[bi]
            for i in range(BYTES_PER_BLOCK):
                cmp_result[bi][i] = self.blocks[b][i] == other.blocks[b][i]

        # Print results
        for bi in range(len(cmp_result)):
            print("Block {0:02d}: {1}".format(blocks_to_compare[bi], "".join("✅" if i else "❌" for i in cmp_result[bi])))

def load_data(files_to_load, silent = False):
    data = []
    for filename in files_to_load:
        try:
            filepath = Path(filename)
            with open(filepath, "rb") as f:
                newdata = Tag(filepath, f.read())
                data.append(newdata)
        except TagLengthMismatchError:
            if not silent: print(f"{filepath} not a valid tag, skipping")

    return data

def print_data(data, print_comparisons):
    for i in range(len(data)):
        tag = data[i]
        print(tag.filename)
        print(tag)
        print()

        if print_comparisons and i > 0:
            tag.compare(data[i-1])
            print()

if __name__ == "__main__":
    data = load_data(sys.argv[1:])
    print_data(data, False)
