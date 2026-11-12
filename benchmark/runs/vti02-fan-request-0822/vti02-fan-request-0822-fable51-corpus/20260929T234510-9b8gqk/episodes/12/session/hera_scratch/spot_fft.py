"""SdH spot-check read for runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12):
raw R(B), sdh_onset (per-tone onsets), sdh_fft over the usable record, tones vs F_L."""
import sys, warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency, resolve_channels

base = Path(__file__).resolve().parents[1]
I_BIAS_NOM = 1.0 / 100e6  # 1 V / 100 MOhm

def load(rid):
    r = open_run(base / "data" / str(rid))
    print(summarize_run(r))
    ch = resolve_channels(r.metadata)
    print("channels:", ch)
    B = r.col("magnet_field")
    I = r.col("sr0_X") / -1e6
    R = r.col("sr1_X") / 1.0 / I
    return r, B, I, R

for rid, n12 in [(6, 3.2), (7, -1.2)]:
    print("=" * 30, "run", rid, "n =", n12, "e12")
    r, B, I, R = load(rid)
    o = np.argsort(B); B, I, R = B[o], I[o], R[o]
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"F_L = {FL:.2f} T; I_bias median {np.median(I)*1e9:.3f} nA; R range {R.min():.1f}..{R.max():.1f} Ohm; "
          f"R(B<0.1) = {np.median(R[B < 0.15]):.1f}; T_sample {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K")
    # onset
    fs = 50e-6 / np.median(I)
    on = None
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, r_full_scale=fs, b_lo=0.3)
            for ww in w: print("  warn:", ww.message)
        print(on.summary())
        print("onset_b", on.onset_b, "clip_high_b", on.clip_high_b)
        for t in on.tones:
            print("  tone", vars(t) if hasattr(t, '__dict__') else t)
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
    # FFT over windows
    fig, ax = plt.subplots(1, 3, figsize=(17, 4.5))
    ax[0].plot(B, R, lw=0.7); ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("Rxx sr1 (Ohm)"); ax[0].set_title(f"run {rid}: n={n12:+.2f}e12 raw")
    blo = on.onset_b if on is not None else 1.5
    for cut, col in [(max(blo, 1.0), "C0"), (2.0, "C1"), (3.0, "C2"), (4.0, "C3")]:
        if cut >= B.max() - 1: continue
        f, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5, log=False, nfft=4096)
        sp = spec[0]
        ax[2].plot(f, sp / sp[f > 3].max(), col, lw=0.8, label=f"B>{cut:.1f} T")
        m = (f > 2) & (f < 3 * FL)
        from scipy.signal import find_peaks
        pk, pr = find_peaks(sp[m], prominence=0.05 * sp[m].max())
        top = sorted(zip(pr["prominences"], f[m][pk]), reverse=True)[:8]
        print(f"  FFT B>{cut:.1f}: dF_res={1/(1/cut-1/B.max()):.2f} T; peaks(T, rel-prom): " + ", ".join(f"{ff:.1f}({p/sp[m].max():.2f})" for p, ff in top))
    # detrended in 1/B for the eye
    m = B > max(blo, 1.0)
    cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax[1].plot(1 / B[m], dR, lw=0.7); ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("dRxx (Ohm)"); ax[1].set_title("bg-subtracted (deg 5 in B)")
    for k, frac in [("F_L", 1.0), ("0.72FL", 0.72), ("0.28FL", 0.28)]:
        ax[2].axvline(FL * frac, color="k", ls=":", lw=0.8); ax[2].text(FL * frac, 1.02, k, fontsize=7, rotation=90)
    ax[2].set_xlim(0, 2.2 * FL); ax[2].set_xlabel("F (T)"); ax[2].set_ylabel("FFT (norm)"); ax[2].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(base / "hera_scratch" / f"spot_run{rid}.png", dpi=110)
    print("saved", f"spot_run{rid}.png")
