"""SdH read on the spot checks: run 6 (electron, n=+3.2e12, B 0->10 T) and run 7
(hole, n=-1.2e12, B 10->0.3 T). Raw R(B), tone onsets (sdh_onset), FFT in 1/B
(sdh_fft) vs the stacking model frequencies. Model (from step-2 table, cal run 5):
  electron n=+3.2e12: full-density F_L = 33.1 T; ABAB two-band ~ (7.5, 25.6) T; ABCA single ~33 T
  hole     n=-1.2e12: F_L = 12.4 T; ABAB ~ (5.3, 7.1) T; ABCA ~12.4 T (LK-dead at T_e~8K)
"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, SdhOnsetError

MODEL = {6: dict(FL=33.1, abab=(7.5, 25.6), label="electron n=+3.2e12"),
         7: dict(FL=12.4, abab=(5.3, 7.1), label="hole n=-1.2e12")}

fig, ax = plt.subplots(2, 2, figsize=(12, 7))
for k, rid in enumerate((6, 7)):
    r = open_run(f"data/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    srt = np.argsort(B); B, R = B[srt], R[srt]
    sens = r.meta["measurement_config"].get("sr1_sensitivity", 50e-6)
    rfs = 50e-6 / 10e-9  # 50 uV at 10 nA
    print(f"\n=== run {rid} ({MODEL[rid]['label']}): {len(B)} pts, B {B[0]:.2f}->{B[-1]:.2f} T, "
          f"R {R.min():.1f}..{R.max():.1f} Ohm, interrupted={r.interrupted}")

    ax[k, 0].plot(B, R, lw=0.6)
    ax[k, 0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {rid} raw — {MODEL[rid]['label']}")

    try:
        o = sdh_onset(R, B, r_full_scale=rfs)
        print(o.summary())
        onset = o.onset_b
    except SdhOnsetError as e:
        print(f"sdh_onset FAILED: {e}")
        onset = 3.0

    # FFT over the oscillatory window (onset -> B_max)
    for blo in sorted({max(onset, 1.5), 3.0, 4.5}):
        f, sp = sdh_fft(R[:, None], B, b_range=(blo, B.max()), log=False)
        s = sp[0] / sp[0].max()
        ax[k, 1].plot(f, s, lw=0.8, label=f"B in [{blo:.1f}, {B.max():.0f}] T")
        pk = f[np.argmax(s)]
        top = sorted(zip(s, f), reverse=True)[:6]
        print(f"  FFT b_lo={blo:.1f}: top freqs " + ", ".join(f"{ff:.1f} T ({ss:.2f})" for ss, ff in top))
    m = MODEL[rid]
    for x, c, lab in [(m["FL"], "k", "F_L (single band)")] + [(x, "r", "ABAB pair") for x in m["abab"]]:
        ax[k, 1].axvline(x, color=c, ls="--", lw=0.8, alpha=0.6)
    ax[k, 1].set(xlim=(0, 60), xlabel="F (T)", ylabel="FFT (norm)", title=f"run {rid} SdH FFT (dashed: black F_L, red ABAB)")
    ax[k, 1].legend(fontsize=7)

fig.tight_layout()
fig.savefig("hera_scratch/sdh_spots.png", dpi=110)
print("\nwrote hera_scratch/sdh_spots.png")
