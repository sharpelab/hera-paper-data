# Run 6 — raw first: MR at n = +3.2e12, D = 0 (electron), B 0 -> 10 T
from hera.analysis import sdh_onset, SdhOnsetError  # not in the preamble import

r6 = run(6)
print(summarize_run(r6))
B6 = r6.col("magnet_field")
IBIAS = 1.0 / 100e6          # sr1 drive 1.0 V over 100 MOhm = 10 nA
R6 = r6.col("sr1_X") / IBIAS  # sr1 gain 1 (unity, device card)
T6 = r6.col("T_sample")

fig, ax = plt.subplots(1, 2, figsize=(11, 3.6))
ax[0].plot(B6, R6, lw=0.6, color="#4053d3")
ax[0].set(xlabel="B (T)", ylabel=r"$R_{xx}$ ($\Omega$)", title="run 6 raw — n=+3.2e12, D=0")
ax[1].plot(B6, T6, lw=0.6, color="#4053d3")
ax[1].set(xlabel="B (T)", ylabel="T_sample (K)", title="T during run 6")
fig.tight_layout()
print(f"R: {np.nanmin(R6):.1f}..{np.nanmax(R6):.1f} Ohm on 5 kOhm FS (max {np.nanmax(R6)/5e3*100:.0f}% FS, no rail)")
print(f"T_sample {np.nanmin(T6):.3f}..{np.nanmax(T6):.3f} K; "
      f"leakage tg/bg medians {np.nanmedian(r6.col('k_2400_tg_curr'))*1e12:+.0f}/{np.nanmedian(r6.col('k_2400_bg_curr'))*1e12:+.0f} pA")
