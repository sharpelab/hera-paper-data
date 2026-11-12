"""Read-only, session-local SdH spot-check analysis for runs 6 and 7."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, luttinger_frequency

fig, axs = plt.subplots(2, 2, figsize=(12, 8))
for row, (rid, n) in enumerate([(6, 3.2), (7, -1.2)]):
    run = open_run(f"data/{rid}")
    b = run.col("magnet_field")
    ch = resolve_channels(run.meta)
    cur = current_channel(ch)
    rv = next(c for c in ch if c.cid == "sr1")
    I = run.col(cur.col) / cur.gain
    R = (run.col(rv.col) / rv.gain) / I
    print(f"run {rid}: n={n:+.2f}e12, B={b.min():.2f}-{b.max():.2f} T, R={R.min():.1f}-{R.max():.1f} ohm, I={I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA, T={run.col('T_sample').min():.3f}-{run.col('T_sample').max():.3f} K")
    print(f"  TG current median/max abs = {np.median(run.col('k_2400_tg_curr'))*1e12:.1f}/{np.max(np.abs(run.col('k_2400_tg_curr')))*1e12:.1f} pA; BG = {np.median(run.col('k_2400_bg_curr'))*1e12:.1f}/{np.max(np.abs(run.col('k_2400_bg_curr')))*1e12:.1f} pA")
    f, spec = sdh_fft(R[:, None], b, b_range=(1.5, 10), bg_degree=5, log=False)
    y = spec[0]
    p, _ = find_peaks(y, prominence=0.1*y.max())
    p = sorted(p, key=lambda i: y[i], reverse=True)[:8]
    print("  FFT peaks (1.5-10 T):", [(round(float(f[i]), 2), round(float(y[i]/y.max()), 2)) for i in p])
    print("  full-density F_L:", float(luttinger_frequency(abs(n)*1e16)), "T")
    try:
        o = sdh_onset(R, b, b_hi=10, b_lo=0.5, r_full_scale=5000, bg_degree=5)
        print(o.summary())
    except Exception as e:
        print("  onset failed:", type(e).__name__, str(e))
    axs[row, 0].plot(b, R, lw=0.7)
    axs[row, 0].set(xlabel="B (T)", ylabel="Rxx (ohm)", title=f"run {rid} raw n={n:+.1f}e12")
    axs[row, 1].plot(f, y, lw=0.9)
    axs[row, 1].set(xlim=(0, 60), xlabel="F (T)", ylabel="FFT magnitude", title=f"run {rid}, 1.5-10 T")
    axs[row, 1].axvline(float(luttinger_frequency(abs(n)*1e16)), color="r", ls="--", lw=0.8)
fig.tight_layout()
fig.savefig("hera_scratch/spot_checks.png", dpi=150)
