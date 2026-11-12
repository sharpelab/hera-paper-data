#!/usr/bin/env python3
"""s1_extract.py — extract the four 73474_ spectral maps + three video images
from vti-01.wip into data.npz / video_*.png, with stage-frame geometry.

Run: uv run --with numpy --with matplotlib python s1_extract.py
Outputs (this dir): data.npz, video_002.png, video_004.png, video_007.png
"""
import numpy as np
from s0_parse_wip import load, walk, leaf_array, leaf_string

WIP = "/data/sharpelab/hera-data/raman-vti-01/vti-01.wip"

buf, tags = load(WIP)
nodes = dict(walk(tags))

def child(tag, *names):
    t = tag
    for n in names:
        t = next(c for c in t.children if c.name == n)
    return t

def arr(tag, *names):
    return leaf_array(buf, child(tag, *names))

# ---- index data objects by their position in the Data container ----
data_root = next(t for t in tags[0].children if t.name == "Data")
objs = {}  # index -> (classname, tag)
i = 0
kids = data_root.children
while i < len(kids):
    if kids[i].name.startswith("DataClassName"):
        idx = int(kids[i].name.split()[-1])
        cls = leaf_string(buf, kids[i])[0]
        dtag = kids[i + 1]
        objs[idx] = (cls, dtag)
        i += 2
    else:
        i += 1

by_id = {}   # WITec object ID -> (classname, tag)
for idx, (cls, dtag) in objs.items():
    try:
        oid = int(arr(dtag, "TData", "ID")[0])
        by_id[oid] = (cls, dtag)
    except StopIteration:
        pass

def space_transform(oid):
    cls, t = by_id[oid]
    vp = child(t, "TDSpaceTransformation", "ViewPort3D")
    return dict(
        model_origin=arr(vp, "ModelOrigin")[:2],
        world_origin=arr(vp, "WorldOrigin")[:2],
        scale=arr(vp, "Scale").reshape(3, 3)[:2, :2],
        rot=arr(vp, "Rotation").reshape(3, 3)[:2, :2],
    )

def spectral_axis(oid):
    cls, t = by_id[oid]
    st = child(t, "TDSpectralTransformation")
    poly = arr(st, "FreePolynom")
    bins = np.arange(2000, dtype=float)
    lam = np.zeros_like(bins)
    for k, c in enumerate(poly):
        lam += c * bins ** k
    return lam  # nm

EXC_532 = 532.3380127  # nm, from trace records

out = {}
maps = {}
for idx, (cls, dtag) in objs.items():
    if cls != "TDGraph":
        continue
    cap = leaf_string(buf, child(dtag, "TData", "Caption"))[0]
    g = child(dtag, "TDGraph")
    sx = int(arr(g, "SizeX")[0]); sy = int(arr(g, "SizeY")[0])
    sg = int(arr(g, "SizeGraph")[0])
    raw = leaf_array(buf, child(g, "GraphData", "Data")).astype(np.float32)
    cube = raw.reshape(sy, sx, sg)
    inverted = bool(arr(g, "DataFieldInverted")[0])
    lam = spectral_axis(int(arr(g, "XTransformationID")[0]))
    tr = space_transform(int(arr(g, "SpaceTransformationID")[0]))
    key = cap.split("--")[2]  # '003'
    maps[key] = dict(cube=cube, lam=lam, tr=tr, inverted=inverted,
                     caption=cap, sx=sx, sy=sy)

# ---- stage-frame pixel-center coordinates ----
# world = world_origin + R @ (S @ (model - model_origin)); model = (i+0.5, j+0.5)
# for pixel column i (0..sx-1), row j (0..sy-1) in STORED order. DataFieldInverted
# is handled empirically in s2 (overlap cross-check between maps 003/005).
def pixel_world(m):
    sx, sy, tr = m["sx"], m["sy"], m["tr"]
    ii, jj = np.meshgrid(np.arange(sx) + 0.5, np.arange(sy) + 0.5)
    model = np.stack([ii - tr["model_origin"][0], jj - tr["model_origin"][1]])
    v = np.einsum("ab,bij->aij", tr["rot"] @ tr["scale"], model)
    return v[0] + tr["world_origin"][0], v[1] + tr["world_origin"][1]

for key, m in maps.items():
    wx, wy = pixel_world(m)
    out[f"cube_{key}"] = m["cube"]
    out[f"lam_{key}"] = m["lam"]
    out[f"wx_{key}"] = wx
    out[f"wy_{key}"] = wy
    out[f"inverted_{key}"] = np.array(m["inverted"])
    print(f"map {key}: {m['sy']}x{m['sx']}x2000, inverted={m['inverted']}, "
          f"x {wx.min():.1f}..{wx.max():.1f}, y {wy.min():.1f}..{wy.max():.1f}")

out["exc_nm"] = np.array(EXC_532)
np.savez_compressed("data.npz", **out)
print("wrote data.npz")

# ---- video images ----
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

for idx, (cls, dtag) in objs.items():
    if cls != "TDBitmap":
        continue
    cap = leaf_string(buf, child(dtag, "TData", "Caption"))[0]
    key = cap.split("--")[-1]
    b = child(dtag, "TDBitmap")
    sx = int(arr(b, "SizeX")[0]); sy = int(arr(b, "SizeY")[0])
    dtag_data = child(b, "BitmapData", "Data")
    rgba = np.frombuffer(buf[dtag_data.start:dtag_data.end], dtype=np.uint8)
    rgba = rgba.reshape(sy, sx, 4)
    img = rgba[:, :, :3].mean(axis=2)  # grayscale from BGR
    tr = space_transform(int(arr(b, "SpaceTransformationID")[0]))
    # corners in world frame (model units = pixels, origin at (0,0))
    corners = np.array([[0, 0], [sx, 0], [sx, sy], [0, sy]], float)
    wc = (tr["rot"] @ tr["scale"] @ (corners - tr["model_origin"]).T).T + tr["world_origin"]
    np.savez_compressed(f"video_{key}.npz", img=img.astype(np.float32), corners=wc)
    fig, ax = plt.subplots(figsize=(10, 7.5))
    ax.imshow(img, cmap="gray",
              extent=[wc[0, 0], wc[1, 0], wc[2, 1], wc[0, 1]])
    ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)")
    ax.set_title(f"{cap} (stage frame, rotation ignored ~0.5°)")
    # overlay map footprints
    for k, m in maps.items():
        wx, wy = pixel_world(m)
        ax.plot([wx[0, 0], wx[0, -1], wx[-1, -1], wx[-1, 0], wx[0, 0]],
                [wy[0, 0], wy[0, -1], wy[-1, -1], wy[-1, 0], wy[0, 0]],
                lw=1.2, label=f"map {k}")
    ax.legend(fontsize=8)
    fig.savefig(f"video_{key}.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote video_{key}.png ({sy}x{sx})")
