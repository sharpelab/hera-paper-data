"""Runs 6 (e-side n=+3.2e12) and 7 (h-side n=-1.2e12): raw R(B), 1/B FFT, per-tone onsets.
Grounds the landau-fan design (B_lo, B_hi, tone structure vs F_L)."""
import numpy as np, json, warnings
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency

CAL = json.load(open("hera_scratch/cal_run5.json"))
out = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    T = r.col("T_sample")
    o = np.argsort(B); B, R, I, T = B[o], R[o], I[o], T[o]
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"\n=== run {rid}: n = {n12:+.2f}e12, F_L(full, 4-fold) = {FL:.2f} T; T {T.min():.3f}-{T.max():.3f} K; "
          f"I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; R {R.min():.1f}..{R.max():.1f} Ohm, R(B~0) = {R[B<0.1].mean():.1f}")
    # signed R minima (near-zero / negative -> QH-like minima)
    ax[0, j].plot(B, R, lw=0.8); ax[0, j].set_title(f"run {rid}: n = {n12:+.2f}e12, D = 0 — raw Rxx(B)"); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx (Ohm)")
    ax[0, j].axhline(0, color="k", lw=0.5)
    # FFT windows
    for lo, hi, col in [(1.5, 10.0, "C0"), (3.0, 10.0, "C1"), (1.5, 5.0, "C2")]:
        m = (B >= lo) & (B <= hi)
        f, sp = sdh_fft(R[m][:, None], B[m], nfft=2048, bg_degree=5, log=False)
        sp = sp[0]
        sel = (f > 1) & (f < 150)
        ax[1, j].plot(f[sel], sp[sel] / sp[sel].max(), color=col, lw=0.9, label=f"B {lo}-{hi} T")
        pk = f[sel][np.argsort(sp[sel])[::-1][:6]]
        print(f"  FFT window {lo}-{hi} T top freqs: {np.round(np.sort(pk),1)} T")
    for k in (1, 2, 4):
        ax[1, j].axvline(FL / k, color="gray", ls=":", lw=0.8)
    ax[1, j].set_xlim(0, 80); ax[1, j].set_xlabel("F (T)"); ax[1, j].set_ylabel("|FFT| (norm)"); ax[1, j].legend(fontsize=7)
    ax[1, j].set_title(f"1/B FFT (dotted: F_L, F_L/2, F_L/4 = {FL:.1f}/{FL/2:.1f}/{FL/4:.1f} T)")
    # onset
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            on = sdh_onset(R, B, b_lo=0.3, r_full_scale=50e-6 / 10e-9)
        print(on.summary())
        out[rid] = dict(onset_b=float(on.onset_b), tones=[(float(t.freq), float(t.contrast), float(t.onset_b), t.harmonic_of) for t in on.tones])
    except SdhOnsetError as e:
        print("  sdh_onset failed:", e)
    # 1/B view w/ background removed
    m = B >= 1.0
    cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax[2, j].plot(1 / B[m], dR, lw=0.7); ax[2, j].set_xlabel("1/B (1/T)"); ax[2, j].set_ylabel("dRxx (Ohm), poly5 removed"); ax[2, j].set_title("oscillatory part vs 1/B (B >= 1 T)")
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spot_runs6_7.png", dpi=110)
json.dump(out, open("hera_scratch/sdh_spot_onsets.json", "w"), indent=1, default=str)
print("saved hera_scratch/sdh_spot_runs6_7.png")
