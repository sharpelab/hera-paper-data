#!/usr/bin/env python3
"""s0_parse_wip.py — generic WIT tag-tree parser for WITec Project (WIP) files.

Format (WIT_PR06): file begins with magic b"WIT_PR06", then a sequence of tags.
Tag layout:
    uint32  name_length
    bytes   name (ASCII, name_length bytes)
    uint32  type      (0 = container of child tags; >0 = leaf data)
    uint64  start     (absolute file offset of data)
    uint64  end       (absolute file offset of data end)
Leaf payload interpretation by type:
    2 = float64, 3 = float32, 4 = int64, 5 = int32, 6 = uint32,
    7 = uint16, 8 = uint8, 9 = length-prefixed string(s)
Usage:
    python s0_parse_wip.py <file.wip> tree   > tree.txt     # full tree, values for small leaves
    python s0_parse_wip.py <file.wip> strings > strings.txt # all decoded strings with paths
"""
import sys, struct
import numpy as np

MAGIC = b"WIT_PR06"

class Tag:
    __slots__ = ("name", "type", "start", "end", "children")
    def __init__(self, name, typ, start, end):
        self.name, self.type, self.start, self.end = name, typ, start, end
        self.children = []
    @property
    def size(self):
        return self.end - self.start

def parse_tags(buf, start, end, depth=0):
    tags = []
    pos = start
    while pos + 4 <= end:
        (nlen,) = struct.unpack_from("<I", buf, pos)
        if pos + 4 + nlen + 4 + 16 > end or nlen > 10000:
            break
        name = buf[pos + 4 : pos + 4 + nlen].decode("latin-1")
        p = pos + 4 + nlen
        typ, dstart, dend = struct.unpack_from("<IQQ", buf, p)
        if dstart < pos or dend < dstart or dend > len(buf):
            break
        tag = Tag(name, typ, dstart, dend)
        if typ == 0 and dend > dstart and depth < 40:
            tag.children = parse_tags(buf, dstart, dend, depth + 1)
        tags.append(tag)
        pos = dend
    return tags

DTYPES = {2: "<f8", 3: "<f4", 4: "<i8", 5: "<i4", 6: "<u4", 7: "<u2", 8: "u1"}

def leaf_array(buf, tag):
    if tag.type not in DTYPES:
        return None
    return np.frombuffer(buf[tag.start:tag.end], dtype=DTYPES[tag.type])

def leaf_string(buf, tag):
    """Type 9: sequence of (uint32 len, chars)."""
    out, pos = [], tag.start
    while pos + 4 <= tag.end:
        (slen,) = struct.unpack_from("<I", buf, pos)
        if pos + 4 + slen > tag.end:
            break
        out.append(buf[pos + 4 : pos + 4 + slen].decode("latin-1", "replace"))
        pos += 4 + slen
    return out

def load(path):
    buf = open(path, "rb").read()
    assert buf[:8] == MAGIC, buf[:8]
    return buf, parse_tags(buf, 8, len(buf))

def walk(tags, path=""):
    for t in tags:
        yield path + "/" + t.name, t
        if t.children:
            yield from walk(t.children, path + "/" + t.name)

def fmt_val(buf, t, maxn=16):
    if t.type == 9:
        s = leaf_string(buf, t)
        return " | ".join(repr(x) for x in s[:8]) + (" ..." if len(s) > 8 else "")
    a = leaf_array(buf, t)
    if a is None:
        return f"<raw {t.size} B>"
    if a.size <= maxn:
        return np.array2string(a, max_line_width=200)
    return f"<{a.size} x {a.dtype}> min={a.min():g} max={a.max():g}"

def main():
    path, mode = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "tree")
    buf, tags = load(path)
    if mode == "tree":
        for p, t in walk(tags):
            depth = p.count("/") - 1
            ind = "  " * depth
            if t.type == 0:
                print(f"{ind}{t.name}/  [{t.size} B]")
            else:
                print(f"{ind}{t.name}  (type {t.type}, {t.size} B) = {fmt_val(buf, t)}")
    elif mode == "strings":
        for p, t in walk(tags):
            if t.type == 9:
                for s in leaf_string(buf, t):
                    if s.strip():
                        print(f"{p} :: {s!r}")

if __name__ == "__main__":
    main()
