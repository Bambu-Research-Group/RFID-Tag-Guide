# OpenTag: Open Source RFID Standard
RFID is becoming more prevalent, with each company launching their own RFID system that is incompatible with the rest.
OpenTag strives to be a standard that allows RFID tags to work across 3D Printer Brands, Filament Brands, and Accessory Brands.

OpenTag aims to standardize the following:
* **Hardware** - The specific underlying RFID technology
* **Mechanical Requirements** - Positioning of tag on the spool
* **Data Structure** - What data should be stored on the RFID tag, and how that data should be formatted
* **Web API** - How extended data should be formatted when an optional online spool lookup is requested


<img src="images/SpoolTag.jpg" height=300>

# Table of Contents
* [Backers](#backers)
* [Why RFID](#why-rfid)
* [OpenTag Standards](#opentag-standards)
    * [Hardware Standard](#hardware-standard)
    * [Mechanical Standard](#mechanical-standard)
    * [Data Structure Standard](#data-structure-standard)
    * [Web API Standard](#web-api-standard)
* [Add RFID support to your printer](#add-rfid-support-to-your-printer)
* [OpenTag Consortium](#opentag-consortium)
    * [Voting Members](#voting-members)
    * [Non-Voting Members](#non-voting-members)
* [Previous Considerations](#previous-considerations)
    
# Backers
These are companies that are implementing Open 3D-RFID into their printers, filament, add-ons, etc.  If you would like to join this list, please open an Issue on GitHub.
* Filament Manufacturers (Sorted by date backed):
  * [Polar Filament](https://polarfilament.com)
  * [3D Fuel](https://www.3dfuel.com/)
  * [Ecogenesis Biopolymers](https://ecogenesisbiopolymers.com)
  * [Numakers](https://numakers.com/)
  * [American Filament](https://americanfilament.us)
* Printers + Hardware:
  * [OpenSpool](https://www.youtube.com/watch?v=ah7dm-dtQ5w) ([GitHub Source](https://github.com/spuder/OpenSpool))
  * [Cosmyx](https://www.cosmyx3d.com/)
  * [Distrifab](https://distrifab.fr/)

# Why RFID?
What is the benefit of adding RFID chips to filament?

* AMS / Multi-Material Printers
    * **Color + Material ID:** Simplifying the painting process!  AMS units can automatically detect what filament is loaded up in each slot. This also adds a sanity check before you start printing to make sure you don't end up with a print in the wrong color.
* High-Speed Printing
    * **Advanced Filament Data:** Tags can store advanced per-spool printing data, such as printing/bed temps, melt-flow index, retration, and even filament diameter graphs.  This would make the transition simpler when using filaments from different brands.
* HueForge
    * **Transmission distance + Hex**: Each spool can have a unique TD and color. Saving this data on the spool allows for more accurate tuning, and less math for the consumer
* Every Printer
    * **Filament Remaining Estimation:** Using the RFID tag as an encoder, printers can measure how long it takes for one rotation of a spool of filament, and use this to estimate how much filament is remaining.
    * **Print Profiles**: Each spool can contain print/bed temps, as well as other settings like retraction settings. This makes it much easier to use different brands/colors/materials without worrying about creating a bunch of different slicer profiles.

# Add RFID support to your printer
This standard was designed to be simple to implement in firmware. You will need to add custom firmware and potentially an RFID reader (if your printer doesn't already have one).

RFID support can theoretically be added to any printer using off-the-shelf RFID Modules such as the PN532 (as low as $3). This module communicates over SPI.

<img src="images/PN532-Reader-Blue.png" width=200>
<img src="images/PN532-Reader-Red.png" width=200>

Did you make a design to add RFID to your printer? Let us know so we can link to it here!  Designs can be 3D models, or firmware.

# OpenTag Standards
## Hardware Standard
NFC NTAG216: 13.56 MHz 888-byte tags

<img src="images/mifareclassicsticker.jpg" width="200">

NTAG216 tags are cheap and common. They allow 888 bytes of data, which is plenty of space to store required information. NFC tags such as NTAG216 can be read/written with smartphones. 13.56 MHz RFID modules are plentiful, low-cost and Arduino-compatible, allowing for easy integration.

NFC NTAG216 was chosen over MIFARE 1K Classic tags, which is what the Bambu AMS uses, for the following reasons:
* More memory (NTAG216: 888-bytes usable, MF1K: 768-bytes usable)
* Smartphone Support: NTAG216 can be read from smartphones, while MF1K requires a dedicated reader

## Mechanical Standard
* Tag placement: The center should be 56.0mm away from the center of the spool (see pic)
* The tag should never be more than 4.0mm away from the external surface of the spool
  * For spool sides thicker than 4mm, there must be a cutout to embed the tag, or the tag should be fixed to the outside of the spool
* Two tags should be used, one on each end of the spool, directly across from each other

<img src="images/TagLocation.png" width="400">

## Data Structure Standard

This is a list of data that will live on the RFID chip, separated into required and optional data.  All REQUIRED data must be populated to be compliant with this open source RFID protocol.

NTAG216 tags have 888 bytes of usable memory.

### Required Data
All chips MUST contain this information, otherwise they are considered non-compliant
| Field | Data Type | Size (bytes) | Example | Description
|-------------|---------------|------------|----|-----|
| Tag Version | Int | 2 | `1234` | RFID tag data format version to allow future compatibility in the event that the data format changes dramatically. Stored as an int with 3 implied decimal points. Eg `1000` -> `version 1.000`|
| Filament Manufacturer | String | 16 | `"Polar Filament"` | String representation of filament manufacturer.  16 bytes is the max data length per-block. Longer names will be abbreviated or truncated |
| Material Name | String | 16 | `"PLA"` or `"Glass-Filled PC"` | Material name in plain text |
| Color Name | String | 32 | `"Blue"` or `"Electric Watermellon"` | Color in plain text. Color spans 2-blocks |
| Diameter (Target) | Int | 2 | `1750` or `2850` | Filament diameter (target) in µm (micrometers) Eg "1750" -> "1.750mm"
| Weight (Nominal, grams) | Int |  2 | `1000` (1kg), `5000` (5kg), `750` (750g) | Filament weight in grams, excluding spool weight. This is the TARGET weight, eg "1kg".  Actual measured weight is stored in a different field.
| Print Temp (C)| Int | 2 | `210` (C), `240` (C) | The recommended print temp in degrees-C
| Bed Temp (C) | Int | 2 | `60` (C), `80` (C) | The recommended bed temp in degrees-C |
| Density | Int | 2 | `1240` (1.240g/cm<sup>3</sup>), `3900` (3.900g/cm<sup>3</sup>) | Filament density, measured in µg (micrograms) per cubic centimeter.

### Optional Data
This is additional data that not all manufacturers will implement, typically due to technological restrictions. These fields are populated if available.  All unused fields must be populated with "-1" (all 1's in binary, eg 0xFFFFFFFFFFFFFFFF)

| Field | Data Type | Size (bytes) | Example | Description
|-------------|---------------|------------|----|-----|
| Serial Number / Batch ID | String | 16 | `"1234-ABCD"`, `"2024-01-23-1234"` | An identifier to represent a serial number or batch number from manufacturing. Stored as a string, and this format will vary from manufacturer to manufacturer |
| Manufacture Date | Int | 4 | `20240123` (Jan 23rd, 2024) | Date code in YYYYMMDD format, stored as a 32-bit integer |
| Manufacture Time | Int | 3 | `103000` (10:30am), `152301` (3:23:01pm)  | 24-hour time code in HHMMSS format (Hour, Minumte, Second), specifying UTC.
| Spool Core Diameter (mm) | Int | 1 | `100` (mm), `80` (mm) | The diameter of the spool core, which is the part that the filament is wound around. This diameter is to estimate remaining filament by treating the tag as an encoder, and measuring how long it takes for one rotation of a spool.
| MFI (Melt-flow index) | TBD | TBD | TBD | Format TBD. The melt-flow index describes how "melty" plastic is.  Meltier plastics can usually print faster.  Formula is somewhat complex, and often measured at different temperatures.  For example Corbion LX175 melt flow index is `MFI(210°C/2.16kg) = 6g/10min`, and `MFI(190°C/2.16kg) = 3g/10min`
| Tolerance (Measured) | Int | 1 | `20` (±0.020mm), `55` (±0.055mm) | Actual tolerance, measured in µm (micrometers). This field is unique to each spool, and should only be populated if per-spool tolerances are measured and recorded during manufacturing. This is not a TARGET tolerance, this is ACTUAL.  If not recorded, leave undefined (0xFF)
| Additional Data URL | String | 32 | `pfil.us?i=8078-RQSR` | URL to access additional data in JSON format. This data may be unique to this spool, or just general info about this material.  All urls must be https, and the "https" at the beginning is implied. Eg `pfil.us?i=8078-RQSR` becomes `https:pfil.us?i=8078-RQSR`, formatted this way to save memory.
| Empty Spool Weight (g) | Int | 2 | `105` (105 grams) | Weight of the empty spool in grams. This can be used to calculate how much filament is remaining on each spool
| Filament Weight (Measured) | Int | 2 | `1002` (1002 grams) | ACTUAL weight of the filament, excluding empty-spool weight. Measured after filament manufacturing.  This is not the target weight (eg 1kg) but rather the actual weighed result (eg 1.002kg).
| Filament Length (Measured) | Int | 2 | `336` (336 meters) | ACTUAL length of filament measured in meters.  This is unique to each spool.
| TD (Transmission Distance) | Int | 2 | `2540` (2.540mm) | Transmission Distance in µm (micrometers). Transmission distance is the distance at which no light can pass through the filament.  See the HueForge project for more details |
| Color Hex | Int | 3 | `0xffa64d` (Light orange color) | Color hexcode. Hex is a 3-byte number in the format 0xRRGGBB (Red, Green, Blue, one byte each) |
| Max Dry Temp (C) | Int | 1 | `55` (55C), `50` (50C) Maximum drying temperature in Degrees-C. Drying above this temperature can damage the filament

### Web API Standard
Some tags can contain extended data that doesn't fit or doesn't belong on the RFID tag itself.  One example is a diameter graph, which is too much data to be stored within only 888 bytes of memory.

These complex variables can be looked up using the "web API" URL that is stored on the RFID tag.

The format of this data should be JSON.
The exact contents of this data are still open to discussion, and it is not required to launch the OpenTag standard.  The web API can be implemented in the future without affecting the launch of OpenTag. 

## OpenTag Consortium
The OpenTag Consortium is a collaborative group of 3D printing companies, hobbyists, RFID experts, and other stakeholders committed to maintaining and evolving the OpenTag RFID standard specification. The consortium operates under a structured membership model, ensuring a balance of inclusivity and effective decision-making.

### Voting Members
Voting members play a critical role in the governance of the OpenTag standard. They have the authority to vote on proposals related to modifying the specification. Their decisions shape the future direction of OpenTag, ensuring it meets the needs of the community and industry.

To maintain fairness and inclusivity, the voting seats are divided equally between:

* Industry Representatives: Voting members representing companies and organizations involved in 3D printing, RFID, and related fields.
* Community Representatives: Voting members from the broader community, including hobbyists, independent developers, and RFID experts.

This balanced structure ensures that no single group dominates decision-making, fostering a standard that reflects the interests of both professional and grassroots contributors.

### Non-Voting Members
Non-voting members are integral to the consortium's ecosystem, contributing ideas and fostering collaboration. While they cannot directly vote on proposals, they can:

* **Propose Changes**: Submit new ideas or modifications to the specification, which voting members will evaluate and vote on.
* **Elect Voting Members**: Participate in elections to select voting members through a popular vote, ensuring representation aligns with the community’s vision.
This dual-tier structure enables broad participation while maintaining an efficient and organized decision-making process.


## Previous Considerations
These are topics that are commonly brought up when learning about OpenTag.  Below is a quick summary of each topic, and why we decided to settle on the standards we defined.

* NTAG216 vs MIFARE:
    * NTAG216 is compatible with smartphones and has slightly more usable memory than MIFARE tags
    * MIFARE uses about 25% of memory to encrypt data, preventing read/write operations, which is not applicable for OpenTag because of the open-source nature
* JSON vs Memory Map:
    * Formats such as JSON (human-readable text) takes up considerably more more memory than memory mapped.  For example, defining something like Printing Temperature would be `PrintTemp:225` which is 13 bytes, instead of storing a memory mapped 2-byte number.  Tokens could be reduced, but that also defeats the purpose of using JSON in the first place, which is often for readability.
    * NTAG216 tags only have 888 bytes of usable memory, which would be eaten up quickly
* Lookup Tables
    * OpenTag does NOT use lookup tables, which would be too difficult to maintain due to the decentralized nature of this standard.
    * Lookup tables can quickly become outdated, which would require regular updates to tag readers to make sure they've downloaded the most recent table.
    * Storing lookup tables consumes more memory on the device that reads tags
    * On-demand lookup (via the internet) would require someone to host a database. Hosting this data would have costs associated with it, and would also put the control of the entire OpenTag format in the hands of a single person/company
    * Rather than representing data as a number (such as "company #123 = Example Company), the plain-text company name should be used instead
