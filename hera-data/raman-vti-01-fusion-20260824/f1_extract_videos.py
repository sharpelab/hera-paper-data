"""f1_extract_videos.py — pull the three stage-registered video images
(the only frame bridge) out of vti-01.wip, with their stage transforms.

Output: fusion_videos.npz with, per video NNN:
  imgNNN (H,W float grayscale), plus worldorigin/scale/rotation arrays,
and a cross-check table printed against raman-provenance.md.
"""
import numpy as np

import f0_parse_wip as f

buf, roots = f.load()
data_node = [n for n in roots[0]["children"] if n["name"] == "Data"][0]


def get(node, path):
    cur = [node]
    for p in path.split("/"):
        cur = [k for c in cur for k in c["children"] if k["name"] == p]
    return cur


by_id = {}
for ch in data_node["children"]:
    if ch["dtype"] != 0:
        continue
    idn = get(ch, "TData/ID")
    if idn:
        by_id[int(f.data(buf, idn[0])[0])] = ch

out = {}
for ch in data_node["children"]:
    if not get(ch, "TDBitmap"):
        continue
    cap = f.data(buf, get(ch, "TData/Caption")[0])[0]
    tag = cap.split("--")[-1]  # e.g. 002
    sx = int(f.data(buf, get(ch, "TDBitmap/SizeX")[0])[0])
    sy = int(f.data(buf, get(ch, "TDBitmap/SizeY")[0])[0])
    raw = f.data(buf, get(ch, "TDBitmap/BitmapData/Data")[0])
    px = np.frombuffer(raw, dtype="<u4").reshape(sy, sx)
    # 4 bytes/px: try BGRA split; grayscale video -> channels equal
    b = (px & 0xFF).astype(np.float32)
    g = ((px >> 8) & 0xFF).astype(np.float32)
    r = ((px >> 16) & 0xFF).astype(np.float32)
    gray = (r + g + b) / 3.0
    stid = int(f.data(buf, get(ch, "TDBitmap/SpaceTransformationID")[0])[0])
    st = by_id[stid]
    wo = f.data(buf, get(st, "TDSpaceTransformation/ViewPort3D/WorldOrigin")[0])
    sc = f.data(buf, get(st, "TDSpaceTransformation/ViewPort3D/Scale")[0]).reshape(3, 3)
    rot = f.data(buf, get(st, "TDSpaceTransformation/ViewPort3D/Rotation")[0]).reshape(3, 3)
    utc = f.data(buf, get(ch, "TData/CreationOrChangeUTCTime")[0])[0]
    ang = np.degrees(np.arctan2(rot[1, 0], rot[0, 0]))
    print(f"{cap}: {sx}x{sy}px, {sc[0,0]:.5f} um/px, TL world=({wo[0]:.2f},{wo[1]:.2f}), "
          f"rot={ang:+.3f} deg, chan-equal={np.allclose(r,g) and np.allclose(g,b)}, {utc}")
    out[f"img{tag}"] = gray.astype(np.float32)
    out[f"wo{tag}"] = wo
    out[f"scale{tag}"] = sc
    out[f"rot{tag}"] = rot
    out[f"utc{tag}"] = np.array(utc)

np.savez_compressed("fusion_videos.npz", **out)
print("saved fusion_videos.npz:", sorted(out))
