#! /usr/bin/python3

import os

from common import *

"""
    CFN format specification (FNIRSI toolbox v0.0.6):

    86 bytes header
      size - value, format
      8 bytes - sample rate (float)

      14 bytes - unknown

      7 bytes - block header, unknown data
      8 bytes - max voltage (float)
      8 bytes - min voltage (float)

      7 bytes - block header, unknown data
      8 bytes - max current (float)
      8 bytes - min current (float)

      14 bytes - unknown
      4 bytes - count of data points (int)

    40 bytes / point (default setup)
      8 bytes - time (float)
      8 bytes - voltage (float)
      8 bytes - current (float)
      8 bytes - capacity (float)
      8 bytes - energy (float)
    
    All multi-byte values stored in Little-endian
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
