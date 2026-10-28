"""SdH spot checks runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): raw R(B), background-subtracted, FFT, onset."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, luttinger_frequency

cal = json.load(open("hera_scratch/cal_run5.json"))
out = {}
fig, ax = plt.subplots(3, 2, figsize=(12, 11))
for j, (rid, n12) in enumerate(((6, 3.2), (7, -1.2))):
    r = open_run(f"data/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    I = r.col("sr0_X") / ch["sr0"].gain
    V = r.col("sr1_X") / ch["sr1"].gain
    R = np.abs(V / I)
    o = np.argsort(B); B, R, I, V = B[o], R[o], I[o], V[o]
    T = r.col("T_sample")[o]
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    dt = np.diff(r.col("time"))
    print(f"run {rid}: n={n12:+.1f}e12  B {B.min():.3f}..{B.max():.3f}  R {R.min():.0f}..{R.max():.0f} Ohm  "
          f"R(B<0.1)={np.median(R[B<0.1]):.0f}  R(10T)={np.median(R[B>9.9]):.0f}  I {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA  "
          f"max|V| {np.abs(V).max()*1e6:.1f} uV (sens 50 uV)  T {T.min():.3f}..{T.max():.3f}  "
          f"I_tg {itg.min()*1e12:+.0f}..{itg.max()*1e12:+.0f} pA I_bg {ibg.min()*1e12:+.0f}..{ibg.max()*1e12:+.0f} pA  "
          f"dt median {np.median(dt):.2f}s")
    FL = float(luttinger_frequency(np.array([abs(n12) * 1e16]))[0])
    print(f"   F_L (full density, 4-fold) = {FL:.2f} T")
    a = ax[0, j]; a.plot(B, R, lw=0.8); a.set_xlabel("B (T)"); a.set_ylabel("|Rxx| (Ohm)"); a.set_title(f"run {rid} raw, n={n12:+.1f}e12, D=0")
    # onset + tones
    try:
        so = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
        print(so.summary())
        out[rid] = dict(onset=so.onset_b, tones=[(t.freq, t.contrast, t.onset_b, t.marginal, t.harmonic_of) for t in so.tones])
    except Exception as e:
        print("   sdh_onset:", repr(e))
    for k, (blo, bhi) in enumerate(((2.0, 10.0), (4.0, 10.0))):
        f, sp = sdh_fft(R[:, None], B, b_range=(blo, bhi), nfft=4096, bg_degree=5)
        sp = sp[0]
        m = f < 3 * FL + 20
        ax[1, j].plot(f[m], sp[m] / sp[m][f[m] > 1].max(), label=f"B {blo}-{bhi} T")
        pk = np.argsort(sp * (f > 1.5))[::-1]
        # simple peak list
        from scipy.signal import find_peaks
        pp, _ = find_peaks(sp * (f > 1.5), prominence=0.05 * sp[f > 1.5].max())
        pp = pp[np.argsort(sp[pp])[::-1]][:8]
        print(f"   FFT {blo}-{bhi} T peaks (F T, rel amp): " + ", ".join(f"{f[p]:.1f}:{sp[p]/sp[pp[0]]:.2f}" for p in pp))
    for x in (FL, FL / 2, FL / 4):
        ax[1, j].axvline(x, color="k", ls=":", lw=0.7)
    ax[1, j].set_xlabel("F (T)"); ax[1, j].set_title(f"FFT (log R, poly5 bg); dotted: F_L, F_L/2, F_L/4 (F_L={FL:.1f})"); ax[1, j].legend()
    # background-subtracted vs 1/B
    sel = B > 1.5
    x = B[sel]; y = np.log10(R[sel]); bg = np.polyval(np.polyfit(x, y, 5), x)
    ax[2, j].plot(1 / x, y - bg, lw=0.7); ax[2, j].set_xlabel("1/B (1/T)"); ax[2, j].set_ylabel("dlog10 R")
    ax[2, j].set_title("B > 1.5 T, poly5 background removed")
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=90)
json.dump(out, open("hera_scratch/spot_runs67.json", "w"), indent=1, default=float)
