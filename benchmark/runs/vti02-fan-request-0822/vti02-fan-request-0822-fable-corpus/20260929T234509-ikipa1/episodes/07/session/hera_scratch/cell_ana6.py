"""sdh-spot-check run 6 — electron side, n = +3.2e12, D = 0, B 0->10 T (50 mT to 1 T, 10 mT above).
Raw MR first; onset + tones on the trustworthy fine grid (B >= 1 T: the 50 mT leg
under-samples the 7.3 T tone below ~0.85 T in 1/B); FFT vs model tone predictions."""
import sys
from hera.analysis import sdh_onset
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
from fs_count_b0 import abab_fs, abca_fs

IB, SENS = 10e-9, 50e-6
rid, n_spot = 6, 3.2e12  # cm^-2 units below; model takes m^-2
r6 = run(rid)
print(summarize_run(r6))
B6 = r6.col("magnet_field"); R6 = r6.col("sr1_X") / IB
i = np.argsort(B6); B6, R6 = B6[i], R6[i]
FL6 = luttinger_frequency(n_spot * 1e4)  # m^-2
_, ab = abab_fs(n_spot * 1e4); f_light, f_heavy = ab[0][0], ab[1][0]
*_, F_abca = abca_fs(n_spot * 1e4)
_, abB = abab_fs((n_spot + 0.43e12) * 1e4)  # region-B mosaic: +0.43e12 doped

# --- raw first ---
fig, ax = plt.subplots(figsize=(11, 3.2))
ax.plot(B6, R6, lw=0.5, color="k")
ax.set(xlabel="B (T)", ylabel="R_xx (Ohm)", title=f"run 6 raw — n = +3.2e12, D = 0, sr1 50 uV (FS 5 kOhm), T ~ {np.nanmedian(r6.col('T_sample')):.2f} K")
plt.show()

# --- onset: fine grid only (B >= 1 T) ---
m = B6 >= 0.999
on6 = sdh_onset(R6[m], B6[m], r_full_scale=SENS / IB, b_lo=1.0)
print(on6.summary())

# --- FFT vs model ---
freqs, spec = sdh_fft(R6[m][:, None], B6[m], b_range=(1.0, 10.0), nfft=4096)
fig, ax = plt.subplots(figsize=(11, 3.2))
ax.plot(freqs, spec[0], lw=0.8, color="k")
for f, lab, c in [(f_light, f"ABAB light {f_light:.1f}", "tab:blue"), (f_heavy, f"ABAB heavy {f_heavy:.1f}", "tab:red"),
                  (FL6, f"F_L {FL6:.1f} (= ABCA {F_abca:.1f})", "tab:green"), (abB[1][0], f"region-B heavy {abB[1][0]:.1f}", "tab:orange")]:
    ax.axvline(f, color=c, ls="--", lw=1, label=lab)
for k in (2, 3, 4):
    ax.axvline(k * 7.3, color="gray", ls=":", lw=0.8)
ax.set(xlim=(0, 45), xlabel="F (T)", ylabel="log FFT amp", title="run 6 FFT (1/B), B 1-10 T, bg_degree 5; gray dots: k x 7.3 T harmonics")
ax.legend(fontsize=8)
plt.show()
print(f"model (run-5 cal, geometry-prior scale): F_L = {FL6:.1f} T; ABAB pair = {f_light:.2f} / {f_heavy:.2f} T; "
      f"ABCA singleton = {F_abca:.2f} T; region-B (n+0.43e12) ABAB pair = {abB[0][0]:.2f} / {abB[1][0]:.2f} T")
