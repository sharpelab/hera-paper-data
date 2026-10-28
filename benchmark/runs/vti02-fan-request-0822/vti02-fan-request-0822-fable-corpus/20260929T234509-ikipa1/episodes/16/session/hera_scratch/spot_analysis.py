# SdH spot checks runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12) — onset + FFT read
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError, resolve_channels

fig, axs = plt.subplots(2, 3, figsize=(15, 7))

for row, (rid, n12) in enumerate(((6, 3.2), (7, -1.2))):
    run = open_run(f"data/{rid}")
    B = run.col("magnet_field")
    order = np.argsort(B)
    B = B[order]
    ch = resolve_channels(run.meta["measurement_config"])
    print(f"run {rid}: channels resolved: {ch}")
    # sr1 voltage (gain 1), current from sr0 (gain -1e6)
    V = run.col("sr1_X")[order]
    Icur = run.col("sr0_X")[order] / (-1e6)
    R = V / Icur
    Rn = V / 1e-10  # nominal I from 10 nA? — report both; use measured-I R for analysis
    print(f"  I measured: {np.nanmedian(np.abs(Icur))*1e9:.3f} nA median; R(B~0) = {np.nanmedian(R[:5]):.1f} Ohm; R range {np.nanmin(R):.1f}..{np.nanmax(R):.1f}")
    r_fs = 50e-6 / np.nanmedian(np.abs(Icur))
    F_L = luttinger_frequency(abs(n12) * 1e16)
    print(f"  F_L = {F_L:.1f} T; r_full_scale = {r_fs:.0f} Ohm")

    axs[row, 0].plot(B, R, lw=0.5)
    axs[row, 0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {rid}: n={n12:+.1f}e12 raw")

    try:
        on = sdh_onset(R, B, r_full_scale=r_fs)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print(f"  SdhOnsetError: {e}")
        onset = None

    if onset is not None:
        b_hi = on.clip_high_b if on.clip_high_b else B.max()
        for cut_label, cut in (("onset", onset), ("onset*1.2", onset * 1.2)):
            freqs, spec = sdh_fft(R[:, None], B, b_range=(cut, b_hi), bg_degree=5)
            sp = spec[0]
            axs[row, 1].plot(freqs, sp / sp.max(), lw=0.8, label=f"cut {cut:.2f} T")
        axs[row, 1].axvline(F_L, color="k", ls="--", label=f"F_L={F_L:.1f} T")
        axs[row, 1].legend(fontsize=7)
        axs[row, 1].set(xlabel="F (T)", xlim=(0, 1.5 * F_L), title=f"run {rid}: FFT in 1/B")
        # background-subtracted trace vs 1/B
        pf = np.polyfit(B[B >= onset], R[B >= onset], 5)
        dR = R - np.polyval(pf, B)
        m = B >= onset
        axs[row, 2].plot(1 / B[m], dR[m], lw=0.5)
        axs[row, 2].set(xlabel="1/B (1/T)", ylabel="dRxx", title=f"run {rid}: bg-subtracted")

plt.tight_layout()
plt.savefig("hera_scratch/spot_checks_67.png", dpi=110)
print("saved hera_scratch/spot_checks_67.png")
