# Bambu Lab RFID Tag Documentation

This contains documentation for the known and unknown data that is contained in each block on the RFID tags for Bambu Lab spools.

## Block Overview

Summary of what kind of data is stored in each block. Detailed info for each block is documented below.
| sec | blk | Data |
|-----|-----|----------------------------------------------------------------------------------------|
| 0 | 0 | [Block 0](#block-0) UID and Tag Manufacturer Data |
| 0 | 1 | [Block 1](#block-1) Tray Info Index |
| 0 | 2 | [Block 2](#block-2) Filament Type |
| 0 | 3 | [Block 3](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 1 | 0 | [Block 4](#block-4) Detailed Filament Type |
| 1 | 1 | [Block 5](#block-5) Spool Weight, Color Code, Filament Diameter |
| 1 | 2 | [Block 6](#block-6) Temperatures and Drying Info |
| 1 | 3 | [Block 7](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 2 | 0 | [Block 8](#block-8) X Cam Info, Nozzle Diameter |
| 2 | 1 | [Block 9](#block-9) Tray UID |
| 2 | 2 | [Block 10](#block-10) Spool Width |
| 2 | 3 | [Block 11](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 3 | 0 | [Block 12](#block-12) Production Date/Time |
| 3 | 1 | [Block 13](#block-13) Short Production Date/Time |
| 3 | 2 | [Block 14](#block-14) Filament Length |
| 3 | 3 | [Block 15](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 4 | 0 | [Block 16](#block-16) Extra Color Info |
| 4 | 1 | [Block 17](#block-17) **Unknown** |
| 4 | 2 | **Empty** |
| 4 | 3 | [Block 19](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 5 | 0 | **Empty** |
| 5 | 1 | **Empty** |
| 5 | 2 | **Empty** |
| 5 | 3 | [Block 23](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 6 | 0 | **Empty** |
| 6 | 1 | **Empty** |
| 6 | 2 | **Empty** |
| 6 | 3 | [Block 27](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 7 | 0 | **Empty** |
| 7 | 1 | **Empty** |
| 7 | 2 | **Empty** |
| 7 | 3 | [Block 31](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 8 | 0 | **Empty** |
| 8 | 1 | **Empty** |
| 8 | 2 | **Empty** |
| 8 | 3 | [Block 35](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 9 | 0 | **Empty** |
| 9 | 1 | **Empty** |
| 9 | 2 | **Empty** |
| 9 | 3 | [Block 39](#mifare-encryption-keys) MIFARE encryption keys, Unrelated to Bambu Lab |
| 10-15 | \* | **RSA-2048 Signature** |

The first part of the filament serial number seems to be the Tag UID.

> [!NOTE]
> All numbers are encoded as Little Endian (LE).

## MIFARE Encryption Keys

Every 4th block (eg Sector X, Block 3) contains encryption keys that are part of the MIFARE RFID standard.
This has nothing to do with Bambu Lab's memory format.
All Bambu Lab tags use the same Permission Bits (Access Control)

Example Data:
`AA AA AA AA AA AA PP PP PP PP BB BB BB BB BB BB`

| position | length | type    | Description                                                                    |
| -------- | ------ | ------- | ------------------------------------------------------------------------------ |
| 0 (AA)   | 6      | RAW Bin | A-Key                                                                          |
| 6 (PP)   | 4      | RAW Bin | Permission Bits (Access Control)<br>ALWAYS `87 87  87 69` (hex) for Bambu Tags |
| 10 (BB)  | 6      | RAW Bin | B-Key (always `00 00 00 00 00 00` for Bambu tags)                              |

## Block 0

Note: Block 0 is Read-only. The contents are set by the tag manufacturer.

Example Data:
`AA AA AA AA BB BB BB BB BB BB BB BB BB BB BB BB`

| position | length | type    | Description           |
| -------- | ------ | ------- | --------------------- |
| 0 (AA)   | 4      | string  | Tag UID               |
| 4 (BB)   | 12     | RAW Bin | Tag Manufacturer Data |

## Block 1

Example Data:
`AA AA AA AA AA AA AA AA BB BB BB BB BB BB BB BB`

| position | length | type   | Description                                   |
| -------- | ------ | ------ | --------------------------------------------- |
| 0 (AA)   | 8      | string | Tray Info Index - Material Variant Identifier |
| 8 (BB)   | 16     | string | Tray Info Index - Unique Material Identifier  |

## Block 2

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| position | length | type   | Description   |
| -------- | ------ | ------ | ------------- |
| 0 (AA)   | 16     | string | Filament Type |

## Block 4

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| position | length | type   | description            |
| -------- | ------ | ------ | ---------------------- |
| 0 (AA)   | 16     | string | Detailed Filament Type |

Known Values:

- PLA Basic
- PLA Matte
- PLA Silk
- PLA Galaxy
- PLA Sparkle
- Support for PLA (prev. Support W)
- PLA-CF (prev. PLA Tough)
- PETG Basic

## Block 5

Example Data:
`AA AA AA AA BB BB __ __ CC CC CC CC __ __ __ __`

| position | length | type        | Description                                |
| -------- | ------ | ----------- | ------------------------------------------ |
| 0 (AA)   | 4      | RGBA        | Color in hex RGBA                          |
| 4 (BB)   | 2      | uint16 (LE) | Spool Weight in grams (`E8 03` --> 1000 g) |
| 8 (CC)   | 8      | float (LE)  | Filament Diameter in milimeters            |

## Block 6

Example Data:
`AA AA BB BB CC CC DD DD EE EE FF FF __ __ __ __`

| position | length | type        | Description                             |
| -------- | ------ | ----------- | --------------------------------------- |
| 0 (AA)   | 2      | uint16 (LE) | Drying Temperature in °C                |
| 2 (BB)   | 2      | uint16 (LE) | Drying time in hours                    |
| 4 (CC)   | 2      | uint16 (LE) | Bed Temerature Type **(types unknown)** |
| 6 (DD)   | 2      | uint16 (LE) | Bed Temperature in °C                   |
| 8 (EE)   | 2      | uint16 (LE) | Max Temperature for Hotend in °C        |
| 10 (FF)  | 2      | uint16 (LE) | Min Temperature for Hotend in °C        |

## Block 8

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA BB BB BB BB`

| position | length | type       | description             |
| -------- | ------ | ---------- | ----------------------- |
| 0 (AA)   | 12     | RAW Bin    | X Cam info              |
| 12 (BB)  | 4      | float (LE) | **Nozzle Diameter...?** |

## Block 9

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| position | length | type   | Description |
| -------- | ------ | ------ | ----------- |
| 0 (AA)   | 16     | string | Tray UID    |

## Block 10

Example Data:
`__ __ __ __ AA AA __ __ __ __ __ __ __ __ __ __`

| position | length | type        | Description                                           |
| -------- | ------ | ----------- | ----------------------------------------------------- |
| 4 (AA)   | 2      | uint16 (LE) | Spool Width in mm*100 (`E1 19` --> 6625 --> 66.25mm ) |

## Block 12

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| position | length | type   | Description                                                                |
| -------- | ------ | ------ | -------------------------------------------------------------------------- |
| 0 (AA)   | 16     | string | Production Date and Time in ASCII (`<year>_<month>_<day>_<hour>_<minute>`) |

## Block 13

Example Data:
`AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA`

| position | length | type   | Description                        |
| -------- | ------ | ------ | ---------------------------------- |
| 0 (AA)   | 16     | string | **Short Production Date/Time...?** |

## Block 14

Example Data:
`__ __ __ __ AA AA __ __ __ __ __ __ __ __ __ __`

| position | length | type        | Description                       |
| -------- | ------ | ----------- | --------------------------------- |
| 4 (AA)   | 2      | uint16 (LE) | **Filament length in meters...?** |

## Block 16

Example Data:
`AA AA BB BB CC CC CC CC __ __ __ __ __ __ __ __`

| position | length | type        | Description                        |
| -------- | ------ | ----------- | ---------------------------------- |
| 0 (AA)   | 2      | uint16 (LE) | Format Identifier                  |
| 2 (BB)   | 2      | uint16 (LE) | Color Count                        |
| 4 (CC)   | 4      | RGBA        | Second color in _reverse_ hex ABGR |

Known Format Identifiers:

- 00 00 = Empty
- 02 00 = Color Info

## Block 17

Example Data:
`AA AA __ __ __ __ __ __ __ __ __ __ __ __ __ __`

| position | length | type        | Description |
| -------- | ------ | ----------- | ----------- |
| 0 (AA)   | 2      | **Unknown** | **Unknown** |
