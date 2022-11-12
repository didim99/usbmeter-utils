#! /usr/bin/python3

import os
import re

from common import *

"""
    WITRN U2p: maximum 352 points x 5 bytes each.
    Total 1760 bytes for internal offline storage.

    VAT format specification (WITRN Meter v4.6).

    File name: YYYYMMDD_HHIISS_CCC.vat
        Y - Year
        M - Month (01-12)
        D - Day of month (01-31)
        H - Hour (00-23)
        I - mInutes (00-59)
        S - Seconds (00-59)
        C - total Count of recorded points in file

    all multi-byte values stored in Little-endian.
    File structure:

      Offset     Size         Unit     Description

    - Header: 2 bytes -----------------------------------------------
      0x00 (0)   1 (int8)              Constant 0x05, unknown
      0x01 (1)   1 (int8)     1 hour   Total record time

    - Data section: 5 bytes * point count ---------------------------
      0x00 (0)   2  (int16)   1 mV     USB V_BUS voltage
      0x02 (2)   2  (int16)   1 mA     USB V_BUS current
      0x04 (4)   1  (int8)    1 °C/°F  External temperature
"""

src_dir = "src"
out_dir = "out"
src_ext = ".vat"
out_ext = ".csv"
header = b'\x05'
max_points = 352

use_float = True
add_header = False

if __name__ == '__main__':
    cwd = os.getcwd()
    src_dir = os.path.join(cwd, src_dir)
    out_dir = os.path.join(cwd, out_dir)

    files = 0
    for name in os.listdir(src_dir):
        if src_ext != os.path.splitext(name)[1]:
            continue

        print(f"Processing: {name}")
        total = int(re.split('[_.]', name)[2])
        out_name = rreplace(name, src_ext, out_ext)

        src_file = open(os.path.join(src_dir, name), "rb")
        out_file = open(os.path.join(out_dir, out_name), "w")

        if add_header:
            voltage_res = 'V' if use_float else 'mV'
            current_res = 'A' if use_float else 'mA'
            out_file.write('time (HH:MM:SS:MS),voltage ({}),current ({}),temp (deg)'
                           .format(voltage_res, current_res))
            out_file.write('\n')

        try:
            buf = src_file.read(len(header))
            if buf != header:
                print("Incorrect header")
                raise LookupError

            buf = src_file.read(1)
            hours = int.from_bytes(buf, 'little')
            dt = 3600 * 1000 * hours // max_points
            print(f"{total} points, record time: {hours} hours")

            ts = 0
            count = 1
            while count <= total:
                voltage = read_int(src_file, 2)
                current = read_int(src_file, 2)
                temp = read_int(src_file, 1)

                if temp == -72:
                    temp = 'null'

                if use_float:
                    voltage /= 1000
                    current /= 1000

                strtime = ts2str(ts)
                # print(count, ts, voltage, current, temp)
                fmt_main = '{:.3f}' if use_float else '{:d}'
                fmt_line = "{},%s,%s,{}" % (fmt_main, fmt_main)
                line = fmt_line.format(strtime, voltage, current, temp)

                out_file.write(line)
                out_file.write('\n')
                # print(line)

                count += 1
                ts += dt

            print(f"Total points: {count-1} ({ts2str(ts)})")
            files += 1
        except LookupError:
            pass

        src_file.close()
        out_file.close()

    print(f"Total files processed: {files}")
