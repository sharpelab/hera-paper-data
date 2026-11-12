"""SdH spot checks runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw R(B), onset, FFT vs model."""
import sys, json, warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from hera.analysis import open_run, resolve_channels, current_channel, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

OUT = "hera_scratch"
SPOTS = {6: 3.2, 7: -1.2}
res = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for col, (rid, n12) in enumerate(SPOTS.items()):
    r = open_run(f"data/{rid}")
    chans = resolve_channels(r.meta)
    ic = current_channel(chans)
    B = r.col("magnet_field")
    I = r.col("sr0_X") / r.meta["measurement_config"]["sr0_gain"]
    V = r.col("sr1_X") / 1.0
    R = V / I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    T = r.col("T_sample")
    ins = r.meta["instruments"]
    sens = 50e-6
    Ib = np.median(np.abs(I))
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"=== run {rid}: n = {n12:+.2f}e12, F_L = {FL:.2f} T; |I| median {Ib*1e9:.2f} nA (min {np.abs(I).min()*1e9:.2f});"
          f" R(0) = {R[0]:.1f}, R range {R.min():.1f}..{R.max():.1f} Ohm; FS = {sens/Ib:.0f} Ohm -> max fs {np.abs(V).max()/sens:.2f};"
          f" T {T.min():.3f}-{T.max():.3f} K; |I_tg|max {np.abs(r.col('k_2400_tg_curr')).max()*1e12:.0f} pA")
    ax[0, col].plot(B, R, lw=0.7); ax[0, col].set_title(f"run {rid} raw Rxx (n={n12:+.1f}e12, D=0)"); ax[0, col].set_xlabel("B (T)"); ax[0, col].set_ylabel("R (Ohm)")
    try:
        on = sdh_onset(np.abs(R), B, r_full_scale=sens / Ib, b_lo=0.3)
        print(on.summary())
        onb = on.onset_b
        tones = [(t.freq, t.onset_b, t.censored, t.marginal, t.harmonic_of) for t in on.tones]
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); onb = None; tones = []
    # background-subtracted residual
    sel = B > max(0.5, (onb or 1.0) * 0.8)
    p = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(p, B[sel])
    ax[1, col].plot(1 / B[sel], dR, lw=0.7); ax[1, col].set_xlabel("1/B (1/T)"); ax[1, col].set_ylabel("dR (Ohm), deg-5 bg in B")
    if onb: ax[1, col].axvline(1 / onb, color="r", ls="--", label=f"onset {onb:.2f} T"); ax[1, col].legend()
    # FFT stability over windows / bg degree
    for blo in sorted({round(onb or 1.0, 2), 2.0, 3.0, 4.0}):
        for deg in (3, 5, 7):
            f, S = sdh_fft(np.abs(R)[:, None], B, b_range=(blo, B.max()), bg_degree=deg, nfft=4096)
            s = S[0]; m = f > 1.5
            pk = [i for i in range(1, len(s) - 1) if m[i] and s[i] > s[i - 1] and s[i] > s[i + 1] and s[i] > 0.15 * s[m].max()]
            pk = sorted(pk, key=lambda i: -s[i])[:5]
            print(f"   FFT b>[{blo:.2f}] deg {deg}: peaks " + ", ".join(f"{f[i]:.1f}T({s[i]/s[m].max():.2f})" for i in sorted(pk)))
            if deg == 5:
                ax[2, col].plot(f, s / s[m].max(), lw=0.8, label=f"B>{blo:.1f}")
    ax[2, col].axvline(FL, color="k", ls="--", lw=1, label="F_L")
    try:
        from fs_count_b0 import abab_fs, abab_mstar, abca_mstar
        EF, orb = abab_fs(n12)
        ab = [F for F, k in orb]
        print(f"   model ABAB orbits: {[round(x,2) for x in ab]}; m* {[ (round(F,1), round(m,3)) for F, m in abab_mstar(n12)]}; ABCA m* {abca_mstar(n12)}")
        for F in ab: ax[2, col].axvline(F, color="C3", ls=":", lw=1)
    except Exception as e:
        print("model err", e); ab = []
    ax[2, col].set_xlim(0, 2 * FL); ax[2, col].set_xlabel("F (T)"); ax[2, col].legend(fontsize=7); ax[2, col].set_title("FFT (deg-5 bg), F_L dashed, ABAB model dotted")
    res[rid] = dict(n=n12, FL=FL, onset=onb, tones=tones, abab=ab, R0=float(R[0]), Rmax=float(R.max()), Ib=float(Ib))
fig.tight_layout(); fig.savefig(f"{OUT}/spot_runs67.png", dpi=110)
json.dump(res, open(f"{OUT}/spot_runs67.json", "w"), indent=1, default=str)
