import os

from common import rreplace, hex_spaced

"""
    WTM format specification (WITRN Meter v4.6):
    
    file structure
    Measurement frequency: 100 samples per second
    16 bytes - header, 'wtm1903 ' in UTF16-LE
    Data records, 7 bytes for each record:
        2 bytes - voltage
        2 bytes - current
        1 byte - D- voltage
        1 byte - D+ voltage
        1 byte - ext. temp
"""

src_dir = "src"
out_dir = "out"
src_ext = ".wtm"
out_ext = ".csv"
header = 'wtm1903 '
point_size = 7  # bytes in sequence

if __name__ == '__main__':
    cwd = os.getcwd()
    src_dir = cwd + "/" + src_dir
    out_dir = cwd + "/" + out_dir

    for name in os.listdir(src_dir):
        if src_ext != os.path.splitext(name)[1]:
            continue

        print(f"Processing: {name}")
        out_name = rreplace(name, src_ext, out_ext)
        src_file = open(src_dir + "/" + name, "rb")
        out_file = open(out_dir + "/" + out_name, "w")

        try:
            buf = src_file.read(len(header) * 2)  # UTF16-LE
            buf = buf.decode('utf-16le')
            if buf != header:
                print("Incorrect header")
                raise LookupError

            count = 1
            while True:
                buf = src_file.read(point_size)
                if not buf:
                    break

                print(count, hex_spaced(buf))
                count += 1

        except LookupError:
            pass

        src_file.close()
        out_file.close()
        # break
