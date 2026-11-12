"""SdH spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).

Raw first, then onset (hera.analysis.sdh_onset), then per-window FFT.
Feeds the landau-fan design levers: B_lo (measured onset), tone set, dF.
"""
import json
import warnings

import numpy as np
import scipy.constants as cst
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from hera.analysis import (
    open_run,
    summarize_run,
    sdh_onset,
    sdh_fft,
    luttinger_frequency,
    GateCalibration,
)

D = "/home/hera/measurements/zack/20260822-vti-02"
cal_j = json.load(open(f"{D}/hera_scratch/cal_run5.json"))
cal = GateCalibration(
    c_tg=cal_j["c_tg"],
    c_bg=cal_j["c_bg"],
    n_offset=cal_j["n_offset"] * 1e16,
    D_offset=cal_j["D_offset"] * 1e9,
)


def load(i):
    r = open_run(f"{D}/data/{i}")
    B = r.col("magnet_field")
    # R = (V_xx / gain_xx) / I ,  I = sr0_X / sr0_gain
    mc = r.meta["measurement_config"]
    g0 = mc["sr0_gain"]
    I = r.col("sr0_X") / g0
    V = r.col("sr1_X") / 1.0  # sr1 gain unity (device card)
    R = V / I
    return r, B, R, I


fig, axes = plt.subplots(2, 3, figsize=(16, 8))

out = {}
for k, (i, label, npred) in enumerate(
    [(6, "run 6 — electron n=+3.20e12", +3.20e12), (7, "run 7 — hole n=-1.20e12", -1.20e12)]
):
    r, B, R, I = load(i)
    print("=" * 70)
    print(label)
    print(summarize_run(r))
    o = np.argsort(B)
    Bs, Rs = B[o], R[o]
    print(f"  B {B.min():.3f} -> {B.max():.3f} T, {len(B)} pts")
    print(f"  R: {np.nanmin(R):.1f} .. {np.nanmax(R):.1f} Ohm  (R(B_lo)={Rs[0]:.1f})")
    print(f"  I_meas: {np.nanmedian(I)*1e9:.4f} nA  (ptp {np.ptp(I)*1e9:.4f} nA)")
    print(f"  T_sample {np.nanmin(r.col('T_sample')):.3f}-{np.nanmax(r.col('T_sample')):.3f} K")
    for g in ("k_2400_tg_curr", "k_2400_bg_curr"):
        c = r.col(g)
        print(f"  {g}: med {np.nanmedian(c)*1e12:.0f} pA, min {np.nanmin(c)*1e12:.0f}, max {np.nanmax(c)*1e12:.0f}")
    # sensitivity rail check: 50 uV FS on sr1 -> R_FS = 50e-6 / I
    r_fs = 50e-6 / abs(np.nanmedian(I))
    print(f"  sr1 50 uV FS  ->  R_full_scale = {r_fs:.0f} Ohm; max|R| = {np.nanmax(np.abs(R)):.0f} "
          f"({100*np.nanmax(np.abs(R))/r_fs:.1f} % FS)")

    # --- gate voltages -> actual (n, D)
    ax = axes[k, 0]
    ax.plot(Bs, Rs, lw=0.8)
    ax.set(xlabel="B (T)", ylabel=r"$R_{xx}$ ($\Omega$)", title=f"{label} — RAW")
    ax.grid(alpha=0.3)

    # --- onset
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(Rs, Bs, r_full_scale=r_fs)
            print("\n" + on.summary())
        except Exception as e:
            on = None
            print(f"\n  sdh_onset FAILED: {type(e).__name__}: {e}")
        for w in ws:
            print(f"  [warn] {w.message}")

    F_L = luttinger_frequency(npred * 1e4) if False else abs(npred) * 1e4 * cst.h / (4 * cst.e)
    print(f"\n  F_L(n={npred:.2e} cm^-2) = {F_L:.2f} T")

    # --- FFT: full window above onset, plus low/high B-window split
    b_lo = on.onset_b if on else 1.0
    b_hi = Bs.max()
    b_mid = 1.0 / (0.5 * (1 / b_lo + 1 / b_hi))  # midpoint in 1/B
    ax = axes[k, 1]
    for rng, lab, sty in [
        ((b_lo, b_hi), f"full {b_lo:.2f}-{b_hi:.1f} T", "-"),
        ((b_lo, b_mid), f"low {b_lo:.2f}-{b_mid:.1f} T", "--"),
        ((b_mid, b_hi), f"high {b_mid:.1f}-{b_hi:.1f} T", ":"),
    ]:
        fr, amp = sdh_fft(Rs[:, None], Bs, b_range=rng, nfft=2048, log=False)
        a = amp[0]
        ax.plot(fr, a / np.nanmax(a), sty, lw=1.0, label=lab)
        # local maxima above 2% of peak, in band
        m = (fr > 1.5) & (fr < 2.2 * F_L)
        loc = m & (a > np.roll(a, 1)) & (a > np.roll(a, -1)) & (a > 0.03 * np.nanmax(a[m]))
        pk = fr[loc]
        pa = a[loc] / np.nanmax(a[m])
        order = np.argsort(pa)[::-1][:10]
        print(f"  FFT [{lab}] peaks (T, rel-amp): "
              + ", ".join(f"{pk[j]:.2f}({pa[j]:.2f})" for j in np.sort(order[np.argsort(pk[order])])
                          ) if False else
              f"  FFT [{lab}] peaks: " + ", ".join(
                  f"{pk[j]:.2f}T/{pa[j]:.2f}" for j in order[np.argsort(pk[order])]))
        if sty == "-":
            out[i] = dict(freqs=[float(pk[j]) for j in order[np.argsort(pk[order])]],
                          amps=[float(pa[j]) for j in order[np.argsort(pk[order])]],
                          F_L=float(F_L), onset=float(b_lo), b_hi=float(b_hi))
    ax.axvline(F_L, color="k", lw=1.2, label=f"$F_L$={F_L:.1f} T")
    ax.axvline(0.72 * F_L, color="r", lw=0.8, ls="--", label="0.72/0.28 $F_L$")
    ax.axvline(0.28 * F_L, color="r", lw=0.8, ls="--")
    ax.set(xlabel="F (T)", ylabel="|FFT| (norm)", xlim=(0, 2.0 * F_L),
           title="FFT in 1/B, B-window split")
    ax.legend(fontsize=6)
    ax.grid(alpha=0.3)

    # --- detrended trace vs 1/B (the record the FFT sees)
    ax = axes[k, 2]
    m = Bs >= b_lo
    bg = np.polyval(np.polyfit(Bs[m], Rs[m], 5), Bs[m])
    ax.plot(1 / Bs[m], Rs[m] - bg, lw=0.8)
    ax.set(xlabel="1/B (1/T)", ylabel=r"$\Delta R$ ($\Omega$)",
           title=f"detrended, B>{b_lo:.2f} T")
    ax.grid(alpha=0.3)
    if on:
        print(f"  delta_F over [{b_lo:.2f}, {b_hi:.1f}] T = "
              f"{1/(1/b_lo - 1/b_hi):.2f} T")

plt.tight_layout()
plt.savefig(f"{D}/hera_scratch/spot_runs67.png", dpi=110)
print("\nwrote spot_runs67.png")
json.dump(out, open(f"{D}/hera_scratch/spot_read.json", "w"), indent=1)
