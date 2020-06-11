import datetime


def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    for k, v in d.items():
        d[k] = str(v).zfill(2)
    return fmt.format(**d)

def blockno_to_NW_idx(blockno):
    return ((blockno // 3) * 3, (blockno % 3) * 3)

def idx_to_blockno(row, col):
    return 3*(row // 3) + (col // 3)

def some(iterable):
    for i in iterable:
        if i:
            return i
    return False
