"""f0_parse_wip.py — minimal independent WIT-tag parser for vti-01.wip.

Fusion-side re-extraction of the ONLY frame bridge: the stage-registered
video images (TDBitmap) inside the WITec project. Written fresh for the
fusion step (the Raman read's s0 parser was not an input).

WIT_PR06 tag format (public knowledge, e.g. witio/apricot readers):
  int32 name_len | name bytes | uint32 dtype | int64 start | int64 end
  dtype 0 => children tags occupy [start, end); else raw data there.
"""
import struct
import sys

import numpy as np

WIP = "/data/sharpelab/hera-data/raman-vti-01/vti-01.wip"


def read_tag(buf, pos):
    (nlen,) = struct.unpack_from("<i", buf, pos)
    pos += 4
    name = buf[pos : pos + nlen].decode("latin1")
    pos += nlen
    dtype, start, end = struct.unpack_from("<Iqq", buf, pos)
    pos += 4 + 8 + 8
    return name, dtype, start, end, pos


def parse_children(buf, start, end, depth, out, path):
    pos = start
    while pos < end:
        try:
            name, dtype, dstart, dend, pos = read_tag(buf, pos)
        except (struct.error, UnicodeDecodeError):
            return
        if dstart < 0 or dend > len(buf) or dend < dstart:
            return
        node = {"name": name, "dtype": dtype, "start": dstart, "end": dend,
                "path": path + "/" + name, "children": []}
        out.append(node)
        if dtype == 0:
            parse_children(buf, dstart, dend, depth + 1, node["children"], node["path"])
        pos = dend


def flatten(nodes):
    for n in nodes:
        yield n
        yield from flatten(n["children"])


DT = {2: ("<f8", 8), 3: ("<f4", 4), 4: ("<i8", 8), 5: ("<i4", 4),
      6: ("<u2", 2), 7: ("<u1", 1)}


def data(buf, node):
    b = buf[node["start"] : node["end"]]
    if node["dtype"] in DT:
        fmt, sz = DT[node["dtype"]]
        return np.frombuffer(b, dtype=fmt)
    if node["dtype"] == 9:  # length-prefixed string(s)
        out, p = [], 0
        while p + 4 <= len(b):
            (ln,) = struct.unpack_from("<i", b, p)
            p += 4
            if ln < 0 or p + ln > len(b):
                break
            out.append(b[p : p + ln].decode("latin1", "replace"))
            p += ln
        return out
    return b


def load():
    buf = open(WIP, "rb").read()
    assert buf[:8] == b"WIT_PR06", buf[:8]
    roots = []
    # file: 8-byte magic then the root tag
    parse_children(buf, 8, len(buf), 0, roots, "")
    return buf, roots


if __name__ == "__main__":
    buf, roots = load()
    want = sys.argv[1] if len(sys.argv) > 1 else None
    for n in flatten(roots):
        sz = n["end"] - n["start"]
        if want and want.lower() not in n["path"].lower():
            continue
        depth = n["path"].count("/")
        if n["dtype"] == 0 or sz <= 64:
            extra = ""
            if n["dtype"] != 0:
                d = data(buf, n)
                extra = " = " + (str(d[:8]) if isinstance(d, np.ndarray) else str(d)[:80])
            print(f'{"  "*depth}{n["name"]} [t{n["dtype"]} {sz}B]{extra}')
        else:
            print(f'{"  "*depth}{n["name"]} [t{n["dtype"]} {sz}B]')
