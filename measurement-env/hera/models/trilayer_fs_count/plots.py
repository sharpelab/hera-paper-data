#!/usr/bin/env python3
"""Plots for the stacking-extraction FS-counting study (see fs_count_b0.py).
Run: uv run --no-project --with numpy --with scipy --with matplotlib python3 plots.py"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from fs_count_b0 import (aba_bands, aba_fs, abc_fs, E_abc, H_aba, VF, V0,
                         HBAR, E, F_from_area)

OUT = "."
h_e = 6.626e-34 / 1.6e-19  # h/e  (T m^2)

# ---- 1. ABA E vs k line cut (D=0 and finite U), E_F both signs ----
kg = np.linspace(0, 4.5e8, 800)
fig, axes = plt.subplots(1, 2, figsize=(9, 4.4), sharey=True)
for ax, U, ttl in [(axes[0], 0.0, "ABA  D=0"), (axes[1], 0.020, "ABA  U=20 meV")]:
    Eb = aba_bands(kg, U)
    for b in range(6):
        ax.plot(kg/1e8, Eb[b]*1e3, lw=1.3)
    EFe, fse = aba_fs(2e16, U=U)
    EFh, fsh = aba_fs(-2e16, U=U)
    ax.axhline(EFe*1e3, ls="--", c="k", lw=1,
               label=f"E_F(+2e12)={EFe*1e3:.0f} meV ({len(fse)} FS)")
    ax.axhline(EFh*1e3, ls="--", c="0.45", lw=1,
               label=f"E_F(−2e12)={EFh*1e3:.0f} meV ({len(fsh)} FS)")
    ax.set_title(ttl); ax.set_xlabel("k (10^8 m$^{-1}$)")
    ax.set_ylim(-90, 90); ax.legend(fontsize=8)
axes[0].set_ylabel("E (meV)")
fig.suptitle("ABA bands: ML (light) + BL (heavy) coexist, both signs; finite D hybridizes/merges them")
fig.tight_layout(); fig.savefig(f"{OUT}/aba_bands_linecut.png", dpi=130); plt.close(fig)

# ---- 2. ABC E vs k along KM (phi=0) and KK' (phi=pi/3), both branches ----
k = np.linspace(0, 2.6e8, 600)
fig, ax = plt.subplots(figsize=(5, 4.4))
for phi, lab, c in [(0.0, "φ=0", "C0"), (np.pi/3, "φ=π/3", "C1")]:
    Ep = E_abc(k*np.cos(phi), k*np.sin(phi)) * 1e3
    Em = E_abc(k*np.cos(phi), k*np.sin(phi), band=-1) * 1e3
    ax.plot(k/1e8, Ep, label=f"E$^+$ {lab}", lw=1.5, c=c)
    ax.plot(k/1e8, Em, label=f"E$^-$ {lab}", lw=1.5, c=c, ls="--")
ax.set_xlabel("k (10^8 m$^{-1}$)"); ax.set_ylabel("E (meV)")
ax.set_title("ABC bands (MacDonald 2-band), E$^+$ and E$^-$\ntrigonal warping → direction-dependent")
ax.legend(fontsize=8); ax.set_ylim(-40, 40)
fig.tight_layout(); fig.savefig(f"{OUT}/abc_bands_linecut.png", dpi=130); plt.close(fig)

# ---- 3. ABC band contourf (kx,ky) + FS contours, E+ electrons / E- holes ----
kx = np.linspace(-2.6e8, 2.6e8, 500); KX, KY = np.meshgrid(kx, kx)
fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.4))
for ax, band, sgn, ttl in [(axes[0], +1, +1, "E$^+$; electron FS @ n=+0.4(w)/+1.0(r)/+2.0(orange)×10¹²"),
                           (axes[1], -1, -1, "E$^-$; hole FS @ n=−0.4(w)/−1.0(r)/−2.0(orange)×10¹²")]:
    Eg = E_abc(KX, KY, band=band) * 1e3
    vlim = dict(vmax=25) if band > 0 else dict(vmin=-25)
    cf = ax.contourf(KX/1e8, KY/1e8, Eg, levels=40, cmap="viridis", **vlim)
    plt.colorbar(cf, ax=ax, label=f"E$^{'+' if band>0 else '-'}$ (meV)")
    for n, c in [(0.4e16, "w"), (1.0e16, "r"), (2.0e16, "orange")]:
        EF, *_ = abc_fs(sgn*n)
        ax.contour(KX/1e8, KY/1e8, Eg, levels=[EF*1e3], colors=c, linewidths=1.6)
    ax.set_xlabel("k$_x$ (10^8 m$^{-1}$)"); ax.set_ylabel("k$_y$ (10^8 m$^{-1}$)")
    ax.set_title(ttl, fontsize=9)
    ax.set_aspect("equal")
fig.suptitle("ABC Lifshitz cascade, both signs (hole-side cascade sits higher: single only by |n|≈1.6e12)")
fig.tight_layout(); fig.savefig(f"{OUT}/abc_bands_contour.png", dpi=130); plt.close(fig)

# ---- 4. Luttinger: frequencies + orbit count vs n at D=0, both signs ----
side = np.concatenate([np.linspace(0.2, 3.0, 15), np.linspace(3.5, 8.0, 10)]) * 1e16
ns = np.concatenate([-side[::-1], side])
kg6 = np.linspace(1e3, 6e8, 6000)
Eb6 = aba_bands(kg6)
aba_lo, aba_hi, aba_cnt, aba_sum, abc_f = [], [], [], [], []
for n in ns:
    EF, fs = aba_fs(n)
    freqs = sorted(F for F, _ in fs)
    aba_cnt.append(len(fs))
    aba_hi.append(freqs[-1])
    aba_lo.append(freqs[-2] if len(freqs) > 1 else np.nan)
    # signed orbit sum (electron crossings +, hole crossings −): the Luttinger check
    tot = 0.0
    for b in range(6):
        cross = np.where((Eb6[b, :-1]-EF)*(Eb6[b, 1:]-EF) < 0)[0]
        for c in cross:
            s = 1.0 if Eb6[b, c+1] > Eb6[b, c] else -1.0
            tot += s * F_from_area(np.pi*kg6[c]**2)
    aba_sum.append(abs(tot))
    abc_f.append(abc_fs(n)[4])
ns12 = ns/1e16
F_L = h_e * np.abs(ns) / 4.0
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6), sharex=True,
                               gridspec_kw={"height_ratios": [3, 1]})
ax1.plot(ns12, aba_hi, "o-", c="C0", ms=3.5, label="ABA BL (dominant)")
ax1.plot(ns12, aba_lo, "s-", c="C1", ms=3.5, label="ABA ML (small)")
ax1.plot(ns12, abc_f, "^-", c="C3", ms=3.5, label="ABC single = total")
ax1.plot(ns12, aba_sum, "o", mfc="none", mec="0.2", ms=6, label="ABA signed sum $\\Sigma_\\pm F$")
ax1.plot(ns12, F_L, ":", c="0.2", lw=1.2, zorder=5, label="Luttinger $(h/4e)|n|$")
ax1.set_ylabel("SdH frequency (T)"); ax1.legend(fontsize=8); ax1.grid(alpha=.3)
ax1.set_title("Luttinger, both signs: ABA(BL)+ABA(ML) = ABC(total) = (h/4e)|n|.\n"
              "Discriminator = the small ML tone (more balanced on the hole side)")
ax2.step(ns12, aba_cnt, where="mid", c="C0", label="ABA #orbits")
ax2.axhline(1, ls=":", c="C3"); ax2.set_yticks([1, 2, 3])
ax2.set_xlabel("n (10¹² cm$^{-2}$)"); ax2.set_ylabel("ABA #orbits"); ax2.grid(alpha=.3)
fig.tight_layout(); fig.savefig(f"{OUT}/luttinger_vs_n.png", dpi=130); plt.close(fig)

print("wrote: aba_bands_linecut.png, abc_bands_linecut.png, abc_bands_contour.png, luttinger_vs_n.png")
