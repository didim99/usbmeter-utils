#! /usr/bin/python3

import os

from common import *

"""
    CFN format specification (FNIRSI toolbox v0.0.6).
    All multi-byte values stored in Little-endian.
    File structure:

      Offset     Size         Unit     Description

    - Header: 86 bytes (default setup) ------------------------------
      0x00 (0)   8  (double)  1 s/s    Sample rate

      0x08 (8)   14 (???)              Unknown data

      0x16 (22)  7  (???)              Block header, unknown data
      0x1D (29)  8  (double)  1 V      Max registered USB V_BUS voltage
      0x25 (37)  8  (double)  1 V      Min registered USB V_BUS voltage
      0x2D (45)  7  (???)              Block header, unknown data
      0x34 (52)  8  (double)  1 A      Max registered USB V_BUS current
      0x3C (60)  8  (double)  1 A      Min registered USB V_BUS current

      0x44 (68)  14 (???)              Unknown data

      0x52 (82)  4  (int32)            Count of data points

    - Data section: 40 bytes * point count (default setup) ----------
      0x00 (0)   8  (double)  1 sec    Time offset
      0x08 (8)   8  (double)  1 V      USB V_BUS voltage
      0x10 (16)  8  (double)  1 A      USB V_BUS current
      0x18 (24)  8  (double)  1 Ah     Accumulated capacity
      0x20 (32)  8  (double)  1 Wh     Accumulated energy
"""

src_dir = "src"
out_dir = "out"
src_ext = ".cfn"
out_ext = ".csv"

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
        print(samplerate)

        buf = src_file.read(14)  # unknown
        print(hex_spaced(buf))

        seplen = 7
        buf = src_file.read(seplen)
        print(hex_spaced(buf))

        v_max = read_float(src_file, 8)
        v_min = read_float(src_file, 8)
        # print("V min:", v_min, "V max:", v_max)

        buf = src_file.read(seplen)  # unknown
        print(hex_spaced(buf))

        i_max = read_float(src_file, 8)
        i_min = read_float(src_file, 8)
        # print("I min:", i_min, "I max:", i_max)

        buf = src_file.read(37-16-seplen)  # unknown
        pts_count = read_int(src_file, 4)

        fsize = os.stat(os.path.join(src_dir, name)).st_size
        # print(fsize, pts_count)

        for index in range(pts_count):
            time = read_float(src_file, 8)
            voltage = read_float(src_file, 8)
            current = read_float(src_file, 8)
            capacity = read_float(src_file, 8)
            energy = read_float(src_file, 8)

            # print(time, voltage, current, capacity * 1000, energy * 1000)

        src_file.close()
        out_file.close()

    print(f"Total files processed: {files}")
