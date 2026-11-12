import numpy as np, json, warnings
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, summarize_run
out = {}
fig, axs = plt.subplots(2, 3, figsize=(16, 8))
for k, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}")
    print(summarize_run(r))
    B = r.col("magnet_field"); X1 = r.col("sr1_X"); I = r.col("sr0_X") / -1e6
    R = X1 / I
    o = np.argsort(B); B, R = B[o], R[o]
    md = r.meta
    sens = 50e-6; Ib = np.nanmedian(np.abs(I))
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"run {rid}: n={n12:+}e12  F_L={FL:.2f} T  R range {R.min():.1f}..{R.max():.1f} Ohm, I {Ib*1e9:.2f} nA, FS {sens/Ib:.0f} Ohm")
    try:
        on = sdh_onset(R, B, r_full_scale=sens / Ib)
        print(on.summary())
        out[rid] = dict(onset=float(on.onset_b), tones=[dict(f=float(t.freq), onset=float(t.onset_b), censored=bool(t.censored),
                        harmonic_of=(None if t.harmonic_of is None else float(t.harmonic_of))) for t in on.tones])
    except Exception as e:
        print("ONSET ERR", type(e).__name__, e); on = None; out[rid] = dict(err=str(e))
    axs[k, 0].plot(B, R, lw=.7); axs[k, 0].set_title(f"run {rid} raw Rxx, n={n12:+}e12, D=0"); axs[k, 0].set_xlabel("B (T)"); axs[k, 0].set_ylabel("R (Ohm)")
    for j, (lo, hi) in enumerate([(2.0, 10.0), (3.0, 10.0), (4.0, 10.0)] if rid == 6 else [(1.5, 10.0), (2.5, 10.0), (4.0, 10.0)]):
        for deg in (3, 5, 7):
            f, s = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=deg, log=False, nfft=4096)
            sp = s[0]; m = f > 2
            pk = [f[i] for i in range(1, len(f) - 1) if m[i] and sp[i] > sp[i-1] and sp[i] > sp[i+1] and sp[i] > 0.15 * sp[m].max()]
            print(f"  run {rid} FFT b[{lo},{hi}] deg{deg}: peaks {np.round(pk, 2)} ; F/F_L {np.round(np.array(pk)/FL, 3)}")
            if deg == 5:
                axs[k, 1].plot(f, sp / sp[m].max(), label=f"[{lo},{hi}]")
    axs[k, 1].axvline(FL, color="k", ls="--", label="F_L"); axs[k, 1].set_xlim(0, 2.2 * FL); axs[k, 1].legend(fontsize=7); axs[k, 1].set_xlabel("F (T)")
    # bg-subtracted vs 1/B
    sel = B > 1.5
    c = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(c, B[sel])
    axs[k, 2].plot(1 / B[sel], dR, lw=.7); axs[k, 2].set_xlabel("1/B (1/T)"); axs[k, 2].set_title("dR (deg-5 bg in B)")
fig.tight_layout(); fig.savefig("hera_scratch/spot_6_7.png", dpi=90)
json.dump(out, open("hera_scratch/spot_6_7.json", "w"), indent=1)
