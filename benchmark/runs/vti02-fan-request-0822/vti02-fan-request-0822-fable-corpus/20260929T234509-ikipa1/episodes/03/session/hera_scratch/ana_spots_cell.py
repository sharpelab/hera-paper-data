"""Runs 6-7 (sdh-spot-check, D = 0): raw -> onset -> FFT vs F_L and the FS-count model.
Electron n = +3.2e12 (run 6), hole n = -1.2e12 (run 7). Design inputs for the Landau fan."""
import sys
from hera.analysis import sdh_onset, SdhOnsetError

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from fs_count_b0 import abab_fs, abab_mstar

H_4E = cst.h / (4 * cst.e)
SENS = 50e-6

fig, axs = plt.subplots(2, 3, figsize=(16, 8))
for row, (rid, n12) in enumerate([(6, +3.2), (7, -1.2)]):
    r = run(rid)
    B, I = r.col("magnet_field"), np.abs(r.col("sr0_X") / 1e6)
    Rxx = r.col("sr1_X") / I
    idx = np.argsort(B)
    B, Rxx = B[idx], Rxx[idx]
    FL = H_4E * abs(n12) * 1e16
    _, orbs = abab_fs(n12 * 1e16)
    ms = abab_mstar(n12 * 1e16)
    print(f"===== run {rid}: n = {n12:+.1f}e12, F_L = {FL:.1f} T; model ABAB orbits: "
          + ", ".join(f"{F:.2f} T [m*={m:.3f}]" for (F, _), (_, m) in zip(orbs, ms)) + " =====")
    on = sdh_onset(Rxx, B, r_full_scale=SENS / np.mean(I))
    print(on.summary())
    if rid == 6:  # coarse-leg alias screen: re-track on the fine 10 mT leg only
        m1 = B >= 1.0
        on1 = sdh_onset(Rxx[m1], B[m1], r_full_scale=SENS / np.mean(I))
        print("--- run 6, fine leg only (B >= 1 T, 10 mT) ---")
        print(on1.summary())

    # raw
    axs[row, 0].plot(B, Rxx, lw=0.6)
    axs[row, 0].axvline(on.onset_b, color="r", ls="--", lw=0.8, label=f"onset {on.onset_b:.2f} T")
    axs[row, 0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {rid} raw, n = {n12:+.1f}e12")
    axs[row, 0].legend(fontsize=7)
    # bg-subtracted vs 1/B (detrend in B before the 1/B view)
    mm = B >= max(0.3, 0.9 * on.onset_b)
    dR = Rxx[mm] - np.polyval(np.polyfit(B[mm], Rxx[mm], 5), B[mm])
    axs[row, 1].plot(1 / B[mm], dR, lw=0.5)
    axs[row, 1].set(xlabel="1/B (1/T)", ylabel="dRxx (Ohm)", title=f"run {rid} bg-subtracted (deg-5 in B)")
    # FFT, two low-B cuts (stability)
    for cut in (on.onset_b, 1.3 * on.onset_b):
        cut = max(cut, 0.31)
        freqs, spec = sdh_fft(Rxx.reshape(-1, 1), B, b_range=(cut, B.max()), bg_degree=5)
        axs[row, 2].plot(freqs, spec[0] / np.nanmax(spec[0]), lw=0.8, label=f"cut {cut:.2f} T")
    axs[row, 2].axvline(FL, color="k", ls=":", lw=1.2, label=f"F_L = {FL:.1f} T")
    for (F, _), (_, m) in zip(orbs, ms):
        axs[row, 2].axvline(F, color="b", ls="--", lw=0.7)
    axs[row, 2].set(xlim=(0, 1.5 * FL), xlabel="F (T)", ylabel="FFT (norm)",
                    title=f"run {rid} FFT in 1/B (blue dashes: model ABAB)")
    axs[row, 2].legend(fontsize=7)
fig.tight_layout()
plt.show()
