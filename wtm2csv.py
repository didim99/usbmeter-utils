import os

from common import *

"""
    WTM format specification (WITRN Meter v4.6):
    
    File structure
    Measurement frequency: 100 samples per second
    16 bytes - header, 'wtm1903 ' in UTF16-LE
    Data records, 7 bytes for each record:
        size - value, format, precision
        2 bytes - voltage, sighed int, 1 mV
        2 bytes - current, sighed int, 1 mA
        1 byte - D- voltage, sighed int, 100 mV
        1 byte - D+ voltage, sighed int, 100 mV
        1 byte - ext. temp, sighed int, 1 degC/degF
    all multi-byte values stored in Little-endian
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
    src_dir = cwd + "/" + src_dir
    out_dir = cwd + "/" + out_dir

    files = 0
    for name in os.listdir(src_dir):
        if src_ext != os.path.splitext(name)[1]:
            continue

        print(f"Processing: {name}...")
        out_name = rreplace(name, src_ext, out_ext)

        src_file = open(src_dir + "/" + name, "rb")
        out_file = open(out_dir + "/" + out_name, "w")

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

                strtime = timestr(ts)
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

            print(f"Total points: {count} ({timestr(ts)})")
            files += 1
        except LookupError:
            pass

        src_file.close()
        out_file.close()

    print(f"Total files processed: {files}")
