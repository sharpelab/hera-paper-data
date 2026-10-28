from hera.analysis import open_run, resolve_channels, current_channel, summarize_run
import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
for j, rid in enumerate((6, 7)):
    r = open_run(f"data/{rid}")
    print(summarize_run(r))
    cc = current_channel(resolve_channels(r.meta))
    I = r.col(cc.col) / cc.gain
    B = r.col("magnet_field")
    R = r.col("sr1_X") / I
    ix = np.argsort(B)
    ax[j].plot(B[ix], R[ix], lw=0.8)
    ax[j].set(ylabel="Rxx B1-B2 (Ω)", title=f"run {rid} raw, D≈0; {'electron' if rid == 6 else 'hole'} side")
    print(f"run {rid}: I median {np.median(I)*1e9:.2f} nA; R range {np.min(R):.0f} to {np.max(R):.0f} Ω; T {np.min(r.col('T_sample')):.3f}–{np.max(r.col('T_sample')):.3f} K; max |I_gate| {max(np.max(np.abs(r.col('k_2400_tg_curr'))),np.max(np.abs(r.col('k_2400_bg_curr'))))*1e12:.0f} pA")
ax[-1].set_xlabel("B (T)")
fig.tight_layout()
plt.show()
