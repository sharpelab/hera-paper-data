"""sdh-spot-check run 7 — hole side, n = -1.2e12, D = 0, B 10->0.3 T uniform 20 mT (ride-down).
Raw MR first; onset + tones (20 mT grid resolves the ~6.6 T tone down to ~0.5 T, so the
0.71 T onset is a measured die-off, unlike run 6's censored edge); FFT vs model tones."""
import sys
from hera.analysis import sdh_onset
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
from fs_count_b0 import abab_fs, abca_fs, abca_mstar

IB, SENS = 10e-9, 50e-6
r7 = run(7)
print(summarize_run(r7))
B7 = r7.col("magnet_field"); R7 = r7.col("sr1_X") / IB
i = np.argsort(B7); B7, R7 = B7[i], R7[i]
FL7 = luttinger_frequency(1.2e12 * 1e4)
_, ab7 = abab_fs(-1.2e12 * 1e4)
*_, F_abca7 = abca_fs(-1.2e12 * 1e4)
_, m_abca7 = abca_mstar(-1.2e12 * 1e4)

# --- raw first ---
fig, ax = plt.subplots(figsize=(11, 3.2))
ax.plot(B7, R7, lw=0.5, color="k")
ax.set(xlabel="B (T)", ylabel="R_xx (Ohm)", title=f"run 7 raw — n = -1.2e12, D = 0, sr1 50 uV (FS 5 kOhm), T ~ {np.nanmedian(r7.col('T_sample')):.2f} K")
plt.show()

# --- onset ---
on7 = sdh_onset(R7, B7, r_full_scale=SENS / IB)
print(on7.summary())

# --- FFT vs model ---
freqs7, spec7 = sdh_fft(R7[:, None], B7, b_range=(0.71, 10.0), nfft=4096)
fig, ax = plt.subplots(figsize=(11, 3.2))
ax.plot(freqs7, spec7[0], lw=0.8, color="k")
for f, lab, c in [(ab7[0][0], f"ABAB pair {ab7[0][0]:.1f}", "tab:blue"), (ab7[1][0], f"/ {ab7[1][0]:.1f}", "tab:red"),
                  (FL7, f"F_L {FL7:.1f} (= ABCA {F_abca7:.1f}, m* {m_abca7:.2f} m_e)", "tab:green")]:
    ax.axvline(f, color=c, ls="--", lw=1, label=lab)
ax.set(xlim=(0, 35), xlabel="F (T)", ylabel="log FFT amp", title="run 7 FFT (1/B), B 0.71-10 T, bg_degree 5")
ax.legend(fontsize=8)
plt.show()
print(f"model: F_L = {FL7:.1f} T; ABAB near-CNP pair = {ab7[0][0]:.2f} / {ab7[1][0]:.2f} T (close+balanced regime); "
      f"ABCA singleton = {F_abca7:.2f} T at m* = {m_abca7:.2f} m_e (LK-dead at T_e ~ 8 K if real)")
