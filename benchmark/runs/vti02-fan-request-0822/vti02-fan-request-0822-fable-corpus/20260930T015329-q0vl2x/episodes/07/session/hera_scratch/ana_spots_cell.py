# Runs 6-7: SdH spot checks at D = 0 -> onset, tones, model overlay (fan design inputs)
import sys
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import (open_run, resolve_channels, sdh_onset, sdh_fft,
                           luttinger_frequency, SdhOnsetError)
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as fsm

I_BIAS = 1.0 / 100e6            # sr1 drive 1.0 V / 100 MOhm
R_FS = 50e-6 / I_BIAS           # 5 kOhm full scale
runs = {6: dict(n=+3.2e16, label="electron n=+3.2e12"),
        7: dict(n=-1.2e16, label="hole n=-1.2e12")}

# --- fig 1: RAW, both runs ---
fig1, ax1 = plt.subplots(1, 2, figsize=(12, 3.6))
for k, (rid, info) in enumerate(runs.items()):
    r = open_run(f"data/{rid}")
    ch = [c for c in resolve_channels(r.meta) if c.cid == "sr1"][0]
    B, R = r.col("magnet_field"), r.col(ch.col) / ch.gain / I_BIAS
    o = np.argsort(B); info["B"], info["R"] = B[o], R[o]
    ax1[k].plot(info["B"], info["R"], lw=0.6)
    ax1[k].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {rid} raw — {info['label']}")
    print(f"run {rid}: R {info['R'].min():.0f}..{info['R'].max():.0f} Ohm "
          f"({info['R'].max()/R_FS:.1%} of 5 kOhm FS)")
fig1.tight_layout(); plt.show()

# --- fig 2: onset + FFT vs model ---
fig2, ax2 = plt.subplots(1, 2, figsize=(12, 4))
for k, (rid, info) in enumerate(runs.items()):
    B, R, n = info["B"], info["R"], info["n"]
    FL = float(luttinger_frequency(n))
    print(f"\n=== run {rid} — {info['label']}, F_L = {FL:.1f} T ===")
    try:
        on = sdh_onset(R, B, r_full_scale=R_FS); print(on.summary())
        b_lo = on.onset_b
    except SdhOnsetError as e:
        print(f"SdhOnsetError: {e}"); b_lo = 1.5
    ax = ax2[k]
    for cut, st in ((max(b_lo, 0.5), "-"), (max(b_lo * 1.4, b_lo + 0.5), "--")):
        freqs, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()))
        ax.plot(freqs, spec[0], st, lw=1, label=f"cut {cut:.2f} T")
    ax.axvline(FL, color="k", ls=":", label=f"F_L {FL:.1f} T")
    _, ab = fsm.abab_fs(n)
    for F, _ in ab:
        ax.axvline(F, color="tab:red", ls="--", alpha=0.6)
    Fa = fsm.abca_fs(n)[4]
    ax.axvline(Fa, color="tab:green", ls="--", alpha=0.6)
    print("model ABAB (F, m*):", [(round(F, 2), round(m, 3)) for F, m in fsm.abab_mstar(n)],
          f" | ABCA F = {Fa:.1f} T, m* = {fsm.abca_mstar(n)[1]:.3f}")
    ax.set(xlim=(0, FL * 1.6), xlabel="F (T)", ylabel="FFT amp",
           title=f"run {rid} FFT in 1/B (red = ABAB, green = ABCA)")
    ax.legend(fontsize=7)
fig2.tight_layout(); plt.show()

# --- model F(n) design table (electron side) — the fan's design authority ---
print("\nmodel F(n), electron side —  n(e12)  F_L    light  heavy  heavy/light  3xlight  m*_l/m*_h")
for nn in (1.0, 1.5, 2.0, 2.5, 3.0, 3.2):
    nm = nn * 1e16
    (_, ab), ms = fsm.abab_fs(nm), fsm.abab_mstar(nm)
    fl_, fh_ = ab[0][0], ab[-1][0]
    print(f"  {nn:4.1f}  {float(luttinger_frequency(nm)):5.1f}  {fl_:5.2f}  {fh_:5.2f}"
          f"  {fh_/fl_:6.2f}      {3*fl_:5.1f}   {ms[0][1]:.3f}/{ms[-1][1]:.3f}")
