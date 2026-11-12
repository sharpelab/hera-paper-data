"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw, onset, FFT, model overlay."""
import sys, json, warnings
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as M

D = Path("data")
out = {}
fig, axs = plt.subplots(3, 2, figsize=(14, 12))
for col, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    run = open_run(D / str(rid))
    B = run.col("magnet_field"); X = run.col("sr1_X"); I = np.abs(run.col("sr0_X")) / 1e6
    Ib = np.median(I)
    R = X / Ib   # gain 1
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    print(f"\n===== run {rid}: n = {n12:+.2f}e12, {len(B)} pts, B {B.min():.3f}-{B.max():.3f} T, I_bias med {Ib*1e9:.3f} nA, R range {R.min():.1f}..{R.max():.1f} Ohm, R(Bmin) {R[0]:.1f}")
    FL = luttinger_frequency(abs(n12) * 1e16) if 'luttinger_frequency' in dir() else None
    try:
        FL = float(luttinger_frequency(abs(n12) * 1e16))
    except Exception as e:
        FL = 4.1357e-15 * abs(n12) * 1e16 / 4
        print("luttinger_frequency fallback", e)
    print(f"F_L = {FL:.2f} T")
    # model
    try:
        EF, orbs = M.abab_fs(n12); ms = M.abab_mstar(n12)
        print("ABAB orbits F(T),kF:", [(round(f, 2), round(k*1e-9, 3)) for f, k in orbs], " m*:", [(round(f, 2), round(m, 3)) for f, m in ms])
        ac = M.abca_fs(n12); acm = M.abca_mstar(n12)
        print("ABCA:", ac, " m*:", acm)
    except Exception as e:
        print("model err", e)
    axs[0, col].plot(B, R, lw=0.6); axs[0, col].set_title(f"run {rid} raw R_xx (sr1/I), n={n12:+.1f}e12"); axs[0, col].set_xlabel("B (T)"); axs[0, col].set_ylabel("R (Ohm)")
    # onset
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6 / Ib)
        print(on.summary())
        out[rid] = dict(onset_b=float(on.onset_b), clip_high_b=None if on.clip_high_b is None else float(on.clip_high_b),
                        tones=[dict(freq=float(t.freq), onset_b=float(t.onset_b), censored=bool(t.censored), marginal=bool(t.marginal),
                                    harmonic_of=t.harmonic_of if not hasattr(t.harmonic_of, 'tolist') else t.harmonic_of.tolist()) for t in on.tones])
        b_on = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); b_on = None; out[rid] = dict(error=str(e))
    # bg-subtracted trace
    for cutoff, ls in [(max(1.0, b_on or 1.0), "-"), (max(2.0, (b_on or 1.0) * 1.5), "--")]:
        sel = B >= cutoff
        if sel.sum() < 20: continue
        p = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(p, B[sel])
        if ls == "-":
            axs[1, col].plot(1 / B[sel], dR, lw=0.6); axs[1, col].set_xlabel("1/B (1/T)"); axs[1, col].set_ylabel("dR (Ohm)"); axs[1, col].set_title(f"bg-subtracted (deg 5) from {cutoff:.2f} T")
        for deg in (3, 5, 7):
            f, s = sdh_fft(R[:, None], B, b_range=(cutoff, B.max()), bg_degree=deg, log=False, nfft=2048)
            s = s[0]; s = s / s[(f > 2)].max()
            axs[2, col].plot(f, s, ls, lw=0.8, label=f"cut {cutoff:.2f} T deg {deg}")
            pk = [(round(float(f[i]), 2), round(float(s[i]), 2)) for i in np.argsort(s)[::-1] if f[i] > 2][:8]
            print(f"  FFT cut {cutoff:.2f} deg {deg}: top peaks (F, rel) {pk}")
    axs[2, col].axvline(FL, color="k", ls=":", label=f"F_L {FL:.1f}")
    axs[2, col].axvline(0.72 * FL, color="r", ls=":", lw=0.8); axs[2, col].axvline(0.28 * FL, color="r", ls=":", lw=0.8, label="0.72/0.28 F_L")
    axs[2, col].set_xlim(0, 1.6 * FL); axs[2, col].set_xlabel("F (T)"); axs[2, col].legend(fontsize=6)
fig.tight_layout(); fig.savefig("hera_scratch/spot_67.png", dpi=110)
json.dump(out, open("hera_scratch/spot_67_onset.json", "w"), indent=1, default=str)
print("saved")
