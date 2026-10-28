"""Spot-check read for runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw R(B), onset, FFT tones vs F_L."""
import sys, warnings, json
import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency
warnings.simplefilter("always")
H_OVER_4E = 4.135667e-15/4
out = {}
fig, axes = plt.subplots(2, 3, figsize=(17, 8))
for row, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field"); I = r.col("sr0_X")/(-1e6); V = r.col("sr1_X")/1.0
    R = V/I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    F_L = H_OVER_4E*abs(n12)*1e16
    print(f"\n===== run {rid}: n = {n12:+.2f}e12, F_L = {F_L:.2f} T; R range {R.min():.1f}..{R.max():.1f} Ohm; I {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA =====")
    ax = axes[row,0]; ax.plot(B, R, lw=0.7); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)"); ax.set_title(f"run {rid} raw R(B), n={n12:+.1f}e12")
    # onset
    try:
        on = sdh_onset(R, B, b_lo=0.3, r_full_scale=50e-6/10e-9)
        print(on.summary())
        out[rid] = dict(onset_b=float(on.onset_b), clip_high_b=(None if on.clip_high_b is None else float(on.clip_high_b)),
                        tones=[dict(freq=float(t.freq), onset_b=float(t.onset_b), censored=bool(t.censored), marginal=bool(t.marginal),
                                    harmonic_of=(None if t.harmonic_of is None else float(t.harmonic_of))) for t in on.tones])
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); out[rid] = dict(error=str(e)); onset = 1.5
    # FFT on a few windows: full above onset, low half, high half (1/B halves)
    Bmax = B.max()
    inv_lo, inv_hi = 1/Bmax, 1/max(onset, 0.35)
    inv_mid = 0.5*(inv_lo+inv_hi)
    wins = {"full": (max(onset,0.35), Bmax), "lowB": (max(onset,0.35), 1/inv_mid), "highB": (1/inv_mid, Bmax)}
    ax2 = axes[row,1]; ax3 = axes[row,2]
    for k,(lo,hi) in wins.items():
        m = (B>=lo)&(B<=hi)
        for deg in (3,5,7):
            f, s = sdh_fft(R[:,None], B, b_range=(lo,hi), bg_degree=deg, log=False, nfft=4096)
            s = s[0]/s[0][f>2].max()
            if deg==5:
                ax2.plot(f, s + {"full":0,"lowB":1.1,"highB":2.2}[k], lw=0.8, label=f"{k} [{lo:.2f},{hi:.1f}] T")
            # peaks
            from scipy.signal import find_peaks
            pk,_ = find_peaks(s, height=0.08, distance=5)
            pk = pk[f[pk]>1.5]
            print(f"  win {k:5s} [{lo:.2f},{hi:.2f}] T deg{deg}: dF={1/(1/lo-1/hi):.2f} T peaks(T,rel): " + ", ".join(f"{f[p]:.1f}({s[p]:.2f})" for p in pk[:10]))
    ax2.axvline(F_L, color="k", ls="--", lw=1, label=f"F_L={F_L:.1f} T"); ax2.axvline(0.72*F_L, color="r", ls=":", lw=1); ax2.axvline(0.28*F_L, color="r", ls=":", lw=1, label="0.72/0.28 F_L")
    ax2.set_xlim(0, 1.6*F_L); ax2.set_xlabel("F (T)"); ax2.set_title("FFT in 1/B (deg-5 bg), windows offset"); ax2.legend(fontsize=7)
    # background-subtracted dR vs 1/B
    m = B>=max(onset,0.35)
    cf = np.polyfit(B[m], R[m], 5); dR = R[m]-np.polyval(cf, B[m])
    ax3.plot(1/B[m], dR, lw=0.7); ax3.set_xlabel("1/B (1/T)"); ax3.set_ylabel("dRxx (Ohm)"); ax3.set_title(f"bg-subtracted, B>{max(onset,0.35):.2f} T")
    # filling factor markers: nu = n h/(eB)
    for nu in range(4, 80, 4):
        Bnu = abs(n12)*1e16*4.135667e-15/nu
        if B.min() < Bnu < B.max(): ax.axvline(Bnu, color="gray", lw=0.4, alpha=0.5)
fig.tight_layout(); fig.savefig("hera_scratch/spot_read.png", dpi=110)
json.dump(out, open("hera_scratch/spot_read.json","w"), indent=1)
print(json.dumps(out, indent=1))
