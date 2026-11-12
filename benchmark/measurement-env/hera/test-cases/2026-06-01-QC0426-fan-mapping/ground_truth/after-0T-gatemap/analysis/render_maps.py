#!/usr/bin/env python3
"""
Answer-key renderer for the QC0426 `after-0T-gatemap` frontier.

Self-contained reproduction of Qingrui's analysis convention (analysis.ipynb,
cells 24-26 / 55 / 62-65) WITHOUT the `sweep` package: reads `data.tsv.gz` +
`metadata.json` directly, re-forms Rxx, and renders:

  - the latest result (run 26): the B = 3 T finite-field TG-BG gate map
    Rxx(Vtg, Vbg)                         -> ana_26_gatemap_3T.png
  - context (run 25): the complete 0 T TG-BG gate map (where the CNP slope
    Vtg = -1.3*Vbg + 0.06 was fit)        -> ana_25_gatemap_0T.png
  - the answer key (run 27): the D = 0 Landau fan Rxx(n, B) to 8 T
                                          -> ana_27_fan_D0.png
  - the answer key (run 31): the D = 0 Landau fan extended to 13 T
                                          -> ana_31_fan_D0_13T.png

Convention (matches the device's analysis.ipynb, identical to the sibling
`after-density-cut/analysis/render_fans.py`):
  I    = sr0_X / sr0_gain                  (sr0 = drain current, gain -1e6)
  Rxx  = sr{1,2,3}_X / I
  n,D  = calc_nD(Vtg=DC_bias, Vbg=k_bg_volt, c_tg, c_bg)
  c_tg = eps0*kappa_hBN/t_tg ; c_bg = eps0/(t_bg/kappa_hBN + t_bgSiO2/kappa_SiO2)
  t_bg=12nm, t_bgSiO2=0 (back gate is hBN/graphite), t_tg=1.3*t_bg=15.6nm
  n_12cm = n * 1e-16   (units of 1e12 cm^-2)

The gate maps (25, 26) are `megasweep`s whose metadata stores FLAT slow/fast
setpoint lists (slow = k_bg, 197 pts; fast = DC_bias, 281 pts), distinct from
the fan's nested `multimegasweep` setpoints; `render_gatemap` reshapes the
recorded gate columns directly so it is robust to raster order. `render_fan`
is copied verbatim from `render_fans.py`.

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

def render_gatemap(rid, blabel, tag, ch=1):
    """TG-BG gate map from a `megasweep` (flat slow/fast setpoints)."""
    d = load(rid); m = d["_meta"]
    nslow = len(m["slow_setpoints"]); nfast = len(m["fast_setpoints"])
    R = Rxx(d, ch)
    have = R.size // nfast            # complete fast-rows (guards a stopped map)
    if have < nslow:
        print(f"  run {rid}: INCOMPLETE map — {have}/{nslow} rows complete")
        nslow = have
    sl = slice(0, nslow * nfast)
    Vtg = d["DC_bias"][sl].reshape(nslow, nfast)   # fast axis
    Vbg = d["k_bg_volt"][sl].reshape(nslow, nfast)  # slow axis
    R2 = R[sl].reshape(nslow, nfast)
    fig, ax = plt.subplots(figsize=(5 * 1.25, 4.2))
    norm = SymLogNorm(linthresh=100, vmin=0, vmax=5e4)
    pm = ax.pcolormesh(Vtg, Vbg, R2, cmap="viridis", norm=norm, shading="auto")
    fig.colorbar(pm, ax=ax, label=r"$R_{xx}$ ($\Omega$)")
    # CNP D-line fit from the 0 T map: Vtg = -1.3*Vbg + 0.06
    vbg_line = np.linspace(Vbg.min(), Vbg.max(), 50)
    ax.plot(-1.3 * vbg_line + 0.06, vbg_line, "w--", lw=1,
            label=r"CNP: $V_{tg}=-1.3\,V_{bg}+0.06$")
    ax.set_xlabel(r"$V_{tg}$ (DC205, V)"); ax.set_ylabel(r"$V_{bg}$ (k_bg, V)")
    ax.set_title(f"run {rid}: TG-BG gate map, {blabel}  (sr{ch})")
    ax.legend(fontsize=7, loc="upper right"); fig.tight_layout()
    p = os.path.join(OUT, f"ana_{rid}_gatemap_{tag}.png")
    fig.savefig(p, dpi=120); plt.close(fig); print("wrote", p)

def render_fan(rid, dlabel, tag, ch=1):
    d = load(rid); m = d["_meta"]
    nf = len(m["fast_setpoints"][0]); ns = len(m["slow_setpoints"][0])
    Vtg = np.asarray(m["fast_setpoints"][0]); Vbg = np.asarray(m["fast_setpoints"][1])
    B = np.asarray(m["slow_setpoints"][0])
    n, _ = calc_nD(Vtg, Vbg); n12 = n * 1e-16
    R = Rxx(d, ch)
    # row-major: slow (B) outer, fast (gate-line) inner. Handle interrupted fans
    # by reshaping only the complete B-rows.
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
    render_gatemap(26, "B = 3 T (latest result)", "3T")
    render_gatemap(25, "B = 0 T (context)", "0T")
    render_fan(27, "D = 0, 0->8 T", "D0")
    render_fan(31, "D = 0, 13->0 T, Si = +60 V", "D0_13T")
