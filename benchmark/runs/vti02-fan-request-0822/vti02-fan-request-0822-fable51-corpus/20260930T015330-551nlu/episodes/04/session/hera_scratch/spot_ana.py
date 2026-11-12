"""sdh-spot-check read of runs 6 (electron n=+3.2) and 7 (hole n=-1.2): raw, dR(1/B), onset (b_lo above the coarse segment),
FFT with stability sweep (bg_degree x window), digitization check. Scratch -> promote."""
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, warnings
import scipy.constants as c
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError
warnings.simplefilter("ignore")
FL = lambda n: abs(n)*1e16*c.h/(4*c.e)
out = {}
for rid, n, blo in ((6, 3.2, 1.0), (7, -1.2, 0.3)):
    r = open_run(f"data/{rid}"); B = r.col("magnet_field"); X = r.col("sr1_X"); I0 = r.col("sr0_X")/(-1e6)
    amp = r.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"]; I = amp/1e8
    R = X/I; Rm = X/I0   # nominal-I and measured-I forms
    o = np.argsort(B); B, R, Rm, I0 = B[o], R[o], Rm[o], I0[o]
    d = np.diff(np.unique(np.round(X, 12))); lsb = d[d > 0].min()
    print(f"\n=== run {rid}: n={n:+.2f}e12 F_L={FL(n):.1f} T; I_bias {I*1e9:.1f} nA (measured I {I0.min()*1e9:.2f}-{I0.max()*1e9:.2f} nA); "
          f"X LSB {lsb*1e9:.1f} nV = {lsb/I:.2f} Ohm; R range {R.min():.0f}..{R.max():.0f} Ohm; |R|max/FS = {abs(R).max()/(50e-6/I):.2f}")
    print(f"T_sample {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K; I_tg med {np.median(r.col('k_2400_tg_curr'))*1e12:+.0f} pA, I_bg med {np.median(r.col('k_2400_bg_curr'))*1e12:+.0f} pA")
    m = B >= blo
    for bl in sorted({blo, 1.0, 1.5}):
        try:
            on = sdh_onset(R[B >= bl], B[B >= bl], r_full_scale=50e-6/I)
            print(f"-- onset with b_lo={bl}: onset_b={on.onset_b:.2f} T (tone {on.onset_freq:.1f})")
            for t in on.tones:
                fl = [f for f, v in (("cens", t.censored), ("rev", t.revived), ("marg", t.marginal), ("resid", t.near_residual)) if v]
                print(f"   {t.freq:5.1f} T onset {t.onset_b:.2f} snr {t.snr.max():5.1f} per {t.n_periods:.1f} harm_of {t.harmonic_of} {fl}")
            if bl == blo: out[rid] = on
        except SdhOnsetError as e: print("   SdhOnsetError", str(e)[:200])
    # FFT stability: bg 3/5/7, windows
    fig, ax = plt.subplots(2, 2, figsize=(13, 8))
    ax[0,0].plot(B, R, lw=0.6); ax[0,0].set_xlabel("B (T)"); ax[0,0].set_ylabel("Rxx (Ohm)"); ax[0,0].set_title(f"run {rid} raw Rxx, n={n:+.1f}e12 D=0")
    ax2 = ax[0,0].twinx(); ax2.plot(B, I0*1e9, "r", lw=0.4, alpha=.5); ax2.set_ylabel("I_drain (nA)", color="r")
    # bg-subtracted in B then vs 1/B
    sel = B >= blo; cf = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(cf, B[sel])
    ax[0,1].plot(1/B[sel], dR, lw=0.6); ax[0,1].set_xlabel("1/B (1/T)"); ax[0,1].set_ylabel("dRxx (Ohm), deg-5 bg"); ax[0,1].set_title(f"B >= {blo} T")
    for bg, ls in ((3, ":"), (5, "-"), (7, "--")):
        for (lo, hi), col in (((blo, 10.0), "C0"), ((1.5, 10.0), "C1"), ((max(blo, 2.5), 10.0), "C2"), ((blo, 5.0), "C3"), ((3.0, 10.0), "C4")):
            f, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=bg, log=False, nfft=4096)
            ax[1,0].plot(f, sp[0]/sp[0][(f > 2)].max(), ls, color=col, lw=0.8, label=f"bg{bg} [{lo},{hi}]" if bg == 5 or (lo, hi) == (blo, 10.0) else None)
    ax[1,0].set_xlim(0, 60); ax[1,0].axvline(FL(n), color="k", ls="--", lw=1); ax[1,0].text(FL(n), 1.0, " F_L", va="top")
    ax[1,0].set_xlabel("F (T)"); ax[1,0].set_ylabel("|FFT| (norm)"); ax[1,0].legend(fontsize=6, ncol=2); ax[1,0].set_title("FFT stability: bg degree x window")
    # peak table for the reference choice
    f, sp = sdh_fft(R[:, None], B, b_range=(max(blo, 1.5), 10.0), bg_degree=5, log=False, nfft=4096); s = sp[0]
    from scipy.signal import find_peaks
    pk, pr = find_peaks(s, prominence=0.03*s[f > 2].max()); pk = [p for p in pk if f[p] > 1.5]
    pk = sorted(pk, key=lambda p: -s[p])[:10]
    print(f"-- FFT peaks [1.5,10] bg5 (F, rel amp, F/F_L): " + ", ".join(f"{f[p]:.1f}({s[p]/s[pk[0]]:.2f},{f[p]/FL(n):.2f})" for p in sorted(pk, key=lambda p: f[p])))
    for (lo, hi) in ((1.5, 4.0), (4.0, 10.0), (2.0, 5.0), (5.0, 10.0)):
        if lo < blo: continue
        f2, sp2 = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=4, log=False, nfft=4096); s2 = sp2[0]
        pk2, _ = find_peaks(s2, prominence=0.05*s2[f2 > 2].max()); pk2 = sorted([p for p in pk2 if f2[p] > 1.5], key=lambda p: -s2[p])[:6]
        print(f"   window [{lo},{hi}] dF={1/(1/lo-1/hi):.1f}: " + ", ".join(f"{f2[p]:.1f}({s2[p]/s2[pk2[0]]:.2f})" for p in sorted(pk2, key=lambda p: f2[p])))
    ax[1,1].plot(f, s, lw=0.8); ax[1,1].set_xlim(0, 60); ax[1,1].axvline(FL(n), color="k", ls="--")
    for p in pk: ax[1,1].annotate(f"{f[p]:.1f}", (f[p], s[p]), fontsize=7)
    ax[1,1].set_xlabel("F (T)"); ax[1,1].set_title(f"FFT [{max(blo,1.5)},10] T, bg5 — peaks vs F_L={FL(n):.1f} T")
    fig.tight_layout(); fig.savefig(f"hera_scratch/spot_run{rid}.png", dpi=110)
