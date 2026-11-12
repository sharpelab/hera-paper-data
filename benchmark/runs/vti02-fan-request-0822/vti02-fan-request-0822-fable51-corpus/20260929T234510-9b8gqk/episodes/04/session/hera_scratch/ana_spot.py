"""Runs 6 + 7 — sdh-spot-check read (Step 3): raw R(B) first, then sdh_onset / sdh_fft in 1/B with F_L and the
tetralayer FS-count model overlays. Electron n = +3.2e12 (run 6, 0 -> 10 T), hole n = -1.2e12 (run 7, 10 -> 0.3 T)."""
import numpy as np, matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, luttinger_frequency

# model (fs_count_b0, SI density) at the two spot densities: ABAB [light, heavy], ABCA singleton = F_L
MODEL = {6: dict(n=+3.2e12, abab=(7.31, 25.78), abca=33.08), 7: dict(n=-1.2e12, abab=(6.54, 5.86), abca=12.41)}
R_FS = 50e-6 / 10e-9   # 50 uV sensitivity / 10 nA = 5 kOhm full scale (both runs)

def load(rid):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field"); I = r.col("sr0_X") / (-1e6); R = np.abs(r.col("sr1_X") / I); T = r.col("T_sample")
    o = np.argsort(B); return r, B[o], R[o], I[o], T[o]

fig, axs = plt.subplots(3, 2, figsize=(14, 12))
for j, rid in enumerate((6, 7)):
    r, B, R, I, T = load(rid); m = MODEL[rid]; FL = float(luttinger_frequency(abs(m["n"]) * 1e4))
    print(summarize_run(r)); print(f"  I_bias {np.median(I)*1e9:.2f} nA, T {T.min():.3f}-{T.max():.3f} K, R {R.min():.1f}-{R.max():.1f} Ohm, F_L = {FL:.2f} T")
    # raw first
    ax = axs[0, j]; ax.plot(B, R, lw=0.7); ax.set_title(f"run {rid}: n = {m['n']/1e12:+.2f}e12, D = 0 — raw |Rxx| (sr1)"); ax.set_xlabel("B (T)"); ax.set_ylabel("R (Ohm)")
    # onset (per-tone tracker), full record
    on = sdh_onset(R, B, r_full_scale=R_FS); print(on.summary())
    # background-subtracted vs 1/B above the onset
    blo = max(on.onset_b, 0.3); sel = B >= blo
    dR = R[sel] - np.polyval(np.polyfit(B[sel], R[sel], 5), B[sel])
    ax = axs[1, j]; ax.plot(1 / B[sel], dR, lw=0.7); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dR (Ohm)")
    ax.set_title(f"deg-5 bg removed, B >= {blo:.2f} T (onset_b {on.onset_b:.2f} T{' — censored' if any(t.censored and abs(t.freq-on.onset_freq)<0.5 for t in on.tones) else ''})")
    # FFT windows: full, low (<= 5 T), high (> 5 T)
    ax = axs[2, j]
    for lab, rng in (("full", (blo, 10.0)), ("low B", (blo, 5.0)), ("high B", (5.0, 10.0))):
        f, sp = sdh_fft(R[:, None], B, b_range=rng, bg_degree=5, log=False); sp = sp[0] / sp[0][f > 2].max()
        ax.plot(f, sp, lw=0.9, label=f"{lab} {rng[0]:.1f}-{rng[1]:.0f} T")
        ip, _ = find_peaks(sp, height=0.1, prominence=0.05); ip = ip[f[ip] > 2]
        print(f"  FFT {lab:7s} {rng[0]:.2f}-{rng[1]:.0f} T (dF {1/(1/rng[0]-1/rng[1]):.2f} T): " + ", ".join(f"{f[i]:.1f} T ({sp[i]:.2f})" for i in ip[:10]))
    ax.axvline(FL, color="k", ls="--", label=f"F_L = {FL:.1f} T (ABCA singleton)")
    for k, Fm in enumerate(m["abab"]): ax.axvline(Fm, color="C3", ls=":", label="model ABAB pair" if k == 0 else None)
    ax.set_xlim(0, 1.25 * FL); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm.)"); ax.legend(fontsize=7); ax.set_title("1/B FFT by field window")
plt.tight_layout(); plt.show()
