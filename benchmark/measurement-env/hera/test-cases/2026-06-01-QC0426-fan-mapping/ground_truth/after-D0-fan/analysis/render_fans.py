#!/usr/bin/env python3
"""
Answer-key renderer for the QC0426 `after-D0-fan` frontier.

Reuses the QC0426 analysis convention (analysis.ipynb, cells 24-26 / 55 / 62-65)
WITHOUT the `sweep` package: reads `data.tsv.gz` + `metadata.json` directly,
re-forms Rxx, computes (n, D) from the gate-line via the capacitance helper, and
renders the artifacts relevant to this frontier:

  - the latest result (run 27): the D = 0 Landau fan Rxx(n, B) to 8 T
    -> ana_27_fan_D0.png        (perception-layer target -- see reading.md)
  - the answer key (the "introduce the Si gate" move):
      run 28: the TG-Si gate map Rxx(V_TG, V_Si) at B = 8 T, BG = -4 V
              -> ana_28_tgsi-map.png
      run 31: the Si-screened D = 0 Landau fan Rxx(n, B), Si = +60 V, to 13 T
              -> ana_31_fan_D0_Si60.png
      run 33: the VSi-n map Rxx(n, V_Si) at D = 0 (negative-Si branch)
              -> ana_33_vsi-n-map.png

Convention (matches the device's analysis.ipynb):
  I    = sr0_X / sr0_gain                  (sr0 = drain current, gain -1e6)
  Rxx  = sr{1,2,3}_X / I
  n,D  = calc_nD(Vtg=DC_bias, Vbg=k_bg_volt, c_tg, c_bg)
  c_tg = eps0*kappa_hBN/t_tg ; c_bg = eps0/(t_bg/kappa_hBN + t_bgSiO2/kappa_SiO2)
  t_bg=12nm, t_bgSiO2=0 (back gate is hBN/graphite), t_tg=1.3*t_bg=15.6nm
  n_12cm = n * 1e-16   (units of 1e12 cm^-2)

The TG-Si map (run 28) has no back-gate column (BG fixed at -4 V) and steps the
Si gate, so it is rendered in raw gate volts (V_TG vs V_Si) -- the natural axes
for that map. The Si-screened fan (31) and the VSi-n map (33) use calc_nD on the
constant-D gate-line as for the D-series fans.

Run from the fixture root or anywhere; SRC points at the source measurement dir.
The post-cut runs (28, 31, 33) are NOT in the fixture data/ (they are the answer
key); this script reads them from the source measurement dir at build time.
"""
import json, gzip, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
import scipy.constants as cst

SRC = "/data/sharpelab/dgglab-measurements/vti/qingrui/20260601-QC0426-3LGr/data"
OUT = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(OUT, exist_ok=True)

eps0 = cst.epsilon_0; e = cst.e; h = cst.h
kappa_hBN, kappa_SiO2 = 3.0, 3.9
t_bg, t_bgSiO2 = 12e-9, 0.0
t_tg = 1.3 * t_bg
c_tg = eps0 * kappa_hBN / t_tg
c_bg = eps0 / (t_bg / kappa_hBN + (t_bgSiO2 / kappa_SiO2 if t_bgSiO2 else 0.0))

def calc_nD(Vtg, Vbg):
    n = (1.0 / e) * (c_tg * Vtg + c_bg * Vbg)
    D = 0.5 * (c_tg * Vtg - c_bg * Vbg) / eps0
    return n, D

def load(rid):
    m = json.load(open(f"{SRC}/{rid}/metadata.json"))
    f = f"{SRC}/{rid}/data.tsv.gz"
    if not os.path.exists(f): f = f"{SRC}/{rid}/data.tsv"
    arr = np.loadtxt(f)
    cols = m["columns"]
    d = {c: arr[:, i] for i, c in enumerate(cols)}
    d["_meta"] = m
    return d

def Rxx(d, ch):
    I = d["sr0_X"] / d["_meta"]["measurement_config"]["sr0_gain"]
    return d[f"sr{ch}_X"] / I

