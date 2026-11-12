#!/usr/bin/env python3
"""
Loaders for Raman spectra / hyperspectral maps used by the raman_stacking tool.

Supported formats:
  - WITec ASCII export ("//Exported ASCII-File" + [Header] + [Data]):
    single spectra (2 cols) and maps (1 + SizeX*SizeY cols, column (x/y) order).
  - Headerless two-column whitespace text (wavenumber, counts).
  - PKU Zenodo-20374368 interleaved CSV: repeated (shift, intensity) column
    pairs, one pair per labeled trace.

Public data root: $HERA_DATA/raman-public-data (default /data/sharpelab/hera-data).
"""
import csv
import os
import re
from pathlib import Path

import numpy as np


def data_root():
    return Path(os.environ.get("HERA_DATA", "/data/sharpelab/hera-data")) / "raman-public-data"


def _parse_witec_header(lines):
    hdr = {}
    for ln in lines:
        if "=" in ln:
            k, v = ln.split("=", 1)
            hdr[k.strip()] = v.strip()
    return hdr


def load_witec(path):
    """WITec ASCII export -> (wavenumber[n], intensity[n, ncols], header dict).

    Single spectra come back with ncols == 1. Map pixel columns are in the
    export's (x/y) order: column index j -> x = j % SizeX, y = j // SizeX.
    """
    path = Path(path)
    raw = path.read_text(errors="replace").splitlines()
    try:
        i_data = next(i for i, ln in enumerate(raw) if ln.strip() == "[Data]")
    except StopIteration:
        raise ValueError(f"no [Data] section in {path}")
    hdr = _parse_witec_header(raw[:i_data])
    rows = []
    for ln in raw[i_data + 1:]:
        parts = ln.split("\t")
        try:
            rows.append([float(p) for p in parts])
        except ValueError:
            continue  # X-Axis / unit label lines
    arr = np.array(rows)
    order = np.argsort(arr[:, 0])
    return arr[order, 0], arr[order, 1:], hdr


def load_two_column(path):
    """Headerless whitespace two-column text -> (wavenumber, intensity)."""
    arr = np.loadtxt(path)
    order = np.argsort(arr[:, 0])
    return arr[order, 0], arr[order, 1]


def load_spectrum(path):
    """Sniff format; return (wavenumber, intensity) for a single spectrum."""
    with open(path, errors="replace") as f:
        first = f.readline()
    if first.startswith("//Exported"):
        wn, ii, _ = load_witec(path)
        return wn, ii[:, 0]
    return load_two_column(path)


def witec_excitation_nm(info_path):
    """Excitation wavelength from a WITec --Information.txt file, else None."""
    text = Path(info_path).read_text(errors="replace")
    m = re.search(r"Excitation Wavelength \[nm\]:\s*([\d.]+)", text)
    return float(m.group(1)) if m else None


def map_shape(hdr):
    return int(hdr["SizeX"]), int(hdr["SizeY"])


def load_wip(path):
    """WITec Project (.wip) -> list of spectral datasets, via the optional
    `witio` package (`uv run --with witio ...`).

    Each returned dict: caption, wn (ascending cm^-1), ii[n_wn, ncols]
    (map columns x-fastest, matching load_witec: x = j % nx), nx, ny, meta
    (the WITec measurement metadata dict — wavelength, power-in-fiber,
    integration time, scan geometry, timestamps). Non-spectral project
    items (video images, cursors, transformations) are skipped; read them
    with witio directly if needed (video images carry per-pixel µm grids
    for registration).
    """
    import witio  # optional dep

    out = []
    for d in witio.read(str(path)).data:
        try:
            arr = d.array()
            xa = d.x_axis()
        except Exception:
            continue
        arr = np.asarray(arr)
        meta = d.measurement_metadata
        meta = meta() if callable(meta) else meta
        meta = meta or {}
        if arr.ndim == 3:            # hyperspectral map
            # witio yields (x, y, n_spec) when the in-file scan_size
            # metadata matches (shape[0], shape[1]); transpose so the
            # column order is x-fastest with nx/ny in the sample frame.
            sx = meta.get("scan_size_x_px")
            sy = meta.get("scan_size_y_px")
            if sx and sy and (int(sx), int(sy)) == arr.shape[:2]:
                arr = arr.transpose(1, 0, 2)
            ny, nx, nsp = arr.shape
            ii = arr.reshape(ny * nx, nsp).T
        elif arr.ndim == 1:          # single spectrum
            ny, nx = 1, 1
            ii = arr[:, None]
        else:
            continue
        wn = np.asarray(xa[0] if isinstance(xa, tuple) else xa,
                        dtype=float).ravel()
        if wn.size != ii.shape[0]:
            continue
        order = np.argsort(wn)
        out.append(dict(caption=d.caption, wn=wn[order], ii=ii[order],
                        nx=nx, ny=ny, meta=meta))
    return out


def load_pku_pairs(path):
    """PKU interleaved CSV -> list of (label, wavenumber, intensity)."""
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    heads = rows[0]
    out = []
    for j in range(0, len(heads), 2):
        label = heads[j + 1]
        wn, ii = [], []
        for r in rows[1:]:
            if j + 1 < len(r) and r[j] and r[j + 1]:
                wn.append(float(r[j]))
                ii.append(float(r[j + 1]))
        wn, ii = np.array(wn), np.array(ii)
        order = np.argsort(wn)
        out.append((label, wn[order], ii[order]))
    return out
