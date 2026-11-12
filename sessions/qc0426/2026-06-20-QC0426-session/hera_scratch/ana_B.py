# Run 0 raw — re-form R_xx(V_tg, V_bg) per channel (raw first)
r0 = run(0)
print(summarize_run(r0))
fg0 = fan_grids(r0); rg0 = resistance_grids(fg0)
bg0 = fg0.slow                       # V_bg rows (37,)
tg0 = fg0.grid('DC_bias')[0]         # V_tg fast axis (105,)
Rxx = {ch: np.abs(rg0.R[ch]) for ch in ['sr1', 'sr2']}   # signed -> magnitude

fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
for a_, ch in zip(ax, ['sr1', 'sr2']):
    pc = a_.pcolormesh(tg0, bg0, np.clip(Rxx[ch], 0, 4400), shading='auto', cmap='inferno')
    a_.set_xlabel('V_tg / DC_bias (V)'); a_.set_ylabel('V_bg (V)')
    a_.set_title(f'Run 0  R_xx {ch}  [Ω, clip 4.4k]'); fig.colorbar(pc, ax=a_)
plt.tight_layout(); plt.show()
