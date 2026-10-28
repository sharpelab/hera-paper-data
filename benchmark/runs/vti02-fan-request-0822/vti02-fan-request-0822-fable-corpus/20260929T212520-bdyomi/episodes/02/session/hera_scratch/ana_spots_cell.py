"""sdh-spot-check read — run 6 (electron, n = +3.2e12, D = 0) and run 7 (hole, n = -1.2e12, D = 0).
Raw first, then the detrended 1/B record and the FFT read against F_L and the
tetralayer forward model (hera/models/tetralayer_fs_count/fs_count_b0.py).
Onset/tone tracking via hera.analysis.sdh_onset; FFT via sdh_fft (bg poly in B, FFT in 1/B).
"""
import sys
if "/home/hera/measurement_env/hera/models/tetralayer_fs_count" not in sys.path:
    sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as fs
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency

R_FS = 50e-6 / 10e-9          # sr1 sensitivity / I_bias = 5 kOhm full scale (both runs)
SPOTS = {6: +3.2e16, 7: -1.2e16}  # m^-2, from the run-5 calibration

fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for row, (rid, nspot) in enumerate(SPOTS.items()):
    run = open_run(f"data/{rid}")
    mc = run.meta["measurement_config"]
    B = run.col("magnet_field")
    I = run.col("sr0_X") / float(mc["sr0_gain"])         # measured drain current
    R = (run.col("sr1_X") / float(mc.get("sr1_gain", 1))) / I
    o = np.argsort(B); B, R = B[o], R[o]

    FL = float(luttinger_frequency(nspot))
    on = sdh_onset(R, B, r_full_scale=R_FS)
    print(f"===== run {rid}  n = {nspot/1e16:+.2f}e12 cm^-2  F_L = {FL:.1f} T =====")
    print(on.summary())
    bmax = on.clip_high_b if on.clip_high_b else B.max()
    dF = 1.0 / (1.0 / on.onset_b - 1.0 / bmax)
    print(f"onset_b = {on.onset_b:.3f} T ({'censored at record edge' if any(t.censored for t in on.tones) else 'measured'}), "
          f"deltaF = {dF:.2f} T over [{on.onset_b:.2f}, {bmax:.1f}] T")

    # model tones at this density
    _, ab = fs.abab_fs(nspot); ms = fs.abab_mstar(nspot)
    _, topo, _, _, Fa = fs.abca_fs(nspot)
    print("model ABAB:", ", ".join(f"{F:.1f} T (m* {m:.3f})" for (F, _), (_, m) in zip(ab, ms)),
          f"| ABCA singleton: {Fa:.1f} T ({topo})")

    f, spec = sdh_fft(R[:, None], B, b_range=(1.2 * on.onset_b, bmax), bg_degree=5, log=False)
    sp = spec[0]

    ax = axes[row]
    ax[0].plot(B, R, lw=0.5)
    ax[0].set(xlabel="B [T]", ylabel="Rxx [Ohm]", title=f"run {rid} raw  n = {nspot/1e16:+.1f}e12")
    sel = (B >= on.onset_b) & (B <= bmax)
    dR = R[sel] - np.polyval(np.polyfit(B[sel], R[sel], 5), B[sel])
    ax[1].plot(1 / B[sel], dR, lw=0.6)
    ax[1].set(xlabel="1/B [1/T]", ylabel="dRxx [Ohm]", title=f"detrended, B > {on.onset_b:.2f} T")
    ax[2].plot(f, sp, lw=0.8)
    ax[2].axvline(FL, color="k", ls="--", label=f"F_L = {FL:.1f} T")
    for (F, _) in ab:
        ax[2].axvline(F, color="tab:red", ls=":", alpha=0.8)
    ax[2].axvline(Fa, color="tab:green", ls="-.", alpha=0.6)
    zoom = (f > 2) & (f < 1.4 * FL)
    ax[2].set(xlim=(0, 1.4 * FL), ylim=(0, 1.2 * sp[zoom].max()),
              xlabel="F [T]", ylabel="|FFT|", title="FFT in 1/B (red ABAB, green ABCA)")
    ax[2].legend()
fig.tight_layout()
plt.show()
