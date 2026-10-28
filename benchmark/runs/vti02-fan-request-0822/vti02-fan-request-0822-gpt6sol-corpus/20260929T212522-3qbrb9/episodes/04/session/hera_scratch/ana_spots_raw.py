# Runs 6 and 7: raw, gain-divided four-terminal traces before FFT interpretation.
import numpy as np
import matplotlib.pyplot as plt

fig, axs = plt.subplots(2, 2, figsize=(12, 7), sharex='col')
for row, (fid, n) in enumerate(((6, +3.2), (7, -1.2))):
    q = run(fid)
    print(summarize_run(q))
    B = q.col('magnet_field')
    I = q.col('sr0_X') / -1e6
    R = q.col('sr1_X') / I
    axs[row, 0].plot(B, R, lw=0.7)
    axs[row, 0].set(ylabel='signed Rxx (ohm)', title=f'run {fid}: n={n:+.1f}e12, D=0')
    axs[row, 1].plot(B, I * 1e9, lw=0.7, label='drain I (nA)')
    axs[row, 1].plot(B, q.col('T_sample'), lw=0.7, label='sample T (K)')
    axs[row, 1].legend(fontsize=8)
    axs[row, 1].set_title('raw current and temperature')
    print(f'run {fid}: R range {np.nanmin(R):.1f}..{np.nanmax(R):.1f} ohm, '
          f'I median {np.nanmedian(I)*1e9:.2f} nA, T {q.col("T_sample").min():.3f}..{q.col("T_sample").max():.3f} K; '
          f'|I_gate|max TG/BG {np.max(abs(q.col("k_2400_tg_curr")))*1e12:.0f}/'
          f'{np.max(abs(q.col("k_2400_bg_curr")))*1e12:.0f} pA')
for ax in axs[-1]: ax.set_xlabel('B (T)')
fig.tight_layout(); plt.show()
