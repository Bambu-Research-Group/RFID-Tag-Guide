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

| position | length | type    | Description                                                            |
| -------- | ------ | ------- | ---------------------------------------------------------------------- |
| 0 (AA)   | 6      | RAW Bin | A-Key                                                                  |
| 6 (PP)   | 4      | RAW Bin | Permission Bits (Access Control) (always `87 87 87 69` for Bambu Tags) |
| 10 (BB)  | 6      | RAW Bin | B-Key (always `00 00 00 00 00 00` for Bambu tags)                      |

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

| position | length | type   | Description                           |
| -------- | ------ | ------ | ------------------------------------- |
| 0 (AA)   | 8      | string | Tray Info Index - Material Variant ID |
| 8 (BB)   | 8      | string | Tray Info Index - Material ID         |

The material IDs all start with the letters "GF" (so far), and the material variant IDs start with the last three letters of the material ID. For example, a variant ID of `A50-K0` is associated with a material ID of `GFA50`. We'll refer to the second part (after the hyphen) of the variant IDs as "color IDs".

Known Material IDs:

- GFA00: Bambu PLA Basic
- GFA01: Bambu PLA Matte
- GFA02: Bambu PLA Metal
- GFA03: Bambu PLA Impact
- GFA05: Bambu PLA Silk
- GFA07: Bambu PLA Marble
- GFA08: Bambu PLA Sparkle
- GFA09: Bambu PLA Tough
- GFA11: Bambu PLA Aero
- GFA12: Bambu PLA Glow
- GFA13: Bambu PLA Dynamic
- GFA15: Bambu PLA Galaxy
- GFA50: Bambu PLA-CF
- GFB00: Bambu ABS
- GFB01: Bambu ASA
- GFB02: Bambu ASA-Aero
- GFB50: Bambu ABS-GF
- GFB51: Bambu ASA-CF
- GFB60: PolyLite ABS
- GFB61: PolyLite ASA
- GFB98: Generic ASA
- GFB99: Generic ABS
- GFC00: Bambu PC
- GFC99: Generic PC
- GFG00: Bambu PETG Basic
- GFG01: Bambu PETG Translucent
- GFG02: Bambu PETG HF
- GFG50: Bambu PETG-CF
- GFG60: PolyLite PETG
- GFG96: Generic PETG HF
- GFG97: Generic PCTG
- GFG98: Generic PETG-CF
- GFG99: Generic PETG
- GFL00: PolyLite PLA
- GFL01: PolyTerra PLA
- GFL03: eSUN PLA+
- GFL04: Overture PLA
- GFL05: Overture Matte PLA
- GFL06: Fiberon PETG-ESD
- GFL50: Fiberon PA6-CF
- GFL51: Fiberon PA6-GF
- GFL52: Fiberon PA12-CF
- GFL53: Fiberon PA612-CF
- GFL54: Fiberon PET-CF
- GFL55: Fiberon PETG-rCF
- GFL95: Generic PLA High Speed
- GFL96: Generic PLA Silk
- GFL98: Generic PLA-CF
- GFL99: Generic PLA
- GFN03: Bambu PA-CF
- GFN04: Bambu PAHT-CF
- GFN05: Bambu PA6-CF
- GFN06: Bambu PPA-CF
- GFN08: Bambu PA6-GF
- GFN96: Generic PPA-GF
- GFN97: Generic PPA-CF
- GFN98: Generic PA-CF
- GFN98: Generic PA-CF P1P
- GFN99: Generic PA
- GFN99: Generic PA P1P
- GFP95: Generic PP-GF
- GFP96: Generic PP-CF
- GFP97: Generic PP
- GFP98: Generic PE-CF
- GFP99: Generic PE
- GFR98: Generic PHA
- GFR99: Generic EVA
- GFS00: Bambu Support W
- GFS01: Bambu Support G
- GFS02: Bambu Support for PLA
- GFS03: Bambu Support for PA/PET
- GFS04: Bambu PVA
- GFS05: Bambu Support for PLA/PETG
- GFS06: Bambu Support for ABS
- GFS97: Generic BVOH
- GFS98: Generic HIPS
- GFS99: Generic PVA
- GFT01: Bambu PET-CF
- GFT02: Bambu PPS-CF
- GFT97: Generic PPS
- GFT98: Generic PPS-CF
- GFU00: Bambu TPU 95A HF
- GFU01: Bambu TPU 95A
- GFU02: Bambu TPU for AMS
- GFU98: Generic TPU for AMS
- GFU99: Generic TPU
- GFU99: Generic TPU P1P

Known Color IDs:

- A0:
  - For A00: Orange (#FF671FFF)
  - For G00: Orange (#FF6A13FF)
- B3: Marine Blue (#0078BFFF)
- B4: Blue (#0085ADFF)
- B7: Royal Purple (#483D8BFF)
- D0: Grey (#8E9089FF)
- D1: Silver (#A6A9AAFF)
- G1:
  - For A15: Nebulae (#424379FF)
  - Others: Green (#00AE42FF)
- G6: Green (#00AE42FF)
- K0, K1: Black (#000000FF)
- P0: Purple (#D6ABFF80)
- T3: Neon City (Blue-Magenta) (#0047BBFF / #BB22A3F)
- W0, W1: White (#FFFFFFFF)
- W2: Ivory White (#FFFFFFFF)
- Y3: Bronze (#84754EFF)


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
