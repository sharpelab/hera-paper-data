"""sdh-spot-check read of runs 6 (electron +3.2e12) and 7 (hole -1.2e12): raw R(B), sdh_onset, sdh_fft, B-window split."""
import sys, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency
h=6.62607015e-34; e=1.602176634e-19
runs = {6: +3.2e12, 7: -1.2e12}
fig, axs = plt.subplots(3, 2, figsize=(14, 12))
out = {}
for j, (rid, n) in enumerate(runs.items()):
    r = open_run(f"data/{rid}"); print(f"\n===== run {rid} =====\n{summarize_run(r)}")
    B = r.col("magnet_field"); I = r.col("sr0_X")/(-1e6); V = r.col("sr1_X")/1.0
    R = np.abs(V/I); T = r.col("T_sample")
    o = np.argsort(B); B, R, I, T = B[o], R[o], I[o], T[o]
    FL = luttinger_frequency(abs(n)*1e4)  # n in m^-2
    print(f"n={n:+.2e} cm^-2  F_L={float(FL):.2f} T; I_bias {np.median(I)*1e9:.2f} nA; T {T.min():.3f}-{T.max():.3f} K; R {R.min():.1f}-{R.max():.1f} Ohm; R(B<0.3)={np.median(R[B<0.35]):.1f}")
    ax = axs[0, j]; ax.plot(B, R, lw=0.7); ax.set_title(f"run {rid}: n={n/1e12:+.2f}e12, raw |Rxx| (sr1)"); ax.set_xlabel("B (T)"); ax.set_ylabel("R (Ohm)")
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6/10e-9)
        print(on.summary())
        bl = on.onset_b
    except SdhOnsetError as ex:
        print("SdhOnsetError:", ex); bl = 1.0; on=None
    out[rid] = dict(onset=bl, on=on, FL=float(FL))
    # background-subtracted trace in 1/B
    m = B >= max(bl, 0.3)
    cf = np.polyfit(B[m], R[m], 5); dR = R[m]-np.polyval(cf, B[m])
    ax = axs[1, j]; ax.plot(1/B[m], dR, lw=0.7); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dR (Ohm)"); ax.set_title(f"bg-subtracted, B>={max(bl,0.3):.2f} T (onset {bl:.2f})")
    # FFT full window + halves
    ax = axs[2, j]
    bmax = B.max()
    for lab, rng in (("full", (max(bl,0.3), bmax)), ("low half", (max(bl,0.3), (max(bl,0.3)+bmax)/2)), ("high half", ((max(bl,0.3)+bmax)/2, bmax))):
        try:
            f, sp = sdh_fft(R[:, None], B, b_range=rng, bg_degree=5, log=False)
            sp = sp[0]/sp[0][f>2].max()
            ax.plot(f, sp, lw=0.8, label=f"{lab} {rng[0]:.2f}-{rng[1]:.2f} T")
            pk = f[(f>2)&(sp>0.15)]
            from scipy.signal import find_peaks
            ip,_ = find_peaks(sp, height=0.1, prominence=0.05); ip = ip[f[ip]>2]
            print(f"  FFT {lab} {rng}: peaks at " + ", ".join(f"{f[i]:.1f}T({sp[i]:.2f})" for i in ip[:10]))
        except Exception as ex: print("fft fail", lab, ex)
    ax.axvline(FL, color='k', ls='--', label=f"F_L={float(FL):.1f} T"); ax.axvline(FL/2, color='gray', ls=':', label="F_L/2")
    ax.set_xlim(0, 1.3*float(FL)); ax.set_xlabel("F (T)"); ax.legend(fontsize=7); ax.set_title("1/B FFT (norm.)")
plt.tight_layout(); plt.savefig("hera_scratch/spot_read.png", dpi=110); print("saved hera_scratch/spot_read.png")
