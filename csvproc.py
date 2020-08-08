import os

from common import ts2str, lines_count

src_dir = "src"
out_dir = "out"
src_ext = ".csv"
default_div = ','
time_div = ':'

reformat = True
add_header = True
decimal_div = ','
value_div = ';'

resample = True
resample_rate = 100     # 2, 5, 10, 20, 50, 100, ...
resample_mode = 'avg'   # start, end, center, avg


def num_fields(point):
    fields = []
    for field in point:
        if type(point[field]) in [int, float]:
            fields.append(field)
    return fields


def resample_avg(data):
    res = {}
    fields = num_fields(data[0])
    for field in data[0]:
        res[field] = 0 if field in fields else None
    for field in fields:
        for point in data:
            res[field] += point[field]
        res[field] /= len(data)
    res['ts'] = data[0]['ts']
    return res


if __name__ == '__main__':
    cwd = os.getcwd()
    src_dir = cwd + "/" + src_dir
    out_dir = cwd + "/" + out_dir

    if resample_rate == 1:
        resample = False
    if not reformat:
        decimal_div = '.'
        value_div = default_div
    time_div_ms = decimal_div if reformat else time_div

    header_line = value_div.join(
        ['time (HH:MM:SS{}MS)'.format(time_div_ms), 'voltage (V)',
         'current (A)', 'D+ (V)', ' D- (V)', 'temp (deg)'])
    formats = {'v': '{:.3f}', 'c': '{:.3f}',
               'd+': '{:.1f}', 'd-': '{:.1f}', 't': '{:d}'}

    files = 0
    for name in os.listdir(src_dir):
        if src_ext != os.path.splitext(name)[1]:
            continue

        print(f"Processing: {name}")
        last_line = lines_count(src_dir + "/" + name) - 1
        src_file = open(src_dir + "/" + name, "r")
        out_file = open(out_dir + "/" + name, "w")

        points = []
        total_read = 0
        processed = written = 0
        for line in src_file:
            line = line.strip()
            if not line:
                total_read += 1
                continue

            if processed == 0:
                if add_header:
                    out_file.write(header_line)
                    out_file.write("\n")
                if "?" in line:
                    total_read += 1
                    processed += 1
                    continue

            line = line.split(default_div)
            ts = str2ts(*line[0].split(time_div))
            point = {'ts': ts, 'v': float(line[1]), 'c': float(line[2]),
                     'd+': float(line[3]), 'd-': float(line[4]),
                     't': None if line[5] == 'null' else int(line[5])}
            points.append(point)

            if not resample or total_read == last_line \
               or len(points) == resample_rate:
                if resample:
                    if resample_mode == 'start':
                        point = points[0]
                    elif resample_mode == 'end':
                        point = points[-1]
                    elif resample_mode == 'center':
                        point = points[len(points) // 2]
                    elif resample_mode == 'avg':
                        point = resample_avg(points)
                    else:
                        exit('Unknown resample mode')

                point['ts'] = ts2str(point['ts'], time_div_ms)
                for field in point:
                    if point[field] is None:
                        point[field] = 'null'
                    elif field in formats:
                        point[field] = formats[field].format(point[field]) \
                            .replace('.', decimal_div)

                out_file.write(value_div.join(point.values()))
                out_file.write("\n")
                written += 1
                points = []

            total_read += 1
            processed += 1
            # break

        print(f"Total lines processed: {processed}")
        print(f"Total lines written: {written}")

        src_file.close()
        out_file.close()
        files += 1

    print(f"Total files processed: {files}")
