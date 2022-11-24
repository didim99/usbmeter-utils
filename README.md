# USB-Meter utils

This repo contains utilities for WITRN and FNIRSI USB-meters
software and some file formats specifications (see source code).

## WITRN

* VAT (offline memory dump) to CSV converter
* WTM (realtime record log) to CSV converter
* CSV re-sampler and re-formatter

Scripts based on files collected from WITRN U2p
USB-tester (firmware v7.8) via WITRN Meter v4.6.

## FNIRSI

* CFN (realtime record log & offline memory dump) to CSV converter

Scripts based on files collected from FNIRSI FNB48/FNB58
USB-tester (firmware v2.60) and FNIRSI Toolbox v0.0.6.

## How to use?

1. Clone or download repo in `some-dir`.
2. Create directories `some-dir/src` and `some-dir/out`.
3. Place your source files in `some-dir/src` and run related script.
4. Processed files will be placed in `some-dir/out`
   with same name and `.csv` extension.
5. Done!
