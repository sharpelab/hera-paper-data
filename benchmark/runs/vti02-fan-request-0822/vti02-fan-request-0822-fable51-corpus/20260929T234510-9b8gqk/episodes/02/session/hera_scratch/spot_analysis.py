"""Spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).
Raw R(B), background-subtracted dR, sdh_onset summary, sdh_fft vs F_L.
"""
import sys, json
import numpy as np
import scipy.constants as cst
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError

GAIN0 = -1e6
I_BIAS = 10e-9
SENS = 50e-6

out = {}
fig, axs = plt.subplots(3, 2, figsize=(13, 11))
for j, (fid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{fid}")
    B = r.col("magnet_field"); I = r.col("sr0_X") / GAIN0; V = r.col("sr1_X")
    R = V / I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    FL = cst.h / (4 * cst.e) * abs(n12) * 1e16
    print(f"\n===== run {fid}: n = {n12:+.1f}e12, F_L = {FL:.1f} T, B {B.min():.2f}-{B.max():.2f} T, N={len(B)}, I_med={np.median(I)*1e9:.2f} nA")
    print(f"R(B<0.5) med {np.median(R[B<0.5]):.1f} Ω; R max {R.max():.1f} Ω at B={B[R.argmax()]:.2f}; R min {R.min():.1f} Ω at B={B[R.argmin()]:.2f}")
    axs[0, j].plot(B, R, lw=0.7); axs[0, j].set_title(f"run {fid} raw R(B), n={n12:+.1f}e12"); axs[0, j].set_xlabel("B (T)"); axs[0, j].set_ylabel("R (Ω)")
    try:
        on = sdh_onset(R, B, r_full_scale=SENS / I_BIAS)
        print(on.summary())
        out[fid] = dict(onset_b=on.onset_b, clip_high_b=on.clip_high_b,
                        tones=[dict(freq=t.freq, onset_b=t.onset_b, censored=t.censored, marginal=t.marginal,
                                    harmonic_of=t.harmonic_of, harmonics=t.harmonics) for t in on.tones],
                        untracked=on.untracked)
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); onset = 1.0; out[fid] = dict(error=str(e))
    # FFT at a few cutoffs
    for cut, deg, ls in [(max(onset, 1.0), 5, "-"), (max(onset, 1.0) + 0.5, 5, "--"), (max(onset, 1.0), 3, ":")]:
        m = B >= cut
        try:
            f, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=deg)
            sp = spec[0] / spec[0].max()
            axs[1, j].plot(f, sp, ls, lw=1, label=f"cut {cut:.2f} T, deg {deg}")
            # peaks
            pk = [(f[i], sp[i]) for i in range(1, len(f) - 1) if sp[i] > sp[i - 1] and sp[i] > sp[i + 1] and sp[i] > 0.08 and f[i] > 2]
            print(f"FFT cut {cut:.2f} deg {deg}: peaks (T, rel) = {[(round(a, 1), round(b, 2)) for a, b in pk][:10]}")
        except Exception as e:
            print("sdh_fft failed", cut, deg, e)
    axs[1, j].axvline(FL, color="k", ls="--", label=f"F_L={FL:.1f}"); axs[1, j].axvline(0.72 * FL, color="r", ls=":", label="0.72 F_L"); axs[1, j].axvline(0.28 * FL, color="r", ls=":")
    axs[1, j].set_xlim(0, 2.2 * FL); axs[1, j].set_xlabel("F (T)"); axs[1, j].legend(fontsize=7)
    # background-subtracted dR vs 1/B
    m = B >= max(onset, 1.0)
    p = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(p, B[m])
    axs[2, j].plot(1 / B[m], dR, lw=0.7); axs[2, j].set_xlabel("1/B (1/T)"); axs[2, j].set_ylabel("ΔR (Ω)"); axs[2, j].set_title("bg-subtracted (deg 5)")
plt.tight_layout(); plt.savefig("hera_scratch/spot_runs67.png", dpi=110)
json.dump(out, open("hera_scratch/spot_onset.json", "w"), indent=1, default=str)
print("saved")
