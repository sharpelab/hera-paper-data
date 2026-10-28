# Runs 6 + 7 — sdh-spot-check read: raw MR first, then FFT in 1/B vs the FS-count model
import numpy as np, matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency

I_BIAS = 10e-9
RFS = 50e-6 / I_BIAS                       # 5 kOhm full scale (sr1 gain 1)
# model tones: fs_count_b0 (ABAB SWMcC / ABCA 8-band), hera_scratch/model_Fn_electron.json + md_spot_h table
MODEL = {6: dict(n="+3.2e12 (electron)", FL=33.09, abab=(25.78, 7.31), note="ABCA singleton 33.1"),
         7: dict(n="-1.2e12 (hole)",     FL=12.41, abab=(7.1, 5.3),    note="ABCA singleton 12.4")}

fig, axes = plt.subplots(2, 3, figsize=(15, 7.5))
for row, rid in enumerate((6, 7)):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field"); idx = np.argsort(B); B = B[idx]
    Rxx = (r.col("sr1_X")[idx] / 1.0) / np.abs(r.col("sr0_X")[idx] / 1e6)   # measured-I normalized
    on = sdh_onset(Rxx, B, r_full_scale=RFS)
    print(f"— run {rid} ({MODEL[rid]['n']}), F_L = {MODEL[rid]['FL']} T —")
    print(on.summary())

    ax = axes[row, 0]                                          # raw first
    ax.plot(B, Rxx, lw=0.6); ax.axvline(on.onset_b, color="r", ls="--", lw=0.8)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ω)")
    ax.set_title(f"run {rid} raw — {MODEL[rid]['n']}")

    cut = 1.5
    f, sp = sdh_fft(Rxx[:, None], B, b_range=(cut, B.max())); sp = sp[0]
    pk, pr = find_peaks(sp, prominence=(sp.max() - sp.min()) * 0.05)
    print(f"  FFT peaks ({cut}-{B.max():.0f} T):", ", ".join(
        f"{f[p]:.2f} T ({f[p]/MODEL[rid]['FL']:.2f} F_L)" for p in pk[np.argsort(-pr['prominences'])][:6]))
    ax = axes[row, 1]
    ax.plot(f, sp, "k", lw=0.9)
    ax.axvline(MODEL[rid]["FL"], color="g", lw=1.0, label="F_L / ABCA")
    ax.axvline(MODEL[rid]["abab"][0], color="g", ls="--", lw=0.8, label="ABAB heavy (model)")
    ax.axvline(MODEL[rid]["abab"][1], color="g", ls=":", lw=0.8, label="ABAB light (model)")
    ax.set_xlim(0, MODEL[rid]["FL"] * 2); ax.legend(fontsize=7)
    ax.set_xlabel("F (T)"); ax.set_ylabel("FFT amp"); ax.set_title(f"run {rid} FFT (1/B) vs model")

    m = B >= cut
    dR = Rxx[m] - np.polyval(np.polyfit(B[m], Rxx[m], 5), B[m])
    ax = axes[row, 2]
    ax.plot(1 / B[m], dR, lw=0.6)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("ΔRxx (Ω)"); ax.set_title(f"run {rid} ΔRxx vs 1/B")

fig.tight_layout(); plt.show()
print("\nrun 6 tone algebra: 7.05 + 22.90 = 29.95 (sum/breakdown @ 0.905·F_L), 22.90 - 7.05 = 15.85 (intermod);")
print("global scale 0.905 -> ABAB pair partition measured 0.235/0.765 vs model 0.21/0.79 at n = 2.9e12")
