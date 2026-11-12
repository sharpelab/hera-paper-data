"""Spot-check read: runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12) at D=0.
Raw R(B), sdh_onset per tone, record FFT vs F_L, and the model templates."""
import sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import (open_run, sdh_onset, sdh_fft, luttinger_frequency,
                           resolve_channels, SdhOnsetError)

sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as M

D = Path("/home/hera/measurements/zack/20260822-vti-02/data")
RUNS = {6: ("electron", +3.2), 7: ("hole", -1.2)}

fig, axes = plt.subplots(2, 3, figsize=(16, 8))
out = {}
for k, (rid, (side, n12)) in enumerate(RUNS.items()):
    r = open_run(D / str(rid))
    print(f"\n{'='*70}\nrun {rid} — {side}, n = {n12:+.2f}e12, cols {sorted(set(r.cols))}")
    ch = resolve_channels(r.meta)
    print("channels:", ch)
    B = r.col("magnet_field")
    Ix = r.col("sr0_X"); Vx = r.col("sr1_X")
    gain_cur = r.meta["measurement_config"].get("sr0_gain", -1e6)
    I = Ix / gain_cur
    R = np.abs((Vx / 1.0) / I)
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    T = r.col("T_sample")
    print(f"B {B.min():.3f}-{B.max():.3f} T, {len(B)} pts; R {R.min():.1f}-{R.max():.1f} Ohm; "
          f"I {np.median(I)*1e9:.3f} nA; T {T.min():.3f}-{T.max():.3f} K")
    # sensitivity -> full scale resistance for clip detection
    sens = r.meta["measurement_config"].get("sr1_sens", 50e-6)
    r_fs = sens / abs(np.median(I))
    print(f"sr1 sens {sens} V -> R full scale {r_fs:.0f} Ohm; max R/FS = {R.max()/r_fs:.2f}")

    F_L = luttinger_frequency(abs(n12) * 1e16)   # 1e12 cm^-2 -> m^-2
    print(f"F_L({n12:+.2f}e12) = {F_L:.2f} T")

    ax = axes[k, 0]
    ax.plot(B, R, lw=0.7)
    ax.set_xlabel("B (T)"); ax.set_ylabel("R (Ohm)")
    ax.set_title(f"run {rid} raw — {side} n={n12:+.2f}e12, D=0")

    # --- onset
    try:
        on = sdh_onset(R, B, r_full_scale=r_fs)
        print(on.summary())
        out[rid] = dict(onset_b=float(on.onset_b), onset_freq=float(on.onset_freq),
                        clip_high_b=on.clip_high_b,
                        tones=[dict(freq=float(t.freq), onset_b=float(t.onset_b),
                                    contrast=float(t.contrast), censored=bool(t.censored),
                                    marginal=bool(t.marginal), n_periods=float(t.n_periods),
                                    harmonic_of=t.harmonic_of) for t in on.tones])
    except SdhOnsetError as e:
        print(f"SdhOnsetError: {e}")
        out[rid] = dict(error=str(e))
        on = None

    # --- background-subtracted trace vs 1/B
    bmask = B > 0.9
    p = np.polyfit(B[bmask], R[bmask], 5)
    dR = R[bmask] - np.polyval(p, B[bmask])
    ax = axes[k, 1]
    ax.plot(1.0 / B[bmask], dR, lw=0.7)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dR (Ohm)")
    ax.set_title(f"run {rid} bg-subtracted (B>0.9 T)")

    # --- FFT on several windows
    ax = axes[k, 2]
    for blo, bhi, lab in [(1.0, 10.0, "1-10 T"), (1.0, 4.5, "1-4.5 T"),
                          (4.5, 10.0, "4.5-10 T"), (2.0, 10.0, "2-10 T")]:
        m = (B >= blo) & (B <= bhi)
        if m.sum() < 40:
            continue
        f, spec = sdh_fft(R[m][:, None], B[m], nfft=4096, log=False, bg_degree=5)
        s = spec[0]
        ax.plot(f, s / s[(f > 1)].max(), lw=0.8, label=lab)
        pk = [(f[i], s[i]) for i in range(2, len(f) - 2)
              if s[i] == max(s[max(0, i-3):i+4]) and f[i] > 1.5 and s[i] > 0.15 * s[f > 1.5].max()]
        print(f"  FFT {lab}: dF={1/(1/max(blo,B[m].min())-1/B[m].max()):.2f} T; peaks "
              + ", ".join(f"{a:.1f}T({b/max(x[1] for x in pk):.2f})" for a, b in pk))
    ax.axvline(F_L, color="k", ls="--", lw=1, label=f"F_L={F_L:.1f} T")
    ax.set_xlim(0, max(60, F_L * 1.8)); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)")
    ax.legend(fontsize=7); ax.set_title(f"run {rid} FFT windows")

    # --- model templates at this density
    try:
        Ef, orbs = M.abab_fs(n12 * 1e16)
        ms = M.abab_mstar(n12 * 1e16)
        print(f"  MODEL ABAB: orbits " + ", ".join(f"F={F:.2f}T" for F, _ in orbs)
              + " | m* " + ", ".join(f"{F:.1f}T:{m:.4f}" for F, m in ms)
              + f" | sum/F_L = {sum(F for F, _ in orbs)/F_L:.3f}")
    except Exception as e:
        print("  ABAB model:", e)
    try:
        Ef, topo, ncomp, nfreq, Ftot = M.abca_fs(n12 * 1e16)
        Fm, mm = M.abca_mstar(n12 * 1e16)
        print(f"  MODEL ABCA: topo={topo} ncomp={ncomp} nfreq={nfreq} F_total={Ftot:.2f} T, m*={mm:.4f}")
    except Exception as e:
        print("  ABCA model:", e)

plt.tight_layout()
plt.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_runs67.png", dpi=110)
json.dump(out, open("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_onsets.json", "w"), indent=1)
print("\nwrote spot_runs67.png, spot_onsets.json")
