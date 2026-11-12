"""SdH spot checks, runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw MR,
onset (hera.analysis.sdh_onset), 1/B FFT, tones vs F_L. Sets the fan design."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import (open_run, summarize_run, sdh_onset, sdh_fft,
                           luttinger_frequency, GateCalibration, SdhOnsetError)

HERE = Path("/home/hera/measurements/zack/20260822-vti-02")
cal_d = json.load(open(HERE / "hera_scratch" / "cal_run5.json"))
cal = GateCalibration(c_tg=cal_d["c_tg"], c_bg=cal_d["c_bg"],
                      n_offset=cal_d["n_offset"] * 1e16, D_offset=cal_d["D_offset"] * 1e9)

fig, axes = plt.subplots(2, 3, figsize=(16, 8))
out = {}
for k, rid in enumerate([6, 7]):
    run = open_run(HERE / "data" / str(rid))
    print("=" * 70)
    print(f"RUN {rid}")
    print(summarize_run(run))
    mc = run.metadata["measurement_config"]
    gain = mc["sr0_gain"]  # unused: sr1 is the Rxx channel
    B = run.col("magnet_field")
    T = run.col("T_sample")
    vtg, vbg = run.col("k_2400_tg_curr"), run.col("k_2400_bg_curr")
    # Rxx from sr1 (gain 1, unity) / I_bias ; I_bias = sr1 amplitude / bias resistor
    # sr1 is BOTH the drive oscillator and the Rxx voltage channel (device card).
    sens = None
    inst = run.metadata.get("instruments", {})
    amp = inst.get("sr1", {}).get("snapshot", {}).get("parameters", {}).get("amplitude", {}).get("value")
    sen = inst.get("sr1", {}).get("snapshot", {}).get("parameters", {}).get("sensitivity", {}).get("value")
    tau = inst.get("sr1", {}).get("snapshot", {}).get("parameters", {}).get("time_constant", {}).get("value")
    slope = inst.get("sr1", {}).get("snapshot", {}).get("parameters", {}).get("filter_slope", {}).get("value")
    print(f"  sr1 amplitude={amp} sensitivity={sen} tau={tau} slope={slope}")
    I_bias = (amp / mc["bias_resistor"]) if amp else None
    sr1X = run.col("sr1_X")
    R = np.abs(sr1X) / I_bias if I_bias else np.abs(sr1X)
    print(f"  N={len(B)} pts; B {B.min():.3f}..{B.max():.3f} T; T {np.nanmin(T):.3f}..{np.nanmax(T):.3f} K")
    print(f"  I_bias = {I_bias*1e9:.3f} nA; R {R.min():.1f}..{R.max():.1f} Ohm")
    print(f"  gate curr TG {np.abs(vtg).max()*1e12:.0f} pA max, BG {np.abs(vbg).max()*1e12:.0f} pA max")
    # density at the spot
    Vtg_set = float(np.median(run.col("k_tg_volt"))) if "k_tg_volt" in run.metadata["columns"] else None
    n_txt = run.metadata["comments"][1]
    n_val = float(n_txt.split("n = ")[1].split(" cm")[0])
    FL = luttinger_frequency(abs(n_val) * 1e4)   # cm^-2 -> m^-2
    print(f"  n = {n_val:+.2f}e12 -> F_L = {FL:.2f} T")

    r_fs = (sen / I_bias) if (sen and I_bias) else None
    ax = axes[k]
    ax[0].plot(B, R, lw=0.6)
    ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("Rxx (Ohm)")
    ax[0].set_title(f"run {rid}: raw Rxx vs B (n={n_val:+.2f}e12)")
    if r_fs:
        ax[0].axhline(r_fs, color="r", ls=":", lw=1, label=f"full scale {r_fs:.0f}")
        ax[0].legend(fontsize=7)

    # background-subtracted, plotted vs 1/B
    ok = B > 0.25
    Bo, Ro = B[ok], R[ok]
    cf = np.polyfit(Bo, Ro, 5)
    dR = Ro - np.polyval(cf, Bo)
    ax[1].plot(1.0 / Bo, dR, lw=0.7)
    ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("dRxx (Ohm)")
    ax[1].set_title(f"run {rid}: bg-subtracted (deg 5) vs 1/B")

    # onset
    try:
        on = sdh_onset(Ro, Bo, r_full_scale=r_fs)
        print(on.summary())
        onset_b = on.onset_b
        out[rid] = {"onset_b": float(onset_b), "clip_high_b": on.clip_high_b,
                    "tones": [{"freq": float(t.freq), "onset_b": float(t.onset_b),
                               "censored": bool(t.censored), "marginal": bool(t.marginal),
                               "harmonic_of": t.harmonic_of,
                               "delta_f": float(t.delta_f(Bo.max()))} for t in on.tones]}
    except SdhOnsetError as e:
        print(f"  SdhOnsetError: {e}")
        onset_b = None
        out[rid] = {"onset_b": None, "error": str(e)}

    # FFT over a few cutoffs (stability sweep)
    for cut, col in [(0.5, "C0"), (1.0, "C1"), (2.0, "C2"), (3.0, "C3")]:
        if cut >= Bo.max():
            continue
        f, spec = sdh_fft(Ro[:, None], Bo, b_range=(cut, Bo.max()), bg_degree=5, log=False)
        s = spec[0]
        s = s / s[(f > 1) & (f < 80)].max()
        ax[2].plot(f, s, col, lw=0.8, label=f"cut {cut} T")
        pk = f[(f > 1.5) & (f < 80)][np.argsort(s[(f > 1.5) & (f < 80)])[-4:]][::-1]
        print(f"  FFT cut {cut}-{Bo.max():.1f} T: top freqs {np.round(pk,2)} T; dF={1/(1/cut-1/Bo.max()):.2f} T")
    ax[2].axvline(FL, color="k", ls="--", lw=1, label=f"F_L={FL:.1f} T")
    ax[2].axvline(0.72 * FL, color="g", ls=":", lw=1, label="0.72 F_L")
    ax[2].axvline(0.28 * FL, color="m", ls=":", lw=1, label="0.28 F_L")
    ax[2].set_xlim(0, max(60, 1.4 * FL)); ax[2].set_xlabel("F (T)"); ax[2].set_ylabel("|FFT| (norm)")
    ax[2].set_title(f"run {rid}: 1/B FFT, cutoff ladder")
    ax[2].legend(fontsize=6)
    out[rid].update({"n": n_val, "F_L": float(FL), "I_bias": float(I_bias), "r_full_scale": r_fs,
                     "tau": tau, "slope": slope, "sens": sen, "npts": len(B),
                     "R_min": float(R.min()), "R_max": float(R.max()),
                     "duration_s": float(run.col("time")[-1] - run.col("time")[0])})

fig.tight_layout()
fig.savefig(HERE / "hera_scratch" / "spot_runs67.png", dpi=110)
json.dump(out, open(HERE / "hera_scratch" / "spot_runs67.json", "w"), indent=1, default=str)
print("\nwrote spot_runs67.png / .json")
