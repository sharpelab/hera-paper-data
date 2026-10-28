# scratch harness: mimic ana-notebook namespace, then run the promotable cells
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run, sdh_fft

file_path = "data"
def run(i):
    return open_run(Path(file_path) / str(i))

# ============== promotable cell: run 6 ==============
# Run 6 — SdH spot check, electron side (n = +3.2e12, D = 0), B 0->10 T
from hera.analysis import sdh_onset, resolve_channels, current_channel

def spot_channels(r):
    """Gain-divided Rxx = (V_sr1/gain)/I_drain, ascending in B."""
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    v = [c for c in chans if c.cid == "sr1"][0]
    I = r.col(cur.col) / cur.gain
    R = np.abs((r.col(v.col) / v.gain) / I)
    B = r.col("magnet_field")
    o = np.argsort(B)
    return B[o], R[o], np.abs(I[o])

def spot_read(rid, F_L, model, fft_cut, title):
    r = run(rid)
    print(summarize_run(r))
    B, R, I = spot_channels(r)
    m = B > 0.05
    B, R = B[m], R[m]
    r_fs = 50e-6 / np.nanmedian(I)   # sr1 sens 50 uV over measured I_bias
    on = sdh_onset(R, B, r_full_scale=r_fs)
    print(on.summary())

    fig, ax = plt.subplots(1, 3, figsize=(15, 3.6))
    # raw first
    ax[0].plot(B, R, lw=0.6, color="k")
    ax[0].set_xlabel("B (T)"); ax[0].set_ylabel(r"$R_{xx}$ ($\Omega$)")
    ax[0].set_title(f"run {rid} raw — {title}")
    # background-subtracted vs 1/B (bg poly in B, per recipe)
    msk = B >= fft_cut
    dR = R[msk] - np.polyval(np.polyfit(B[msk], R[msk], 5), B[msk])
    ax[1].plot(1 / B[msk], dR, lw=0.6)
    ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel(r"$\Delta R_{xx}$ ($\Omega$)")
    ax[1].set_title(f"bg-subtracted, B > {fft_cut:g} T")
    # FFT, two cutoffs (stability), F_L + model tone markers
    for cut in (fft_cut, fft_cut * 1.3):
        f, s = sdh_fft(R[B >= 0.05][:, None], B[B >= 0.05], b_range=(cut, B.max()), bg_degree=5, log=False)
        ax[2].plot(f, s[0] / s[0].max(), lw=0.8, label=f"cutoff {cut:.2f} T")
    ax[2].axvline(F_L, color="k", ls=":", lw=1, label=f"$F_L$ = {F_L:.1f} T")
    for lab, fm in model.items():
        ax[2].axvline(fm, color="tab:red", ls="--", lw=0.7, alpha=0.6)
        ax[2].text(fm, 1.02, lab, fontsize=7, ha="center", color="tab:red")
    ax[2].set_xlim(0, 1.35 * F_L)
    ax[2].set_xlabel("F (T)"); ax[2].set_ylabel("|FFT| (norm)")
    ax[2].legend(fontsize=7, loc="upper right")
    dF = 1 / (1 / fft_cut - 1 / B.max())
    print(f"FFT window [{fft_cut:g}, {B.max():g}] T -> record resolution dF = {dF:.2f} T")
    fig.tight_layout()
    return on

# F_L = (h/4e)n = 33.1 T at n = +3.2e12; model (fs_count_b0, run-5 cal densities):
# ABAB pair 7.3 / 25.8 T (m* 0.027/0.061), ABCA singleton 33.1 T (m* 0.074).
# FFT cutoff 1.0 T: the 50 mT leg below 1 T under-samples the tones (Nyquist
# ~7 T at 0.85 T) — only the 10 mT leg feeds the FFT.
on6 = spot_read(6, 33.1, {"ABAB f1": 7.3, "ABAB f2": 25.8, "ABCA": 33.1}, 1.0,
                "e-side n=+3.2e12")
f1, f2 = 7.1, 22.2
print(f"\nLuttinger: f1 + f2 = {f1 + f2:.1f} T = {(f1 + f2) / 33.1:.3f} x F_L "
      f"(lever-arm scale prior 0.8-1.2); partition {f1/(f1+f2):.2f}/{f2/(f1+f2):.2f} "
      f"vs model ABAB 0.22/0.78")
plt.savefig("hera_scratch/ana_run6.png", dpi=110)

# ============== promotable cell: run 7 ==============
plt.figure()
on7 = spot_read(7, 12.4, {"ABAB f1": 5.3, "ABAB f2": 7.1, "ABCA": 12.4}, 0.8,
                "h-side n=-1.2e12")
print(f"\nLuttinger: 4.7 + 6.6 = 11.3 T = {11.3/12.4:.3f} x F_L (e-side gave 0.885)")
plt.savefig("hera_scratch/ana_run7.png", dpi=110)
