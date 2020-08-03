import os

from common import rreplace, hex_spaced

"""
    WITRN U2p: maximum 352 points x 5 bytes each
    total 1760 bytes for internal offline storage

    VAT format specification (WITRN Meter v4.6):
    file name: YYYYMMDD_HHIISS_CCC.vat
        Y - Year
        M - Month (01-12)
        D - Day of month (01-31)
        H - Hour (00-23)
        I - mInutes (00-59)
        S - Seconds (00-59)
        C - total Count of recorded points in file
    
    file structure
    2 bytes - header, time/interval ???
    {Count} records, 5 bytes for each record:
        2 bytes - voltage
        2 bytes - current
        1 byte - ext. temp
"""

src_dir = "src"
out_dir = "out"
src_ext = ".vat"
out_ext = ".csv"
point_size = 5  # bytes in sequence

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
            buf = src_file.read(2)  # header
            print(hex_spaced(buf))

            count = 1
            while True:
                buf = src_file.read(point_size)
                if not buf:
                    break

                if buf[point_size - 1] != 0xb8:
                    print(count, hex_spaced(buf))
                count += 1

        except LookupError:
            pass

        src_file.close()
        out_file.close()
        # break
