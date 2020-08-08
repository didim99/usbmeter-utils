# Common functions

def rreplace(s, old, new, occurrence=1) -> str:
    li = s.rsplit(old, occurrence)
    return new.join(li)


def hex_spaced(s, sep=' ') -> str:
    return sep.join(["{:02x}".format(x) for x in s])


def ts2str(ts, sep=':') -> str:
    res = []
    for part in [1000, 60, 60]:
        res.append(ts % part)
        ts //= part
    res = "{:02d}:{:02d}:{:02d}{}{:03d}".format(
        ts, res[2], res[1], sep, res[0])
    return res


def str2ts(*args) -> int:
    args = [int(v) for v in reversed(args)]
    factors = [1, 1000, 60, 60]
    factor = 1
    res = 0
    for i in range(len(factors)):
        factor *= factors[i]
        res += args[i]*factor
    return res


def read_int(src, size) -> int or None:
    buf = src.read(size)
    if not buf:
        return None
    return int.from_bytes(buf, 'little', signed=True)


def lines_count(name):
    with open(name) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
