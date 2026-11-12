"""Runs 6 (e-side n=+3.2e12) and 7 (h-side n=-1.2e12): raw R(B), FFT in 1/B, sdh_onset."""
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_fft, sdh_onset, luttinger_frequency
D = Path("data")
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, rid in enumerate([6, 7]):
    r = open_run(D / str(rid)); print(summarize_run(r)); print(r.cols)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field") if "magnet_field" in r.cols else r.col_at(1)
    I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    T = r.col("T_sample")[o]
    print(f"run {rid}: B {B.min():.3f}-{B.max():.3f}, N={len(B)}, R {R.min():.1f}-{R.max():.1f}, R(B<0.1)={R[B<0.1].mean():.1f}, "
          f"I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA, T {T.min():.3f}-{T.max():.3f}, "
          f"Itg {r.col('k_2400_tg_curr').min()*1e12:.0f}..{r.col('k_2400_tg_curr').max()*1e12:.0f} pA, "
          f"sens {r.meta['instruments'].get('sr1',{}).get('parameters',{}).get('sensitivity',{}).get('value') if isinstance(r.meta.get('instruments'),dict) else '?'}")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid} raw Rxx"); ax[0, j].set_xlabel("B (T)")
    # background-subtracted in 1/B
    m = B > 1.0
    cf = np.polyfit(B[m], np.log10(R[m]), 5); dR = np.log10(R[m]) - np.polyval(cf, B[m])
    ax[1, j].plot(1 / B[m], dR, lw=0.7); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_title("log R − poly5(B)")
    for lo in (1.5, 3.0):
        f, S = sdh_fft(R[:, None], B, b_range=(lo, B.max()), nfft=4096, bg_degree=5)
        S = S[0]; ax[2, j].plot(f, S / S.max(), lw=0.8, label=f"B>{lo}")
        sel = (f > 2) & (f < 80)
        from scipy.signal import find_peaks
        pk, _ = find_peaks(S[sel], prominence=0.08 * S[sel].max())
        print(f"  FFT B>{lo}: peaks (T, rel) " + ", ".join(f"{f[sel][p]:.1f}:{S[sel][p]/S[sel].max():.2f}" for p in pk))
    ax[2, j].set_xlim(0, 80); ax[2, j].legend(); ax[2, j].set_xlabel("F (T)")
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
        print(on.summary())
    except Exception as e:
        print("  sdh_onset:", type(e).__name__, e)
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spots.png", dpi=90)
