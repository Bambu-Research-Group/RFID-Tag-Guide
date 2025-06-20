# Creality RFID Tag Documentation

This contains documentation for the data that is contained in the RFID tags for Creality RFID spools.

The data format has been primarily researched in the following Reddit thread: https://www.reddit.com/r/Creality_k2/comments/1h5egkv/introducing_rfid_for_cfs_an_android_app_for/?share_id=Vu3JVyAm0wjQzBbbYK9Yp&utm_name=androidcss

## Overview

The data in the tags for Creality RFID spools is stored in blocks 4 through 6. The data is ASCII-encoded and stored in a byte-like format.

## Data

Example Data: 7A3 24120 0A21 01001 #000000 016500 000100000000000000

`AAA BBBBB CCCC DDDDD #EEEEEE FFFFFF GGGGGGGGGGGGGGGGGG`

| position | length | type    | Description                 |
| -------- | ------ | ------- | --------------------------- |
| 0 (A)    | 3      | hex     | Batch number                |
| 3 (B)    | 5      | date    | Manufacturing date as YYMDD |
| 8 (C)    | 4      | hex     | Supplier ID                 |
| 12 (D)   | 5      | hex     | Material ID                 |
| 17 (E)   | 6      | RGB     | Material Color              |
| 23 (F)   | 5      | hex     | Spool ID...?                |
| 28 (G)   | 18     | unknown | Unknown                     |
