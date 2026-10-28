#!/usr/bin/env python3
"""
Answer-key renderer for the QC0426 `after-density-cut` frontier.

Self-contained reproduction of Qingrui's analysis convention (analysis.ipynb,
cells 24-26 / 55 / 62-65) WITHOUT the `sweep` package: reads `data.tsv.gz` +
`metadata.json` directly, re-forms Rxx, computes (n, D) from the gate-line via
the capacitance helper, and renders:

  - the latest result (run 79): the 0-field density cut Rxx(n) at the D = 0.25
    gate-line  -> ana_79_density-cut_D0p25.png
  - context (run 27): the D = 0 Landau fan Rxx(n, B)  -> ana_27_fan_D0.png
  - the answer key (runs 80-84): the D-series Landau fans Rxx(n, B)
    -> ana_8x_fan_D{...}.png

Convention (matches the device's analysis.ipynb):
  I    = sr0_X / sr0_gain                  (sr0 = drain current, gain -1e6)
  Rxx  = sr{1,2,3}_X / I
  n,D  = calc_nD(Vtg=DC_bias, Vbg=k_bg_volt, c_tg, c_bg)
  c_tg = eps0*kappa_hBN/t_tg ; c_bg = eps0/(t_bg/kappa_hBN + t_bgSiO2/kappa_SiO2)
  t_bg=12nm, t_bgSiO2=0 (back gate is hBN/graphite), t_tg=1.3*t_bg=15.6nm
  n_12cm = n * 1e-16   (units of 1e12 cm^-2)

Run from the fixture root or anywhere; SRC points at the source measurement dir.
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

def render_density_cut(rid, dlabel):
    d = load(rid)
    n, _ = calc_nD(d["DC_bias"], d["k_bg_volt"]); n12 = n * 1e-16
    fig, ax = plt.subplots(figsize=(5 * 1.618, 4))
    for ch in (1, 2, 3):
        ax.plot(n12, Rxx(d, ch), lw=1, label=f"sr{ch}")
    ax.set_xlabel(r"$n$ ($10^{12}$ cm$^{-2}$)"); ax.set_ylabel(r"$R_{xx}$ ($\Omega$)")
    ax.set_title(f"run {rid}: 0-field density cut, {dlabel} (latest result)")
    ax.legend(fontsize=8); fig.tight_layout()
    p = os.path.join(OUT, f"ana_{rid}_density-cut_D0p25.png")
    fig.savefig(p, dpi=120); plt.close(fig); print("wrote", p)

def render_fan(rid, dlabel, tag, ch=1):
    d = load(rid); m = d["_meta"]
    nf = len(m["fast_setpoints"][0]); ns = len(m["slow_setpoints"][0])
    Vtg = np.asarray(m["fast_setpoints"][0]); Vbg = np.asarray(m["fast_setpoints"][1])
    B = np.asarray(m["slow_setpoints"][0])
    n, _ = calc_nD(Vtg, Vbg); n12 = n * 1e-16
    R = Rxx(d, ch)
    # row-major: slow (B) outer, fast (gate-line) inner. Handle interrupted fans
    # (e.g. run 84 stopped partway) by reshaping only the complete B-rows.
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

if __name__ == "__main__":
    render_density_cut(79, "D = 0.25")
    render_fan(27, "D = 0", "D0")
    for rid, dlab, tag in [(80, "D = 0.25", "D0p25"), (81, "D = 1", "D1"),
                           (82, "D = -1", "Dm1"), (83, "D = -0.25", "Dm0p25"),
                           (84, "D = -0.5", "Dm0p5")]:
        render_fan(rid, dlab, tag)
