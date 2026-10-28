# Runs 6 & 7 — SdH spot checks at D = 0 (`sdh-spot-check` step 6): raw, onset, 1/B FFT vs FS-count templates
import numpy as np, matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft

I_BIAS = 10e-9
R_FS = 50e-6 / I_BIAS   # sr1 50 uV, gain 1 -> 5 kOhm full scale

# Model refs: fs_count_b0 (hera/models/tetralayer_fs_count), computed this session at the spot densities.
MODEL = {6: dict(n=+3.2, F_L=33.09, abab=[(7.31, 0.027), (25.78, 0.061)], abca=(33.08, 0.074)),
         7: dict(n=-1.2, F_L=12.41, abab=[(5.86, 0.074), (6.54, 0.032)], abca=(12.41, 1.122))}
CUTS = {6: (1.0, 1.4, 1.8), 7: (0.71, 0.93, 1.14)}   # FFT low-B cutoffs (stability sweep)
BMIN = {6: 1.0, 7: 0.3}   # run 6 < 1 T is a 50 mT grid: undersamples the 7.1 T tone (aliases) — excluded

fig, axes = plt.subplots(2, 3, figsize=(16, 8.5))
for row, fid in enumerate((6, 7)):
    run = open_run(f"data/{fid}")
    assert not run.interrupted, f"run {fid} interrupted"
    i = np.argsort(run.col("magnet_field"))
    B, R = run.col("magnet_field")[i], run.col("sr1_X")[i] / I_BIAS
    T = run.col("T_sample")
    print(f"=== run {fid}: n = {MODEL[fid]['n']:+.1f}e12, D = 0, {len(B)} pts, "
          f"B {B.min():.2f}->{B.max():.2f} T, T_sample {T.min():.3f}-{T.max():.3f} K ===")
    ax = axes[row]
    ax[0].plot(B, R, lw=0.5)
    ax[0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {fid} raw — n = {MODEL[fid]['n']:+.1f}e12, D = 0")
    m = B >= BMIN[fid]
    dR = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    on = sdh_onset(R, B, r_full_scale=R_FS)
    print(on.summary())
    ax[1].plot(B[m], dR, lw=0.5)
    ax[1].axvline(on.onset_b, color="r", ls="--", lw=1)
    ax[1].set(xlabel="B (T)", ylabel="dRxx (Ohm)",
              title=f"deg-5 poly(B) removed (B >= {BMIN[fid]} T); onset marker {on.onset_b:.2f} T")
    for cut in CUTS[fid]:
        fr, sp = sdh_fft(R[m][:, None], B[m], b_range=(cut, 10.0), bg_degree=5, log=False)
        s = sp[0] / sp[0][fr > 3].max()
        ax[2].plot(fr, s, lw=0.8, label=f"cut {cut:.2f} T")
        if cut == CUTS[fid][1]:
            f3, s3 = fr[fr > 3], sp[0][fr > 3]
            pk, pr = find_peaks(s3, height=0.1 * s3.max(), distance=3)
            top = pk[np.argsort(pr["peak_heights"])[::-1][:6]]
            print(f"FFT peaks (cut {cut:.2f} T, F > 3 T): " + ", ".join(f"{f3[k]:.1f}" for k in top) + " T")
    md = MODEL[fid]
    for F, _ in md["abab"]:
        ax[2].axvline(F, color="k", ls=":", lw=1)
    ax[2].axvline(md["F_L"], color="g", ls="--", lw=1)
    ax[2].set(xlabel="F (T)", ylabel="amp (norm to max > 3 T)", xlim=(0, 45), ylim=(0, 1.6),
              title=f"1/B FFT — dotted: ABAB {md['abab'][0][0]:.1f}/{md['abab'][1][0]:.1f} T; green: F_L {md['F_L']:.1f} T")
    ax[2].legend(fontsize=8)
fig.tight_layout()
plt.show()
