# -*- coding: utf-8 -*-

# Python script to parse Bambu Lab RFID tag data
# Created for https://github.com/Bambu-Research-Group/RFID-Tag-Guide
# Written by Vinyl Da.i'gyu-Kazotetsu (www.queengoob.org), 2024

import sys
import struct
from datetime import datetime

COMPARISON_BLOCKS = [1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14]
IMPORTANT_BLOCKS = [0] + COMPARISON_BLOCKS

BYTES_PER_BLOCK = 16
BLOCKS_PER_TAG = 64
TOTAL_BYTES = BLOCKS_PER_TAG * BYTES_PER_BLOCK

# Byte conversions
def bytes_to_string(data):
    return data.decode('ascii').replace('\x00', ' ').strip()

def bytes_to_hex(data, chunkify = False):
    output = data.hex().upper()
    return " ".join((string[0+i:2+i] for i in range(0, len(string), 2))) if chunkify else output

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

# Classes

class TagLengthMismatchError(TypeError):
    def __init__(self, actual_length):
        super().__init__(f"The data does not appear to be a valid MIFARE 1K RFID tag (received {actual_length} bytes / {int(actual_length / BYTES_PER_BLOCK)} blocks, expected {TOTAL_BYTES} bytes / {BLOCKS_PER_TAG} blocks).")

class Tag():
    def __init__(self, filename, data):
        # Check to make sure the data is 1KB
        if len(data) != TOTAL_BYTES:
            raise TagLengthMismatchError(len(data))

        # Store the raw data
        self.filename = filename
        self.blocks = list(data[0+i:BYTES_PER_BLOCK+i] for i in range(0, len(data), BYTES_PER_BLOCK))

        # Parse the data
        self.data = {
            "uid": bytes_to_hex(self.blocks[0][0:4]),
            "filament_type": bytes_to_string(self.blocks[2]),
            "detailed_filament_type": bytes_to_string(self.blocks[4]),
            "color": "#" + bytes_to_hex(self.blocks[5][0:4]),
            "weight": bytes_to_int(self.blocks[5][4:6]), # in g (grams)
            "length": bytes_to_int(self.blocks[14][4:6]), # in m (meters)
            "diameter": bytes_to_float(self.blocks[5][8:12]), # in mm (meters)
            "spool_width": bytes_to_int(self.blocks[10][4:6]) / 100, # in mm (meters)
            "material_id": bytes_to_string(self.blocks[1][8:16]),
            "variant_id": bytes_to_string(self.blocks[1][0:8]),
            "nozzle_diameter": bytes_to_float(self.blocks[8][12:16]), # in mm (meters)
            "temperatures": {
                "min_hotend": bytes_to_int(self.blocks[6][10:12]), # in C (Celsius)
                "max_hotend": bytes_to_int(self.blocks[6][8:10]), # in C (Celsius)
                "bed_temp": bytes_to_int(self.blocks[6][6:8]), # in C (Celsius)
                "bed_temp_type": bytes_to_int(self.blocks[6][4:6]),
                "drying_time": bytes_to_int(self.blocks[6][2:4]), # in hours
                "drying_temp": bytes_to_int(self.blocks[6][0:2]), # in C (Celsius)
            },
            "x_cam_info": self.blocks[8][0:12],
            "tray_uid": self.blocks[9],
            "production_date": bytes_to_date(self.blocks[12]),

            "unknown": bytes_to_string(self.blocks[13]), # Appears to be some sort of date -- on some tags, this is identical to the production date, but not always

        }

    def __str__(self, blocks_to_output = IMPORTANT_BLOCKS):
        result = ""

        for key in self.data:
            result += f"- {key}: {bytes_to_hex(self.data[key]) if type(self.data[key]) == bytes else self.data[key]}\n"

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
            with open(filename, "rb") as f:
                newdata = Tag(filename, f.read())
                data.append(newdata)
        except TagLengthMismatchError:
            if not silent: print(f"{filename} not a valid tag, skipping")

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
