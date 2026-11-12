"""Runs 6 & 7 — sdh-spot-check reads (electron n=+3.2e12, hole n=-1.2e12, D=0).

Raw R(B) first, then sdh_onset per trace, FFT vs F_L and the model F(n) table.
R = (sr1_X/gain) / (sr0_X/gain)  — measured drain current denominator.
"""
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as fs

from hera.analysis import (
    open_run, resolve_channels, current_channel, sdh_onset, sdh_fft,
    luttinger_frequency, SdhOnsetError,
)

RUNS = {
    6: dict(n_cm2=+3.2e12, label="run 6 — electron, n = +3.2e12, B 0→10 T"),
    7: dict(n_cm2=-1.2e12, label="run 7 — hole, n = −1.2e12, B 10→0.3 T"),
}

fig, axes = plt.subplots(2, 3, figsize=(17, 9))
results = {}
for row, (rid, spec) in enumerate(RUNS.items()):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field")
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    vch = [c for c in chans if c is not cur and c.col == "sr1_X"][0]
    I = r.col(cur.col) / cur.gain
    R = (r.col(vch.col) / vch.gain) / I
    order = np.argsort(B)
    B, R, I = B[order], R[order], I[order]

    n_SI = spec["n_cm2"] * 1e4
    F_L = float(luttinger_frequency(n_SI))

    # model tones at this density (F, kF) / (F_total,...)
    _, abab = fs.abab_fs(n_SI)
    _, _, _, _, F_abca = fs.abca_fs(n_SI)
    abab_F = [f for f, _ in abab]

    # onset
    try:
        onset = sdh_onset(R, B)
        onset_b = onset.onset_b
        tones = [(t.freq, t.onset_b, t.censored) for t in onset.tones]
    except SdhOnsetError as e:
        onset, onset_b, tones = None, None, str(e)

    # FFT: heavy-tone window (low-f MR leakage swamps a full-record linear FFT)
    b_lo = max(onset_b if onset_b else 1.5, 0.7)
    f_ax, P = sdh_fft(R[:, None], B, b_range=(b_lo, B.max()), nfft=4096)
    P = np.asarray(P).reshape(-1, len(f_ax))[0]

    results[rid] = dict(F_L=F_L, abab=abab_F, abca=F_abca, onset=onset_b,
                        tones=tones, R0=R[np.argmin(np.abs(B - B.min()))],
                        Rmax=np.nanmax(np.abs(R)))
    print(f"=== {spec['label']} ===")
    print(f"  F_L = {F_L:.1f} T | model ABAB tones {['%.1f' % f for f in abab_F]} | ABCA {F_abca:.1f} T")
    print(f"  R({B.min():.2f} T) = {R[0]:.1f} Ω, |R|max = {np.nanmax(np.abs(R)):.1f} Ω, I_bias med = {np.median(np.abs(I))*1e9:.2f} nA")
    print(f"  onset_b = {onset_b}")
    if onset is not None:
        for t in onset.tones:
            print(f"    tone F={t.freq:6.2f} T  contrast={t.contrast:7.1f}  onset={t.onset_b:.2f} T"
                  f"  censored={t.censored}  marginal={t.marginal}  near_res={t.near_residual}"
                  f"  harmonic_of={t.harmonic_of}")

    ax = axes[row, 0]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ω)"); ax.set_title(spec["label"] + " — raw")

    ax = axes[row, 1]
    m = B >= max(b_lo * 0.8, 0.5)
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax.plot(1.0 / B[m], R[m] - bg, lw=0.6)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("ΔRxx (Ω)")
    ax.set_title(f"detrended, B ≥ {max(b_lo*0.8,0.5):.2f} T")

    ax = axes[row, 2]
    ax.plot(f_ax, P, lw=0.8, label=f"FFT B∈[{b_lo:.2f},{B.max():.1f}] T")
    ax.axvline(F_L, color="k", ls="--", lw=1, label=f"F_L = {F_L:.1f} T")
    for f in abab_F:
        ax.axvline(f, color="tab:red", ls=":", lw=1)
    ax.axvline(F_abca, color="tab:green", ls="-.", lw=1)
    if onset is not None:
        for t in onset.tones:
            if t.contrast > 50:
                ax.annotate(f"{t.freq:.1f}", (t.freq, np.interp(t.freq, f_ax, P)),
                            fontsize=7, color="tab:blue", rotation=90)
    ax.set_xlim(0, max(F_L * 1.6, 50)); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (log-R detrended)")
    ax.legend(fontsize=7)
    ax.set_title("red: ABAB model, green: ABCA model")

fig.tight_layout()
fig.savefig("hera_scratch/spots_runs67.png", dpi=110)
print("saved hera_scratch/spots_runs67.png")
