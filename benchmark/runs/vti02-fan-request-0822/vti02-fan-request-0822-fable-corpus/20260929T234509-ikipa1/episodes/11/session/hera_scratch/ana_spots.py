"""Spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D=0.
Raw MR, sdh_onset, sdh_fft vs F_L and the fs_count model. Fan-design inputs out."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"

for rid, nval, side in ((6, 3.2e12, "electron"), (7, -1.2e12, "hole")):
    run = open_run(f"{BASE}/{rid}")
    print("=" * 80)
    print(summarize_run(run))
    B = run.col("magnet_field")
    T = run.col("T_sample")
    # sr1 = Rxx channel, unity gain; I_bias from metadata drive amplitude / bias resistor
    mc = run.meta["measurement_config"]
    from hera.analysis import resistance_grids
    try:
        rg = resistance_grids(run)
        print("resistance_grids channels:", list(rg.channels) if hasattr(rg, "channels") else rg)
    except Exception as e:
        print("resistance_grids failed:", e)
        rg = None
    # fall back: manual
    x1 = run.col("sr1_X")
    # I_bias: sr1 is drive channel; amplitude from instruments snapshot
    try:
        amp = run.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"]
    except Exception:
        amp = None
    print("sr1 osc amplitude:", amp)
    Rbias = mc["bias_resistor"]
    I = (amp / Rbias) if amp else 1e-8
    R = x1 / I
    print(f"I_bias = {I*1e9:.3f} nA;  R range {np.nanmin(R):.1f} .. {np.nanmax(R):.1f} Ohm; T {np.nanmin(T):.3f}-{np.nanmax(T):.3f} K")
    F_L = luttinger_frequency(nval) if callable(luttinger_frequency) else None
    print(f"F_L = {F_L} T for n = {nval:.2e}")
    # sensitivity for clip guard
    sens = 50e-6
    order = np.argsort(B)
    Bs, Rs = B[order], R[order]
    # dedupe field values
    ub, idx = np.unique(np.round(Bs, 5), return_index=True)
    Bs, Rs = Bs[idx], Rs[idx]
    try:
        on = sdh_onset(Rs, Bs, r_full_scale=sens / I)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
        onset = None
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    ax[0].plot(Bs, Rs, lw=0.6)
    ax[0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {rid} ({side}, n={nval/1e12:+.1f}e12) raw")
    if onset:
        ax[0].axvline(onset, color="r", ls="--", lw=0.8)
    for cut in ([onset] if onset else [1.5]):
        if cut is None:
            continue
        try:
            freqs, spec = sdh_fft(Rs[:, None], Bs, b_range=(cut, Bs.max()), bg_degree=5)
            sp = spec[0]
            ax[1].plot(freqs, sp / np.nanmax(sp), lw=0.8, label=f"cut={cut:.2f} T")
            # top peaks
            from scipy.signal import find_peaks
            pk, props = find_peaks(sp, height=0.03 * np.nanmax(sp), distance=5)
            top = sorted(zip(sp[pk], freqs[pk]), reverse=True)[:8]
            print(f"FFT (cut {cut:.2f} T) top peaks (amp_rel, F[T]):",
                  [(round(a / top[0][0], 3), round(f, 2)) for a, f in top])
        except Exception as e:
            print("sdh_fft failed:", e)
    if F_L:
        ax[1].axvline(F_L, color="k", ls=":", lw=0.8)
    ax[1].set(xlabel="F (T)", ylabel="FFT amp (norm)", title=f"run {rid} FFT in 1/B; dotted = F_L")
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(f"/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_run{rid}.png", dpi=110)
    print(f"saved spot_run{rid}.png")
