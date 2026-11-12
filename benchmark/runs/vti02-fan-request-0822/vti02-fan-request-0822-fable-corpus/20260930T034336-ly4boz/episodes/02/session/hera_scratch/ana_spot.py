"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12):
onset via sdh_onset, per-run FFT vs F_L, B-window split, model overlay markers."""
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

I_BIAS = 10e-9
RFS = 50e-6 / I_BIAS   # 5 kOhm full scale

RUNS = {6: dict(n=3.2e12 * 1e4, label="electron n=+3.2e12"),
        7: dict(n=-1.2e12 * 1e4, label="hole n=-1.2e12")}

# model tones (from md_spot_e/h feasibility tables, fs_count_b0 at these n):
MODEL = {6: dict(FL=33.1, abab=(25.6, 7.5), abca=(33.1,)),
         7: dict(FL=12.4, abab=(7.1, 5.3), abca=(12.4,))}

fig, axes = plt.subplots(2, 3, figsize=(16, 8))
for row, (rid, info) in enumerate(RUNS.items()):
    r = open_run(f"data/{rid}")
    print(f"\n================ run {rid} — {info['label']} ================")
    print(sorted(r.cols))
    B = r.col("magnet_field")
    idx = np.argsort(B); B = B[idx]
    Rxx = (r.col("sr1_X") / 1.0 / I_BIAS)[idx]     # sr1 gain 1
    Isd = np.abs(r.col("sr0_X") / 1e6)[idx]         # measured drain current, A
    Rxx_i = (r.col("sr1_X")[idx] / 1.0) / Isd       # measured-I normalized
    FL = luttinger_frequency(abs(info["n"])) if callable(luttinger_frequency) else None
    print(f"F_L check: helper={FL}, table={MODEL[rid]['FL']}")
    print(f"R range {Rxx.min():.1f}..{Rxx.max():.1f} Ohm; I_sd {Isd.min()*1e9:.2f}..{Isd.max()*1e9:.2f} nA")

    try:
        on = sdh_onset(Rxx_i, B, r_full_scale=RFS)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print(f"SdhOnsetError: {e}")
        onset = None

    ax = axes[row, 0]
    ax.plot(B, Rxx_i, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)"); ax.set_title(f"run {rid} raw — {info['label']}")
    if onset:
        ax.axvline(onset, color="r", ls="--", lw=0.8)

    # FFT: full window above cutoff, plus low/high halves in 1/B
    Bmax = B.max()
    cut = max(onset or 1.5, 1.5)
    windows = {"full": (cut, Bmax)}
    inv_mid = 0.5 * (1 / cut + 1 / Bmax)
    windows["lowB"] = (cut, 1 / inv_mid)
    windows["highB"] = (1 / inv_mid, Bmax)
    specs = {}
    for name, (blo, bhi) in windows.items():
        try:
            f, sp = sdh_fft(Rxx_i[:, None], B, b_range=(blo, bhi))
            specs[name] = (f, sp[0])
        except Exception as e:
            print(f"fft {name} ({blo:.2f}-{bhi:.2f}): {e}")
    if "full" in specs:
        f, sp = specs["full"]
        pk, pr = find_peaks(sp, prominence=(sp.max() - sp.min()) * 0.05)
        order = np.argsort(-pr["prominences"])
        print(f"FFT peaks (full, {windows['full'][0]:.2f}-{Bmax:.2f} T), F_L={MODEL[rid]['FL']} T:")
        for j in order[:8]:
            print(f"  f = {f[pk[j]]:7.2f} T   amp {sp[pk[j]]:.2f}  prom {pr['prominences'][j]:.2f}  f/F_L = {f[pk[j]]/MODEL[rid]['FL']:.3f}")
        ax = axes[row, 1]
        for name, c in (("full", "k"), ("lowB", "tab:blue"), ("highB", "tab:red")):
            if name in specs:
                ax.plot(*specs[name], lw=0.9, color=c, label=name)
        for F, ls, lab in ((MODEL[rid]["FL"], "-", "F_L/ABCA"),
                           (MODEL[rid]["abab"][0], "--", "ABAB heavy"),
                           (MODEL[rid]["abab"][1], ":", "ABAB light")):
            ax.axvline(F, color="g", ls=ls, lw=0.8, label=lab)
        ax.set_xlim(0, MODEL[rid]["FL"] * 1.8); ax.legend(fontsize=7)
        ax.set_xlabel("F (T)"); ax.set_ylabel("FFT amp"); ax.set_title(f"run {rid} FFT vs model")

    # background-subtracted trace vs 1/B above cutoff
    m = B >= cut
    if m.sum() > 20:
        cf = np.polyfit(B[m], Rxx_i[m], 5)
        dR = Rxx_i[m] - np.polyval(cf, B[m])
        ax = axes[row, 2]
        ax.plot(1 / B[m], dR, lw=0.6)
        ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)")
        ax.set_title(f"run {rid} dRxx vs 1/B (deg-5 bg, B>{cut:.2f})")
        print(f"dR rms above cutoff: {np.std(dR):.2f} Ohm; record 1/{Bmax:.1f}..1/{cut:.2f} -> dF = {1/(1/cut - 1/Bmax):.2f} T")

fig.tight_layout()
fig.savefig("hera_scratch/spot_checks.png", dpi=110)
print("\nsaved hera_scratch/spot_checks.png")
