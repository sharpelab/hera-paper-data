#!/usr/bin/env python3
"""
Validation figures for the ABA-TLG LL model, to compare against Datta et al.:
  - fig3a_spectrum.png : LL energy vs B, ML (red) / BL (black) -> matches Fig 3a
  - fig2b_dos.png      : calculated DOS(n, B) with N_M crossing chains -> Fig 2b
  - fig2b_loci.png     : explicit ML x BL crossing loci over the DOS map

Run: uv run --no-project --with numpy --with scipy --with matplotlib python3 validate.py
"""
from __future__ import annotations

import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ll_spectrum moved to hera/models/trilayer_fs_count (2026-07-16); make it importable
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                  "..", "..", "..", "models", "trilayer_fs_count"))
from ll_spectrum import SWMcC
from crossing_model import spectrum_vs_B, dos_map, crossing_loci

OUT = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(OUT, exist_ok=True)
P = SWMcC()


def fig3a_spectrum():
    B = np.linspace(0.02, 8.0, 240)
    spec = spectrum_vs_B(P, B, emax=0.12)
    fig, ax = plt.subplots(figsize=(6, 5))
    for Bi, (en, ml) in zip(B, spec):
        col = np.where(ml > 0.5, "tab:red", "k")
        ax.scatter(np.full_like(en, Bi), en * 1e3, s=1.2, c=col, linewidths=0)
    ax.set_xlabel("B (T)"); ax.set_ylabel("E (meV)")
    ax.set_ylim(-120, 120)
    ax.set_title("ABA-TLG LL spectrum (red=ML, black=BL)  — cf. Datta Fig 3a")
    ax.axhline(0, color="0.7", lw=0.5)
    fig.tight_layout()
    p = os.path.join(OUT, "fig3a_spectrum.png")
    fig.savefig(p, dpi=130); plt.close(fig); print("wrote", p); return p


def fig3a_lowB():
    """Zoom to the low-field crossing region, like Fig 3a inset."""
    B = np.linspace(0.02, 2.0, 200)
    spec = spectrum_vs_B(P, B, emax=0.08)
    fig, ax = plt.subplots(figsize=(6, 5))
    for Bi, (en, ml) in zip(B, spec):
        col = np.where(ml > 0.5, "tab:red", "k")
        ax.scatter(np.full_like(en, Bi), en * 1e3, s=1.6, c=col, linewidths=0)
    ax.set_xlabel("B (T)"); ax.set_ylabel("E (meV)")
    ax.set_ylim(-70, 70)
    ax.set_title("LL spectrum, low-B crossing region (red=ML, black=BL)")
    ax.axhline(0, color="0.7", lw=0.5)
    fig.tight_layout()
    p = os.path.join(OUT, "fig3a_lowB.png")
    fig.savefig(p, dpi=130); plt.close(fig); print("wrote", p); return p


def fig2b_dos(nmax=60):
    # Paper Fig 2b window: low B (0.5..1.5 T), positive density side.
    n12 = np.linspace(0.0, 9.0, 600)
    B = np.linspace(0.3, 1.5, 160)
    dos = dos_map(P, n12, B, nmax=nmax, broaden_meV=0.8)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    pm = ax.pcolormesh(n12, B, dos, cmap="magma", shading="auto")
    fig.colorbar(pm, ax=ax, label="calc. DOS (arb.)")
    ax.set_xlabel(r"$n$ ($10^{12}$ cm$^{-2}$)"); ax.set_ylabel("B (T)")
    ax.set_title("Calculated DOS(n,B), low field — cf. Datta Fig 2b")
    fig.tight_layout()
    p = os.path.join(OUT, "fig2b_dos.png")
    fig.savefig(p, dpi=130); plt.close(fig); print("wrote", p); return p


def fig2b_loci(nmax=60):
    n12 = np.linspace(0.0, 9.0, 500)
    B = np.linspace(0.3, 1.5, 140)
    dos = dos_map(P, n12, B, nmax=nmax, broaden_meV=0.8)
    loci = crossing_loci(P, B, nmax=nmax, emax=0.12)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    pm = ax.pcolormesh(n12, B, dos, cmap="bone", shading="auto", alpha=0.9)
    fig.colorbar(pm, ax=ax, label="calc. DOS (arb.)")
    if loci:
        xs = np.array([d["n12"] for d in loci])
        ys = np.array([d["B"] for d in loci])
        nm = np.array([d["N_M"] for d in loci])
        sc = ax.scatter(xs, ys, c=nm, s=10, cmap="rainbow", vmin=0, vmax=4)
        fig.colorbar(sc, ax=ax, label=r"$N_M$")
    ax.set_xlabel(r"$n$ ($10^{12}$ cm$^{-2}$)"); ax.set_ylabel("B (T)")
    ax.set_xlim(0, 9); ax.set_ylim(0.3, 1.5)
    ax.set_title(r"ML$\times$BL crossing loci, colored by $N_M$ — cf. Fig 2b labels")
    fig.tight_layout()
    p = os.path.join(OUT, "fig2b_loci.png")
    fig.savefig(p, dpi=130); plt.close(fig); print("wrote", p); return p


if __name__ == "__main__":
    fig3a_spectrum()
    fig3a_lowB()
    fig2b_dos()
    fig2b_loci()
