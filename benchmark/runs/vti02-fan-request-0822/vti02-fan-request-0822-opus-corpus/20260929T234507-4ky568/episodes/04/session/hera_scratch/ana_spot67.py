"""Spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).

Onset + FFT tone content per sdh-spot-check Verify. Raw first, then the read.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import hera.analysis as A
from hera.analysis import (open_run, summarize_run, sdh_onset, sdh_fft,
                           luttinger_frequency, resolve_channels, current_channel,
                           SdhOnsetError)

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"
SPOTS = ((6, "electron", +3.20e12), (7, "hole", -1.20e12))

fig, axes = plt.subplots(2, 3, figsize=(16, 8))
out = {}

for row, (fid, nlabel, nval) in enumerate(SPOTS):
    run = open_run(f"{BASE}/{fid}")
    chans = resolve_channels(run.meta)
    cur = current_channel(chans)
    print("=" * 72)
    print(f"RUN {fid} — {nlabel}, n = {nval:+.3e} cm^-2")
    for c in chans:
        print(f"   {c.col}  cid={c.cid} gain={c.gain} label={c.label} is_current={c.is_current}")

    B = run.col("magnet_field")
    I = run.col(cur.col) / cur.gain
    vch = [c for c in chans if not c.is_current and c.col in run.cols]
    # sr1 is the Rxx channel (device card); sr2/sr3 n.c.
    c1 = [c for c in vch if c.cid in ("sr1", "sr830_1")][0]
    V = run.col(c1.col) / c1.gain
    R = V / I
    order = np.argsort(B)
    B, R, I = B[order], R[order], I[order]
    T = run.col("T_sample")[order]
    print(f"   B {B.min():.3f}..{B.max():.3f} T, N={len(B)}")
    print(f"   I_meas med {np.median(I)*1e9:.3f} nA (ptp {np.ptp(I)*1e9:.3f} nA)")
    print(f"   R: min {np.nanmin(R):.1f}  max {np.nanmax(R):.1f}  at B=0-edge {R[0]:.1f} Ohm")
    print(f"   T_sample {T.min():.3f}..{T.max():.3f} K")
    sens = 50e-6  # set in the measure cell (both spot checks)
    print(f"   sr1_sens {sens}; R_full_scale = {sens/np.median(np.abs(I)):.1f} Ohm")
    igt = np.abs(run.col("k_2400_tg_curr")); igb = np.abs(run.col("k_2400_bg_curr"))
    print(f"   |I_tg| max {igt.max()*1e12:.1f} pA, |I_bg| max {igb.max()*1e12:.1f} pA")

    ax = axes[row, 0]
    ax.plot(B, R, lw=0.7)
    ax.set_xlabel("B (T)"); ax.set_ylabel("R_xx (Ohm)")
    ax.set_title(f"run {fid} raw — {nlabel} n={nval:+.2e}")

    # --- onset ---
    r_fs = None if sens is None else sens / np.median(np.abs(I))
    try:
        on = sdh_onset(R, B, r_full_scale=r_fs)
        print(on.summary())
        out[fid] = on
    except SdhOnsetError as e:
        print(f"   SdhOnsetError: {e}")
        out[fid] = None

    # --- FFT over a few cutoffs (stability sweep) ---
    F_L = float(luttinger_frequency(abs(nval)))
    print(f"   F_L = (h/4e)*n = {F_L:.2f} T")
    ax = axes[row, 1]
    for cutoff in (1.0, 1.5, 2.0, 3.0, 4.0):
        if cutoff >= B.max():
            continue
        try:
            f, spec = sdh_fft(R[:, None], B, b_range=(cutoff, B.max()), bg_degree=5)
        except Exception as e:
            print(f"   fft cutoff {cutoff}: {e}"); continue
        s = spec[0]
        ax.plot(f, s, lw=0.9, label=f"cut {cutoff} T")
        pk = f[(s > 0) & (f > 2)]
        # top 5 local maxima
        sm = s.copy()
        idx = np.argsort(sm)[::-1]
        picked = []
        for i in idx:
            if f[i] < 2:
                continue
            if all(abs(f[i] - p) > 1.5 for p in picked):
                picked.append(f[i])
            if len(picked) >= 5:
                break
        print(f"   fft cut {cutoff:.1f}->{B.max():.1f} T: top peaks (T) "
              + ", ".join(f"{p:.2f}({p/F_L:.3f}F_L)" for p in sorted(picked, reverse=True)))
    ax.set_xlim(0, max(60, F_L * 1.8)); ax.axvline(F_L, color="k", ls="--", lw=1, label="F_L")
    ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (log)"); ax.legend(fontsize=7)
    ax.set_title(f"run {fid} FFT stability (bg_degree=5)")

    # --- background-subtracted trace vs 1/B ---
    ax = axes[row, 2]
    m = B > 0.5
    p = np.polyfit(B[m], R[m], 5)
    ax.plot(1 / B[m], R[m] - np.polyval(p, B[m]), lw=0.7)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dR (Ohm)")
    ax.set_title(f"run {fid} bg-subtracted vs 1/B")

plt.tight_layout()
plt.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot67.png", dpi=110)
print("saved spot67.png")
