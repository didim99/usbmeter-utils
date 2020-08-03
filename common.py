# Common functions

def rreplace(s, old, new, occurrence=1) -> str:
    li = s.rsplit(old, occurrence)
    return new.join(li)


def hex_spaced(s, sep=' ') -> str:
    return sep.join(["{:02x}".format(x) for x in s])


def timestr(ts, sep=':') -> str:
    res = []
    for part in [1000, 60, 60]:
        res.append(ts % part)
        ts //= part
    res = "{:02d}:{:02d}:{:02d}{}{:03d}".format(
        ts, res[2], res[1], sep, res[0])
    return res


def read_int(src, size) -> int or None:
    buf = src.read(size)
    if not buf:
        return None
    return int.from_bytes(buf, 'little', signed=True)
