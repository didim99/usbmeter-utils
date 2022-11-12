#! /usr/bin/python3

import os

from common import *

"""
    WTM format specification (WITRN Meter v4.6).
    Measurement frequency: 100 samples per second.
    All multi-byte values stored in Little-endian.
    File structure:

      Offset     Size         Unit     Description

    - Header: 16 bytes ----------------------------------------------
      0x00 (0)   16 (string)           "wtm1903 " in UTF16-LE

    - Data section: 7 bytes * point count ---------------------------
      0x00 (0)   2  (int16)   1 mV     USB V_BUS voltage
      0x02 (2)   2  (int16)   1 mA     USB V_BUS current
      0x04 (4)   1  (int8)    100 mV   USB D- voltage
      0x05 (5)   1  (int8)    100 mV   USB D+ voltage
      0x06 (6)   1  (int8)    1 °C/°F  External temperature
"""

src_dir = "src"
out_dir = "out"
src_ext = ".wtm"
out_ext = ".csv"
header = 'wtm1903 '

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

        print(f"Processing: {name}...")
        out_name = rreplace(name, src_ext, out_ext)

        src_file = open(os.path.join(src_dir, name), "rb")
        out_file = open(os.path.join(out_dir, out_name), "w")

        if add_header:
            voltage_res = 'V' if use_float else 'mV'
            current_res = 'A' if use_float else 'mA'
            out_file.write('time (HH:MM:SS:MS),voltage ({}),current ({}),D+ ({}), D- ({}),temp (deg)'
                           .format(voltage_res, current_res, voltage_res, voltage_res))
            out_file.write('\n')

        try:
            buf = src_file.read(len(header) * 2)  # UTF16-LE
            buf = buf.decode('utf-16le')
            if buf != header:
                print("Incorrect header")
                raise LookupError

            ts = 0
            count = 1
            while True:
                voltage = read_int(src_file, 2)
                if voltage is None:
                    break
                current = read_int(src_file, 2)
                data_neg = read_int(src_file, 1) * 100
                data_pos = read_int(src_file, 1) * 100
                temp = read_int(src_file, 1)

                if temp == -72:
                    temp = 'null'

                if use_float:
                    voltage /= 1000
                    current /= 1000
                    data_neg /= 1000
                    data_pos /= 1000

                strtime = ts2str(ts)
                # print(ts, voltage, current, data_pos, data_neg, temp)
                fmt_main = '{:.3f}' if use_float else '{:d}'
                fmt_sub = '{:.1f}' if use_float else '{:d}'
                fmt_line = "{},%s,%s,%s,%s,{}" % (fmt_main, fmt_main, fmt_sub, fmt_sub)
                line = fmt_line.format(strtime, voltage, current, data_pos, data_neg, temp)

                out_file.write(line)
                out_file.write('\n')
                # print(line)

                count += 1
                ts += 10

            print(f"Total points: {count-1} ({ts2str(ts)})")
            files += 1
        except LookupError:
            pass

        src_file.close()
        out_file.close()

    print(f"Total files processed: {files}")
