"""sdh-spot-check read of runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw R(B), sdh_onset, sdh_fft vs F_L
and the model's ABAB/ABCA tones. Saves hera_scratch/spot_read.png and prints the numbers the fan design inherits."""
import sys, json, warnings, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError
from fs_count_b0 import abab_fs, abca_fs, abab_mstar, abca_mstar

I_BIAS = 1.0 / 100e6          # 1 V drive / 100 MOhm
R_FS = 50e-6 / I_BIAS         # sr1 50 uV -> 5 kOhm full scale
runs = {6: ("electron", +3.2e16), 7: ("hole", -1.2e16)}   # n in m^-2
fig, ax = plt.subplots(3, 2, figsize=(14, 12))
out = {}
for j, (rid, (side, n_si)) in enumerate(runs.items()):
    r = open_run(f"data/{rid}")
    print(f"\n===== run {rid} ({side}) =====\n{summarize_run(r)}")
    B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6; V = r.col("sr1_X") / 1.0
    R = V / I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    T = r.col("T_sample")
    print(f"B {B.min():.3f}-{B.max():.3f} T, {len(B)} pts; R {R.min():.1f}..{R.max():.1f} Ohm (fs {R.max()/R_FS:.2f}); I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; T {T.min():.3f}-{T.max():.3f} K")
    FL = float(luttinger_frequency(n_si))
    n12 = n_si * 1e-16
    ef, orb = abab_fs(n12); abab_t = [f for f, k in orb]
    ef2, topo, ncomp, nfreq, Ftot = abca_fs(n12)
    print(f"F_L = {FL:.2f} T; model ABAB tones {np.round(abab_t,2)} (sum {np.sum(abab_t):.2f}); ABCA {Ftot:.2f} T ({topo}, {ncomp} comp)")
    print(f"   masses ABAB {[(round(f,1), round(m,3)) for f,m in abab_mstar(n12)]}; ABCA m* {abca_mstar(n12)[1]:.3f}")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid} {side} n={n12:+.2f}e12 raw R(B)"); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx (Ohm)")
    # onset
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, r_full_scale=R_FS)
            for ww in w: print("  warn:", ww.message)
        print(on.summary())
        out[rid] = dict(onset_b=float(on.onset_b), clip_high_b=(None if on.clip_high_b is None else float(on.clip_high_b)),
                        tones=[dict(freq=float(t.freq), onset_b=float(t.onset_b), censored=bool(t.censored), marginal=bool(t.marginal),
                                    harmonic_of=(None if t.harmonic_of is None else float(t.harmonic_of)) if not isinstance(t.harmonic_of, (list, tuple)) else [float(x) for x in t.harmonic_of]) for t in on.tones])
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); onset = None; out[rid] = dict(onset_b=None, error=str(e))
    # background-subtracted trace + FFT for a few windows
    lo0 = max(onset or 1.0, 1.0)
    Bmax = B.max()
    for k, lo in enumerate([lo0, lo0 * 1.3, max(lo0, 0.5 * Bmax)]):
        m = (B >= lo)
        if m.sum() < 30: continue
        cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
        if k == 0:
            ax[1, j].plot(1 / B[m], dR, lw=0.6); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("dR (Ohm), deg-5 bg removed"); ax[1, j].set_title(f"bg-subtracted, B >= {lo:.2f} T")
        f, spec = sdh_fft(R[:, None], B, b_range=(lo, Bmax), bg_degree=5, log=False, nfft=4096)
        sp = spec[0]; sel = (f > 2) & (f < 3 * FL)
        pk = f[sel][np.argsort(sp[sel])[::-1][:6]]
        dF = 1 / (1 / lo - 1 / Bmax)
        print(f"  FFT window [{lo:.2f},{Bmax:.1f}] T (dF {dF:.2f} T): top peaks {np.round(np.sort(pk),2)} T  [F_L {FL:.1f}]")
        ax[2, j].plot(f[sel], sp[sel] / sp[sel].max(), lw=0.8, label=f"B>={lo:.2f} T, dF {dF:.1f}")
    ax[2, j].axvline(FL, color="k", ls="--", lw=1, label=f"F_L {FL:.1f} T")
    for t in abab_t: ax[2, j].axvline(t, color="r", ls=":", lw=1)
    ax[2, j].set_xlabel("F (T)"); ax[2, j].set_ylabel("norm. FFT amp"); ax[2, j].legend(fontsize=7); ax[2, j].set_xlim(0, 2 * FL)
fig.tight_layout(); fig.savefig("hera_scratch/spot_read.png", dpi=110); print("\nsaved hera_scratch/spot_read.png")
json.dump(out, open("hera_scratch/spot_read.json", "w"), indent=1, default=str)
