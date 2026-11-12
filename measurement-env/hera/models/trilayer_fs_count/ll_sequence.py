#!/usr/bin/env python3
"""ABA Landau-level fan + QH/Streda sequence, to ground the high-field stacking
discriminator: a pseudo-decoupled ML Dirac band shifts the Chern (Streda-slope)
sequence — "trivial" gaps acquire a slope.

Uses the validated ABA SWMcC LL model (ll_spectrum.py, this directory).
Run: uv run --no-project --with numpy --with scipy --with matplotlib python3 ll_sequence.py
"""
import numpy as np, scipy.constants as cst
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import ll_spectrum as L

p = L.SWMcC()
HE = cst.e / cst.h            # eB/h per Tesla = states/area per LL

# ---- LL fan E(B), tagged ML/BL ----
Bs = np.linspace(0.2, 14, 120)
fanE, fanML, fanB = [], [], []
for B in Bs:
    for s in L.all_levels(B, p, nmax=80, drop_top=8):
        if abs(s.energy) < 0.07:
            fanE.append(s.energy*1e3); fanML.append(s.ml_weight); fanB.append(B)
fanE, fanML, fanB = map(np.array, (fanE, fanML, fanB))

fig, ax = plt.subplots(figsize=(6, 4.5))
sc = ax.scatter(fanB, fanE, c=fanML, s=6, cmap="coolwarm", vmin=0, vmax=1)
plt.colorbar(sc, label="ML weight (1=monolayer Dirac)")
ax.set_xlabel("B (T)"); ax.set_ylabel("E (meV)"); ax.set_ylim(-60, 60)
ax.set_title("ABA LL fan: ML (red, ~√B, incl. non-dispersing N=0) + BL (blue, ~linear)")
fig.tight_layout(); fig.savefig("aba_LL_fan.png", dpi=130); plt.close(fig)

# ---- QH / Streda sequence at high field ----
# Chern number of a gap = (spin 2) x (# LLs below it, both valleys already included).
def sequence(B):
    lv = sorted(L.all_levels(B, p, nmax=90, drop_top=10), key=lambda s: s.energy)
    E = np.array([s.energy for s in lv]); mlw = np.array([s.ml_weight for s in lv])
    # cumulative count below each gap, referenced so that nu=0 sits at the CNP
    n0 = int(np.sum(E < 0))                       # levels below E=0 (CNP reference)
    rows = []
    for i in range(len(E)-1):
        if abs(E[i]) < 0.05:
            nu = 2*((i+1) - n0)                   # filling factor at the gap above level i
            gap = (E[i+1]-E[i])*1e3
            rows.append((E[i]*1e3, nu, gap, mlw[i]))
    return rows

print("=== ABA QH sequence at B = 12 T (gap energy meV | nu | gap meV | ML wt of lower level) ===")
for e, nu, gap, ml in sequence(12.0):
    tag = "ML" if ml > 0.6 else ("BL" if ml < 0.4 else "mix")
    print(f"   E={e:7.2f}   nu={nu:+3d}   gap={gap:5.2f}   [{tag}]")

# ---- Wannier/Streda diagram: gap density n(B) lines ----
fig, ax = plt.subplots(figsize=(6, 4.5))
for B in np.linspace(2, 14, 40):
    for e, nu, gap, ml in sequence(B):
        if gap > 0.3 and abs(nu) <= 12:           # resolvable gaps near CNP
            n = nu * HE * B / 1e16                 # density in 1e12 cm^-2
            ax.plot(B, n, ".", c="C3" if ml > 0.6 else "C0", ms=4)
ax.set_xlabel("B (T)"); ax.set_ylabel("n (10$^{12}$ cm$^{-2}$)")
ax.set_title("ABA Wannier/Streda: gap lines n=nu*(eB/h).\nslopes = Chern #; red=ML-edged (Dirac-shifted)")
ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig("aba_wannier.png", dpi=130); plt.close(fig)
print("\nwrote: aba_LL_fan.png, aba_wannier.png")
