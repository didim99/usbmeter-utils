#! /usr/bin/python3

import os

from common import *

"""
    CFN format specification (FNIRSI toolbox v0.0.6).
    All multi-byte values stored in Little-endian.
    File structure:

      Offset     Size         Unit     Description

    - Header: 22 bytes ----------------------------------------------
      0x00 (0)   8  (double)  1 s/s    Sample rate
      0x08 (8)   4  (int32)   1 mA     Start current condition
      0x0B (12)  4  (int32)   1 mA     Stop current condition
      0x10 (16)  4  (int32)   1 s      Stop time condition
      0x14 (20)  2  (int16)            Channel count

    - Channel descriptors: ch_count * 7(23) bytes -------------------

      0x00 (0)   2  (int16)            Channel type (see below)
      0x02 (2)   4  (???)              Unknown data *
      0x06 (6)   1  (bool)             Min/Max flag
      -------------- if Min/Max flag == 0x01 (true) -----------------
      0x07 (7)   8  (double)  various  Max registered value
      0x0e (15)  8  (double)  various  Min registered value

    - Data section header: 4 bytes ---------------------------------
      0x00 (0)   4  (int32)            Count of data points

    - Data section: ch_count * pts_count * 8 bytes ------------------
      0x00 (0)   8  (double)  1 sec    Time offset
      0x08 (8)   8  (double)  various  Channel 1 value
      ...
      0x30 (48)  8  (double)  various  Channel N value

      Channels in data section arranged same as
      channel descriptors in file header
      --------------------------------------------------------------

      Channel types:
      0x00: USB V_BUS voltage (x 1V)
      0x01: USB V_BUS current (x 1A)
      0x02: USB D+ voltage (x 1V)
      0x03: USB D- voltage (x 1V)
      0x04: Power (x 1W)
      0x05: Accumulated capacity (x 1Ah)
      0c06: Accumulated energy (x 1Wh)

      * - byte sequence seems constant dependent from channel type
"""

src_dir = "src"
out_dir = "out"
src_ext = ".cfn"
out_ext = ".csv"

debug = False
add_header = True

channel_types = {
    0: {"symbol": "V", "name": "Voltage"},
    1: {"symbol": "I", "name": "Current"},
    2: {"symbol": "D+", "name": "D+"},
    3: {"symbol": "D-", "name": "D-"},
    4: {"symbol": "P", "name": "Power"},
    5: {"symbol": "C", "name": "Capacity"},
    6: {"symbol": "E", "name": "Energy"}
}

if __name__ == '__main__':
    cwd = os.getcwd()
    src_dir = os.path.join(cwd, src_dir)
    out_dir = os.path.join(cwd, out_dir)

    files = 0
    for name in os.listdir(src_dir):
        if src_ext != os.path.splitext(name)[1]:
            continue

        print(f"Processing: {name}")
        out_name = rreplace(name, src_ext, out_ext)

        src_file = open(os.path.join(src_dir, name), "rb")
        out_file = open(os.path.join(out_dir, out_name), "w")

        # ---------------------------------------------------------

        samplerate = read_float(src_file, 8)
        start_curr = read_int(src_file, 4)
        stop_curr = read_int(src_file, 4)
        stop_time = read_int(src_file, 4)
        ch_count = read_int(src_file, 2)

        tmp_str = f"# {samplerate} sps, start/stop: {start_curr}/{stop_curr}" + \
                  f" mA ({stop_time} s), channels: {ch_count}"
        if add_header:
            out_file.write(tmp_str + "\n")
        if debug:
            print(tmp_str)

        csv_header = ["Time"]
        min_max = []

        for i in range(ch_count):
            ch_type = read_int(src_file, 2)
            ch_name = channel_types[ch_type]
            csv_header.append(ch_name["name"])

            buf = src_file.read(4)  # unknown
            if debug:
                print(f"{ch_name['symbol']:>2}:", hex_spaced(buf))

            has_min_max = read_int(src_file, 1)
            if has_min_max == 1:
                v_max = read_float(src_file, 8)
                v_min = read_float(src_file, 8)
                tmp_str = f"# {ch_name['symbol']} min: {v_min}, " + \
                          f"{ch_name['symbol']} max: {v_max}" + "\n"
                min_max.append(tmp_str)

        if add_header:
            out_file.writelines(min_max)
            csv_header = ",".join(csv_header)
            out_file.write(csv_header + "\n")

        pts_count = read_int(src_file, 4)
        fsize = os.stat(os.path.join(src_dir, name)).st_size
        print(f"  Total points: {pts_count} ({fsize} bytes)")

        for index in range(pts_count):
            values = []
            for i in range(ch_count+1):
                values.append(read_float(src_file, 8))
            if debug:
                print(values)
            values = ",".join([f"{v:.8f}" for v in values])
            out_file.write(values + "\n")

        files += 1

        # ---------------------------------------------------------

        src_file.close()
        out_file.close()

    print(f"Total files processed: {files}")
