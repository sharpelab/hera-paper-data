"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D = 0.
Raw R(B) -> sdh_onset (per-tone onsets) -> sdh_fft vs F_L + model tones -> B-window split.
Also prints the FS-count model F(n) table over the candidate fan density window."""
import sys, json, warnings, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError
import fs_count_b0 as m

CAL = json.load(open("hera_scratch/cal_run5.json"))
SENS = 50e-6
runs = {6: +3.2, 7: -1.2}
out = {}
fig, axs = plt.subplots(3, 2, figsize=(14, 12))
for j, (rid, n12) in enumerate(runs.items()):
    r = open_run(f"data/{rid}")
    print("=" * 80); print(summarize_run(r)); print(r.cols)
    B = r.col("magnet_field"); X1 = r.col("sr1_X"); X0 = r.col("sr0_X")
    I = X0 / (-1e6)                      # measured drain current (A), gain -1e6
    R = np.abs(X1 / 1.0 / I)             # sr1 gain 1
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    Ib = np.median(np.abs(I))
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"run {rid}: n = {n12:+.2f}e12, I_bias med {Ib*1e9:.2f} nA, R range {R.min():.1f}-{R.max():.1f} Ohm, "
          f"max fs {R.max()*Ib/SENS:.2f}; F_L = {FL:.2f} T")
    # model tones
    try:
        ef, orbs = m.abab_fs(n12 * 1e12 * 1e4 if False else n12)   # try 1e12 cm^-2 units first
    except Exception as e:
        print("abab_fs unit probe:", e); orbs = []
    axs[0, j].plot(B, R, lw=0.7); axs[0, j].set_title(f"run {rid}: n={n12:+.1f}e12 D=0 raw |Rxx| (fs max {R.max()*Ib/SENS:.2f})")
    axs[0, j].set_xlabel("B (T)"); axs[0, j].set_ylabel("Rxx (Ohm)")
    # onset
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, r_full_scale=SENS / Ib)
            for ww in w: print("  warn:", ww.message)
        print(on.summary())
        onset = on.onset_b
        out[rid] = dict(onset_b=on.onset_b, clip_high_b=on.clip_high_b,
                        tones=[dict(f=t.freq, onset=t.onset_b, censored=t.censored, marginal=t.marginal,
                                    harmonic_of=t.harmonic_of, n_per=t.n_periods) for t in on.tones])
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); onset = 1.5; out[rid] = dict(error=str(e))
    # background-subtracted trace vs 1/B above onset
    sel = B >= max(onset, 0.3)
    cf = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(cf, B[sel])
    axs[1, j].plot(1 / B[sel], dR, lw=0.7); axs[1, j].set_xlabel("1/B (1/T)"); axs[1, j].set_ylabel("dRxx (Ohm)")
    axs[1, j].set_title(f"bg-subtracted (deg 5) above onset {onset:.2f} T")
    # FFT: full window + low/high halves in 1/B
    Bmax = B.max()
    for lab, (blo, bhi), c in [("full", (onset, Bmax), "k"),
                               ("low-B half", (onset, 2 / (1 / onset + 1 / Bmax)), "tab:blue"),
                               ("high-B half", (2 / (1 / onset + 1 / Bmax), Bmax), "tab:red")]:
        try:
            f, sp = sdh_fft(R[:, None], B, b_range=(blo, bhi), bg_degree=5, log=False, nfft=2048)
            sp = sp[0] / sp[0].max()
            axs[2, j].plot(f, sp, c, lw=1, label=f"{lab} [{blo:.2f},{bhi:.2f}] T")
            pk = f[(f > 2) & (f < 3 * FL)][np.argsort(sp[(f > 2) & (f < 3 * FL)])[::-1][:6]]
            print(f"  FFT {lab:12s} top freqs (T): {np.round(np.sort(pk), 2)}")
        except Exception as e:
            print("  fft fail", lab, e)
    dF = 1 / (1 / onset - 1 / Bmax)
    axs[2, j].axvline(FL, color="g", ls="--", label=f"F_L {FL:.1f} T")
    for fr in [0.72 * FL, 0.28 * FL]:
        axs[2, j].axvline(fr, color="orange", ls=":", label=f"ABAB asymptote {fr:.1f}")
    axs[2, j].set_xlim(0, 1.5 * FL + 5); axs[2, j].set_xlabel("F (T)"); axs[2, j].legend(fontsize=7)
    axs[2, j].set_title(f"1/B FFT, deltaF = {dF:.2f} T")
    out[rid]["FL"] = FL; out[rid]["dF"] = dF
fig.tight_layout(); fig.savefig("hera_scratch/spot_e_h.png", dpi=110)
json.dump(out, open("hera_scratch/spot_read.json", "w"), indent=1, default=float)

print("\n=== model F(n) table (1e12 cm^-2 units probe) ===")
for n in [0.8, 1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 3.2, -1.0, -1.2]:
    try:
        ef, orbs = m.abab_fs(n); ms = m.abab_mstar(n)
        Ft, mA = m.abca_mstar(n)
        FL = float(luttinger_frequency(abs(n) * 1e16))
        print(f"n={n:+.1f}: F_L={FL:5.1f}  ABAB F={[round(F,2) for F,k in orbs]} m*={[round(mm,3) for F,mm in ms]}  "
              f"ABCA F={Ft:.2f} m*={mA:.3f}")
    except Exception as e:
        print(f"n={n}: {e}")
