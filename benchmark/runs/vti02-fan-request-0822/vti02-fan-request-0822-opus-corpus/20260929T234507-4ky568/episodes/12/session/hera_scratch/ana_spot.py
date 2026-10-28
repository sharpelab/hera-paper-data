"""SdH spot checks, runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12).
Onset + 1/B FFT read; the numbers the landau fan inherits."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, luttinger_frequency

D = "/home/hera/measurements/zack/20260822-vti-02/data"
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

def load(fid):
    r = open_run(f"{D}/{fid}")
    print("="*70); print(f"run {fid}"); print(summarize_run(r))
    print("cols:", r.cols)
    B = r.col("magnet_field")
    # channel arithmetic per device card: R = (sr1_X/gain_sr1) / (sr0_X/gain_sr0)
    mcfg = r.meta.get("measurement_config", {})
    print("meas_config gains:", {k: v for k, v in mcfg.items() if "gain" in str(k).lower()})
    v = r.col("sr1_X"); i = r.col("sr0_X")
    g1 = float(mcfg.get("sr1_gain", 1.0)); g0 = float(mcfg.get("sr0_gain", -1e6))
    R = np.abs((v / g1) / (i / g0))
    T = r.col("T_sample") if "T_sample" in r.cols else None
    itg = r.col("k_2400_tg_curr") if "k_2400_tg_curr" in r.cols else None
    return r, B, R, T, itg, (g0, g1)

for fid, n12, label in ((6, +3.20, "electron"), (7, -1.20, "hole")):
    r, B, R, T, itg, g = load(fid)
    o = np.argsort(B); B, R = B[o], R[o]
    n_si = abs(n12) * 1e12 * 1e4          # cm^-2 -> m^-2
    FL = float(luttinger_frequency(n_si))
    print(f"\nn = {n12:+.2f}e12 cm^-2  ->  F_L = {FL:.2f} T")
    print(f"B: {B.min():.3f} -> {B.max():.3f} T, {len(B)} pts")
    print(f"R: min {R.min():.1f}  max {R.max():.1f}  R(B~0) {R[:5].mean():.1f} Ohm")
    if T is not None: print(f"T_sample: {np.nanmin(T):.3f} - {np.nanmax(T):.3f} K")
    if itg is not None: print(f"|I_tg| max {np.nanmax(np.abs(itg)):.2e} A")

    # sensitivity -> full-scale R for clip detection
    sens = 50e-6
    mcfg = r.meta.get("measurement_config", {})
    print("mc keys:", list(mcfg.keys()))
    Ibias = None
    for k, v in mcfg.items():
        if "bias" in str(k).lower() or "amplitude" in str(k).lower():
            print("  bias-ish:", k, v)
    try:
        amp = float(mcfg.get("sr1_amplitude", mcfg.get("Amplitude (V)", 1.0)))
    except Exception:
        amp = 1.0
    Ibias = amp / 100e6
    rfs = sens / Ibias
    print(f"I_bias ~ {Ibias:.3e} A (amp {amp} V / 100 MOhm); R_full_scale ~ {rfs:.0f} Ohm; R_max/FS = {R.max()/rfs:.2f}")

    try:
        on = sdh_onset(R, B, r_full_scale=rfs)
        print("\n--- sdh_onset ---"); print(on.summary())
        print("onset_b =", on.onset_b, " clip_high_b =", on.clip_high_b)
        for t in on.tones:
            print(f"  tone F={t.freq:8.2f} T  onset={t.onset_b:.3f} T  dF={t.delta_f(B.max()):.2f}"
                  f"  F/F_L={t.freq/FL:.3f}  censored={t.censored} marginal={t.marginal}"
                  f" harm_of={t.harmonic_of}")
    except Exception as e:
        print("sdh_onset FAILED:", type(e).__name__, e); on = None

    # FFT over the usable window
    blo = max(on.onset_b if on else 1.5, 1.0)
    bhi = (on.clip_high_b if (on and on.clip_high_b) else B.max())
    freqs, spec = sdh_fft(R[:, None], B, b_range=(blo, bhi), bg_degree=5)
    sp = spec[0]
    print(f"\nFFT window {blo:.2f}-{bhi:.2f} T; dF_res = {1/(1/blo - 1/bhi):.2f} T")
    # peak list
    from scipy.signal import find_peaks
    pk, _ = find_peaks(sp, height=np.max(sp) * 0.06)
    order = np.argsort(sp[pk])[::-1]
    print("peaks (F [T], rel amp, F/F_L):")
    for p in pk[order][:10]:
        print(f"   {freqs[p]:8.2f}  {sp[p]/sp[pk].max():6.3f}   {freqs[p]/FL:6.3f}")

    # B-window split (F_L-tone origin diagnostic)
    bmid = 2 / (1/blo + 1/bhi)
    for w, (a, b) in (("low ", (blo, bmid)), ("high", (bmid, bhi))):
        f2, s2 = sdh_fft(R[:, None], B, b_range=(a, b), bg_degree=5)
        s2 = s2[0]
        p2, _ = find_peaks(s2, height=np.max(s2) * 0.1)
        top = p2[np.argsort(s2[p2])[::-1]][:5]
        print(f"  {w} half {a:.2f}-{b:.2f} T: " + ", ".join(f"{f2[t]:.1f}T({s2[t]/s2[top].max():.2f})" for t in top))

    # plots
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.2))
    ax[0].plot(B, R, lw=0.7); ax[0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {fid} raw — {label} n={n12:+.2f}e12")
    m = (B >= blo) & (B <= bhi)
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[1].plot(1/B[m], R[m]-bg, lw=0.8); ax[1].set(xlabel="1/B (1/T)", ylabel="dRxx (Ohm)", title="bg-subtracted vs 1/B")
    ax[2].plot(freqs, sp, lw=1.0); ax[2].axvline(FL, color="r", ls="--", label=f"F_L={FL:.1f} T")
    for frac, c in ((0.72, "g"), (0.28, "m")):
        ax[2].axvline(frac*FL, color=c, ls=":", label=f"{frac}F_L={frac*FL:.1f}")
    ax[2].set(xlim=(0, 1.6*FL), xlabel="F (T)", ylabel="|FFT|", title="1/B FFT"); ax[2].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(f"/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_run{fid}.png", dpi=110)
    print(f"saved spot_run{fid}.png\n")
