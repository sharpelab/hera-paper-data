"""Runs 6 & 7 — sdh-spot-check (electron n=+3.2e12, hole n=-1.2e12, D=0): raw, onset, FFT vs model."""
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as fs
from hera.analysis import (open_run, resolve_channels, current_channel,
                           sdh_onset, sdh_fft, luttinger_frequency)

RUNS = {6: +3.2e16, 7: -1.2e16}   # n (SI, m^-2) at D = 0, run-5 calibration


def rxx(rid):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field")
    ch = resolve_channels(r.meta)
    cur = current_channel(ch)
    v = [c for c in ch if not c.is_current][0]
    R = (r.col(v.col) / v.gain) / (r.col(cur.col) / cur.gain)
    o = np.argsort(B)
    return B[o], R[o]


fig, axes = plt.subplots(2, 3, figsize=(16, 8.5))
onsets = {}
for row, (rid, n_SI) in enumerate(RUNS.items()):
    B, R = rxx(rid)
    F_L = float(luttinger_frequency(n_SI))
    _, orbs = fs.abab_fs(n_SI)
    _, _, _, _, F_abca = fs.abca_fs(n_SI)

    # onset on the clean 10 mT record (>= 1 T) for run 6; full record for run 7 (20 mT throughout)
    b_lo_rec = 1.0 if rid == 6 else 0.3
    onset = sdh_onset(R[B >= b_lo_rec - 1e-9], B[B >= b_lo_rec - 1e-9], b_lo=b_lo_rec)
    onsets[rid] = onset
    print(f"run {rid}: n = {n_SI/1e16:+.1f}e12, F_L = {F_L:.1f} T | ABAB model "
          f"{[f'{f:.1f}' for f, _ in orbs]} T, ABCA {F_abca:.1f} T | onset_b = {onset.onset_b:.2f} T")
    for t in onset.tones:
        if t.contrast > 50:
            print(f"  F = {t.freq:5.2f} T  contrast {t.contrast:6.1f}  onset {t.onset_b:.2f} T"
                  f"  censored={t.censored}  harmonic_flag={t.harmonic_of}")

    ax = axes[row, 0]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {rid} raw — n = {n_SI/1e16:+.1f}e12, D = 0")

    ax = axes[row, 1]
    m = B >= 0.55
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax.plot(1 / B[m], R[m] - bg, lw=0.6)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)"); ax.set_title("detrended (deg-5 in B)")

    ax = axes[row, 2]
    b_fft = max(onset.onset_b, 0.7)
    f_ax, P = sdh_fft(R[:, None], B, b_range=(b_fft, B.max()), nfft=4096)
    P = np.asarray(P).reshape(-1, len(f_ax))[0]
    ax.plot(f_ax, P, lw=0.8)
    ax.axvline(F_L, color="k", ls="--", lw=1, label=f"F_L = {F_L:.1f} T (g=4)")
    for f, _ in orbs:
        ax.axvline(f, color="tab:red", ls=":", lw=1)
    ax.axvline(F_abca, color="tab:green", ls="-.", lw=1)
    ax.set_xlim(0, max(1.6 * F_L, 50)); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (log-R detrend)")
    ax.legend(fontsize=8); ax.set_title(f"FFT B in [{b_fft:.2f}, 10] T — red ABAB / green ABCA model")

fig.tight_layout(); plt.show()

# --- global density-rescale pin (Verify: single scale fit to the WHOLE tone set) ---
meas = {+3.2e16: (7.11, 22.08),   # heavy tone un-flagged: dropping it as a 3.1x harmonic breaks the Luttinger sum
        -1.2e16: (4.72, 6.59)}

def cost(s):
    c = 0.0
    for n, (fl, fh) in meas.items():
        Fs = sorted(f for f, _ in fs.abab_fs(s * n)[1])
        if len(Fs) < 2:
            return np.inf
        c += ((Fs[0] - fl) / fl) ** 2 + ((Fs[-1] - fh) / fh) ** 2
    return c

ss = np.arange(0.80, 1.01, 0.01)
s_best = ss[int(np.argmin([cost(s) for s in ss]))]
print(f"\nglobal density rescale s = {s_best:.2f} (lever-arm prior band 0.8-1.2)")
for n, (fl, fh) in meas.items():
    F_L = float(luttinger_frequency(abs(n)))
    Fs = sorted(f for f, _ in fs.abab_fs(s_best * n)[1])
    print(f"  n = {n/1e16:+.1f}e12: measured ({fl:.2f}, {fh:.2f}) sum {fl+fh:.1f} = {(fl+fh)/F_L:.2f} F_L,"
          f" partition {fl/(fl+fh):.2f}/{fh/(fl+fh):.2f} | ABAB model at s*n: ({Fs[0]:.1f}, {Fs[-1]:.1f})")
