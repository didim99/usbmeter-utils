# Common functions

def rreplace(s, old, new, occurrence=0):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def hex_spaced(s, sep=' '):
    return sep.join(["{:02x}".format(x) for x in s])