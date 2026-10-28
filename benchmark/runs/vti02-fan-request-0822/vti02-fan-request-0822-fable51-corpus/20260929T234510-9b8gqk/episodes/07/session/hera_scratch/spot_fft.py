"""Spot-check read: runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12). Raw R(B), onset, per-window FFT, tone list vs F_L."""
import sys, json, warnings, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError
from hera.analysis import luttinger_frequency
FS = 50e-6 / 10e-9  # 5 kOhm
out = {}
fig, axs = plt.subplots(3, 2, figsize=(14, 11))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}"); print("="*70); print(summarize_run(r)); print("cols:", r.metadata["columns"])
    B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6; V = r.col("sr1_X") / 1.0
    R = V / I; o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    T = r.col("T_sample"); print(f"T_sample {T.min():.3f}-{T.max():.3f} K; I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA")
    # ADC step estimate on sr1_X at low field
    x = np.sort(np.unique(np.round(r.col("sr1_X"), 12))); d = np.diff(x); d = d[d > 0]
    print(f"sr1_X min step {d.min():.3e} V (= {d.min()/10e-9:.3f} Ohm at 10 nA); FS {FS:.0f} Ohm; R range {R.min():.1f}..{R.max():.1f} Ohm (max/FS {R.max()/FS:.3f})")
    FL = luttinger_frequency(abs(n12) * 1e16); print(f"F_L = {FL:.2f} T")
    axs[0, j].plot(B, R, lw=0.7); axs[0, j].set_title(f"run {rid}: n = {n12:+.1f}e12, raw R(B)"); axs[0, j].set_xlabel("B (T)"); axs[0, j].set_ylabel("Rxx (Ohm)")
    try:
        on = sdh_onset(R, B, r_full_scale=FS, b_lo=0.5)
        print(on.summary()); out[rid] = {"onset_b": float(on.onset_b), "clip_high_b": None if on.clip_high_b is None else float(on.clip_high_b),
                                        "tones": [dict(freq=float(t.freq), onset_b=float(t.onset_b), censored=bool(t.censored), marginal=bool(t.marginal),
                                                        harmonic_of=t.harmonic_of, snr_max=float(np.nanmax(t.snr))) for t in on.tones]}
        b_on = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); b_on = 1.5; out[rid] = {"error": str(e)}
    # background-subtracted trace (deg-5 in B) above 1 T for the eye
    m = B >= max(1.0, 0.8*b_on); cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    axs[1, j].plot(1/B[m], dR, lw=0.7); axs[1, j].set_xlabel("1/B (1/T)"); axs[1, j].set_ylabel("dR (Ohm)"); axs[1, j].set_title(f"bg-subtracted (deg 5), B >= {B[m].min():.2f} T; onset_b {b_on:.2f} T")
    # FFTs over several windows (stability sweep)
    Bmax = B.max()
    for (lo, deg, ls) in [(b_on, 5, "-"), (max(b_on, 1.5), 5, "--"), (max(b_on, 2.5), 5, ":"), (b_on, 3, "-.")]:
        if lo >= Bmax - 1: continue
        f, sp = sdh_fft(R[:, None], B, b_range=(lo, Bmax), bg_degree=deg, log=False, nfft=4096)
        sp = sp[0]; sel = (f > 1) & (f < 3 * FL)
        axs[2, j].plot(f[sel], sp[sel] / sp[sel].max(), ls, lw=0.9, label=f"B {lo:.2f}-{Bmax:.1f}, deg {deg}")
        # top peaks
        from scipy.signal import find_peaks
        pk, pr = find_peaks(sp[sel], prominence=0.05 * sp[sel].max())
        top = sorted(zip(pr["prominences"], f[sel][pk]), reverse=True)[:6]
        print(f"  FFT B {lo:.2f}-{Bmax:.1f} deg {deg}: dF = {1/(1/lo-1/Bmax):.2f} T; peaks (T, rel): " + ", ".join(f"{ff:.1f} ({p/sp[sel].max():.2f})" for p, ff in top))
    for k in (0.28, 0.72, 1.0):
        axs[2, j].axvline(k * FL, color="gray", ls=":", lw=0.8)
    axs[2, j].set_xlim(0, 2.2 * FL); axs[2, j].set_xlabel("F (T)"); axs[2, j].set_ylabel("FFT (norm)"); axs[2, j].legend(fontsize=7)
    axs[2, j].set_title(f"FFT in 1/B; lines at 0.28/0.72/1.0 F_L (F_L={FL:.1f} T)")
fig.tight_layout(); fig.savefig("hera_scratch/spot_fft.png", dpi=110)
json.dump(out, open("hera_scratch/spot_fft.json", "w"), indent=1, default=str)
print("saved hera_scratch/spot_fft.png")
