# Runs 6 + 7 — sdh-spot-check pair at D = 0: raw Rxx(B), per-tone onsets, FFT in 1/B vs F_L
from hera.analysis import open_run, sdh_onset, sdh_fft
import numpy as np, matplotlib.pyplot as plt

def load(rid):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field"); o = np.argsort(B)
    amp = r.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"]
    ib = amp / r.meta["measurement_config"]["bias_resistor"]          # 10 nA
    return B[o], (r.col("sr1_X") / 1.0 / ib)[o], ib                   # sr1 gain = 1

# model references (fs_count_b0, run-5 calibration densities; computed this session)
MODEL = {6: dict(FL=33.09, abab=(7.31, 25.78), lbl="run 6 — electron n=+3.2e12"),
         7: dict(FL=12.41, abab=(5.86, 6.54),  lbl="run 7 — hole n=−1.2e12")}
CLEAN_BLO = {6: 1.00, 7: 0.30}   # run 6: 50 mT below 1 T (aliased) — clean grid starts at 1 T

fig, axes = plt.subplots(3, 2, figsize=(13, 11))
for j, rid in enumerate((6, 7)):
    B, R, ib = load(rid); t = MODEL[rid]
    blo = CLEAN_BLO[rid]; m = B >= blo
    axes[0, j].plot(B, R, lw=0.5); axes[0, j].set_title(f"{t['lbl']}: raw Rxx(B)")
    axes[0, j].set_xlabel("B (T)"); axes[0, j].set_ylabel("Rxx (Ω)")

    on = sdh_onset(R[m], B[m], r_full_scale=50e-6 / ib)               # sens 50 uV
    print(f"=== {t['lbl']} (analysis window B >= {blo} T) ===")
    print(on.summary())

    pf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(pf, B[m])
    axes[1, j].plot(B[m], dR, lw=0.5)
    axes[1, j].set_title("ΔRxx (deg-5 B-space background removed)"); axes[1, j].set_xlabel("B (T)")

    ax = axes[2, j]
    win = [(max(on.onset_b, blo), 10.0, "-")]
    if rid == 6:
        win += [(1.0, 3.2, "--"), (3.2, 10.0, ":")]                   # B-window split (F_L-tone origin check)
    for lo, hi, st in win:
        f, spec = sdh_fft(R[m][:, None], B[m], b_range=(lo, hi), bg_degree=5, log=False)
        sp = spec[0] / spec[0][f > 2].max()
        ax.plot(f, sp, st, lw=1, label=f"{lo:.1f}–{hi:.1f} T")
    ax.axvline(t["FL"], color="k", lw=1); ax.text(t["FL"], 1.02, "F_L", ha="center")
    for fa in t["abab"]:
        ax.axvline(fa, color="tab:red", ls="--", lw=1, alpha=0.6)
    ax.set_xlim(0, t["FL"] * 1.6); ax.set_xlabel("F (T)"); ax.legend(fontsize=7)
    ax.set_title(f"FFT in 1/B (black F_L = {t['FL']} T; red dashed model ABAB pair)")
fig.tight_layout(); plt.show()