def render_fan(rid, dlabel, tag, ch=1):
    """multimegasweep B-n Landau fan: slow=B, fast=[Vtg, Vbg] gate-line."""
    d = load(rid); m = d["_meta"]
    nf = len(m["fast_setpoints"][0]); ns = len(m["slow_setpoints"][0])
    Vtg = np.asarray(m["fast_setpoints"][0]); Vbg = np.asarray(m["fast_setpoints"][1])
    B = np.asarray(m["slow_setpoints"][0])
    n, _ = calc_nD(Vtg, Vbg); n12 = n * 1e-16
    R = Rxx(d, ch)
    ns_have = R.size // nf
    if ns_have < ns:
        print(f"  run {rid}: INTERRUPTED fan — {ns_have}/{ns} B-rows complete")
        B = B[:ns_have]
    R2 = R[: ns_have * nf].reshape(ns_have, nf)
    fig, ax = plt.subplots(figsize=(5 * 1.2, 4.2))
    norm = SymLogNorm(linthresh=100, vmin=0, vmax=5e4)
    pm = ax.pcolormesh(n12, B, R2, cmap="viridis", norm=norm, shading="auto")
    fig.colorbar(pm, ax=ax, label=r"$R_{xx}$ ($\Omega$)")
    ax.set_xlabel(r"$n$ ($10^{12}$ cm$^{-2}$)"); ax.set_ylabel(r"$B$ (T)")
    ax.set_title(f"run {rid}: Landau fan, {dlabel}  (sr{ch})")
    fig.tight_layout()
    p = os.path.join(OUT, f"ana_{rid}_fan_{tag}.png")
    fig.savefig(p, dpi=120); plt.close(fig); print("wrote", p)

def render_tgsi_map(rid, ch=1):
    """megasweep TG-Si gate map: slow=V_Si, fast=V_TG, at fixed B, BG.
    No back-gate column (BG fixed), so plot in raw gate volts."""
    d = load(rid); m = d["_meta"]
    Vtg = np.asarray(m["fast_setpoints"], dtype=float)
    Vsi = np.asarray(m["slow_setpoints"], dtype=float)
    nf, ns = len(Vtg), len(Vsi)
    R = Rxx(d, ch)
    ns_have = R.size // nf
    if ns_have < ns: Vsi = Vsi[:ns_have]
    R2 = R[: ns_have * nf].reshape(ns_have, nf)
    fig, ax = plt.subplots(figsize=(5 * 1.2, 4.2))
    norm = SymLogNorm(linthresh=100, vmin=0, vmax=5e4)
    pm = ax.pcolormesh(Vtg, Vsi, R2, cmap="viridis", norm=norm, shading="auto")
    fig.colorbar(pm, ax=ax, label=r"$R_{xx}$ ($\Omega$)")
    ax.set_xlabel(r"$V_{TG}$ (V, DC205)"); ax.set_ylabel(r"$V_{Si}$ (V, k$_{2410}$)")
    ax.set_title(f"run {rid}: TG-Si gate map, B = 8 T, BG = -4 V  (sr{ch})")
    fig.tight_layout()
    p = os.path.join(OUT, f"ana_{rid}_tgsi-map.png")
    fig.savefig(p, dpi=120); plt.close(fig); print("wrote", p)

def render_vsi_map(rid, ch=1):
    """multimegasweep VSi-n map: slow=V_Si, fast=[Vtg, Vbg] D=0 gate-line."""
    d = load(rid); m = d["_meta"]
    Vtg = np.asarray(m["fast_setpoints"][0]); Vbg = np.asarray(m["fast_setpoints"][1])
    Vsi = np.asarray(m["slow_setpoints"][0], dtype=float)
    nf, ns = len(Vtg), len(Vsi)
    n, _ = calc_nD(Vtg, Vbg); n12 = n * 1e-16
    R = Rxx(d, ch)
    ns_have = R.size // nf
    if ns_have < ns: Vsi = Vsi[:ns_have]
    R2 = R[: ns_have * nf].reshape(ns_have, nf)
    fig, ax = plt.subplots(figsize=(5 * 1.2, 4.2))
    norm = SymLogNorm(linthresh=100, vmin=0, vmax=5e4)
    pm = ax.pcolormesh(n12, Vsi, R2, cmap="viridis", norm=norm, shading="auto")
    fig.colorbar(pm, ax=ax, label=r"$R_{xx}$ ($\Omega$)")
    ax.set_xlabel(r"$n$ ($10^{12}$ cm$^{-2}$)"); ax.set_ylabel(r"$V_{Si}$ (V)")
    ax.set_title(f"run {rid}: VSi-n map at D = 0  (sr{ch})")
    fig.tight_layout()
    p = os.path.join(OUT, f"ana_{rid}_vsi-n-map.png")
    fig.savefig(p, dpi=120); plt.close(fig); print("wrote", p)

if __name__ == "__main__":
    render_fan(27, "D = 0", "D0")              # latest result (perception target)
    render_tgsi_map(28)                         # answer: introduce the Si gate
    render_fan(31, "D = 0, Si = +60 V", "D0_Si60")  # answer: Si-screened fan
    render_vsi_map(33)                          # answer: VSi-n map at D = 0
