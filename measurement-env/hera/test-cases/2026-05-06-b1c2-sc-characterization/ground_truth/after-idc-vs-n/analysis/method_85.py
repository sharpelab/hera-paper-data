# Isaac's VERBATIM analysis of data/85 (the `# B vs Idc` next move) —
# 20260415_ana.ipynb cells for `data_id = 85` (cropped ana cells 34 + 35).
# Extracted 2026-06-05 for the HERA analysis-reproduction test (input: data/85).
# POST-CUT: answer-key only, never served to the agent.

# --- cell: load + form quantities (current = sr830_1; Rxx2 = four-probe) ---
data_id = 85
dat = sl.pload(folder_path, data_id)

ys = dat['ys']*1e3
xs = dat['xs']*10

Ixx = dat['sr830_1_X'] / dat['measurement_config']['sr1_gain']
Rxx2 = (dat['sr830_4_X'] / 1e2) / Ixx
Rxx = (dat['sr830_2_X'] / 1e2) / Ixx
Rxy = (dat['sr830_3_X'] / 1e2) / Ixx

# --- cell: plot Rxx2(Idc, B) and Rxy(Idc, B) ---
fig, axs = plt.subplots(1, 2, figsize=(16, 10), squeeze=False)
axpos = [[0, 0], [0, 1]]
for i in [0]:
    ax = axs[axpos[i][0], axpos[i][1]]
    pcm= ax.pcolormesh(xs, ys, Rxx2, shading='auto', norm=SymLogNorm(linthresh=100, vmin = 0, vmax = 1e3), cmap="RdBu_r")#
    ax.set_ylabel('B (mT)')
    ax.set_xlabel('Idc (nA)')
    ax.set_title(f'Rxx Channel')
    cbar = fig.colorbar(pcm, ax=ax, label=r"R ($\Omega$)", orientation="horizontal", fraction=0.02, pad=0.1)
    cbar.set_ticks([0, 1e3])

for i in [1]:
    chan=[1,3]
    ax = axs[axpos[i][0], axpos[i][1]]
    pcm= ax.pcolormesh(xs, ys, Rxy, shading='auto',vmin=-1000, vmax = 1000, cmap='RdBu')
    ax.set_ylabel('B (mT)')
    ax.set_xlabel('Idc (nA)')
    ax.set_title(f'Rxy Channel')
    cbar = fig.colorbar(pcm, ax=ax, label=r"R ($\Omega$)", orientation="horizontal", fraction=0.02, pad=0.1)
    cbar.set_ticks([-1e3, 1e3])

plt.tight_layout()
plt.show()
