"""Runs 6 + 7 — sdh-spot-check at D = 0 (`sdh-spot-check`): raw -> onset -> FFT vs F_L.
Run 6: electron, n = +3.2e12 (Vtg +0.9836, Vbg +1.1661), B 0->10 T (50 mT to 1 T, 10 mT above).
Run 7: hole, n = -1.2e12 (Vtg -0.2770, Vbg -0.4650), B 10->0.3 T, 20 mT (ride-down)."""
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft

I_BIAS = 10e-9
RFS = 50e-6 / I_BIAS                                  # 5 kOhm full scale (sr1 gain 1)
H4E = 6.62607015e-34 / (4 * 1.602176634e-19)          # h/4e, T m^2

spots = {6: +3.2e16, 7: -1.2e16}                      # m^-2
fig, axes = plt.subplots(2, 3, figsize=(15, 7.5))
onsets = {}
for i, (fid, n) in enumerate(spots.items()):
    r = open_run(f"data/{fid}")
    B, R = r.col("magnet_field"), r.col("sr1_X") / I_BIAS
    o = np.argsort(B); B, R = B[o], R[o]
    FL = H4E * abs(n)

    # raw FIRST
    ax = axes[i, 0]
    ax.plot(B, R, lw=0.6)
    ax.set(xlabel="B (T)", ylabel=r"$R_{xx}$ ($\Omega$)",
           title=f"run {fid} raw — n = {n/1e16:+.1f}e12, D = 0")

    # onset (tone-tracked; r_full_scale guards soft clip)
    on = sdh_onset(R, B, r_full_scale=RFS)
    onsets[fid] = on
    print(f"===== run {fid}: n = {n/1e16:+.1f}e12, F_L = {FL:.1f} T =====")
    print(on.summary())

    # background-subtracted (poly deg 5 in B) over the usable record
    cut = max(on.onset_b, 0.8)
    m = B >= cut
    p = np.polyfit(B[m], R[m], 5)
    ax = axes[i, 1]
    ax.plot(B[m], R[m] - np.polyval(p, B[m]), lw=0.6)
    ax.set(xlabel="B (T)", ylabel=r"$\Delta R_{xx}$ ($\Omega$)",
           title=f"run {fid} bg-subtracted (deg 5, cut {cut:.2f} T)")

    # FFT in 1/B, two cuts (stability)
    ax = axes[i, 2]
    for c in (cut, cut + 0.5):
        mm = B >= c
        freqs, spec = sdh_fft(R[mm][:, None], B[mm], b_range=(c, B.max()), bg_degree=5)
        ax.plot(freqs, spec[0] / spec[0].max(), lw=0.9, label=f"cut {c:.2f} T")
    ax.axvline(FL, color="k", ls=":", label=f"$F_L$ = {FL:.1f} T")
    ax.set(xlim=(0, 1.6 * FL), xlabel="F (T)", ylabel="FFT (norm)",
           title=f"run {fid} FFT in 1/B")
    ax.legend(fontsize=7)
    dF = 1 / (1 / cut - 1 / B.max())
    print(f"record above {cut:.2f} T -> dF = {dF:.2f} T\n")

plt.tight_layout(); plt.show()

# model comparison at the electron spot (fs_count_b0, brief-designated arc-reader)
import sys
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from fs_count_b0 import abab_fs, abca_fs
_, orbs = abab_fs(3.2e16)
_, _, _, _, f_abca = abca_fs(3.2e16)
fl = H4E * 3.2e16
print(f"model @ n=+3.2e12: ABAB pair {orbs[0][0]:.1f} / {orbs[1][0]:.1f} T (partition "
      f"{orbs[0][0]/fl:.2f}/{orbs[1][0]/fl:.2f}); ABCA singleton {f_abca:.1f} T; F_L {fl:.1f} T")
print(f"measured run 6 (cut 0.80): tones 7.1 / 22.1 / 29.5 T; 7.1+22.1 = 29.2 = {29.2/fl:.2f} F_L "
      f"(scale prior 0.8-1.2 OK); partition 7.1/29.2 = {7.1/29.2:.2f}, 22.1/29.2 = {22.1/29.2:.2f}")
