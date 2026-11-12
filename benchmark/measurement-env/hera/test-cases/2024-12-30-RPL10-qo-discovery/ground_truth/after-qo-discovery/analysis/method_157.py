# Aaron's verbatim analysis of data/157 — fans_ana.ipynb cell 9.
# Extracted 2026-06-05. data/157 is the single-density (n = -2.6) 'resolution
# check': Rxx vs B (0 -> 1 T) at fixed gate, decimated 1x/2x/3x, confirming SdH
# oscillations are resolvable before the full fan (159). Forms Rxx = Vxx/I with
# I = sr830_4_X. This is the immediate in-section predecessor of 159.

file = 157
contact_pairs = {
    'long1': {'indices': [1, 2, 3, 5, 6,], 'norm': colors.SymLogNorm(linthresh=100, vmin=0, vmax=1E4), 'cmap': 'viridis', 'label': r'$R_{xx}$ ($\Omega$)'},
    'hall1': {'indices': [7, 8], 'norm': None, 'cmap': 'RdBu_r', 'label': r'$R_{yx}$ ($h/e^{2}$)', 'vmin': -0.05, 'vmax': 0.05},
}
contact_pairs = {
    'long1': {'indices': [1,], 'norm': colors.SymLogNorm(linthresh=100, vmin=0, vmax=1E4), 'cmap': 'viridis', 'label': r'$R_{xx}$ ($\Omega$)'},
}

xlabel = r'$B$ (T)'
ns = [1, 2, 3,]

for pair, options in contact_pairs.items():
    indices = options['indices']
    norm = options.get('norm', None)
    cmap = options['cmap']
    label = options['label']
    vmin = options.get('vmin', None)
    vmax = options.get('vmax', None)

    for ind in indices:
        fig, axs = plt.subplots(len(ns), 1, figsize=(5*1.618, 5*(len(ns))))
        for i, ni in enumerate(ns):
            ax = axs[i]
            data = sl.pload(file_path, file)
            mc_0 = data['measurement_config']
            # print(mc_0['sr830_4'])
            xs = data['xs']
            I = data['sr830_4_X']
            Vxx = data[f'sr830_{ind}_X']
            Rxx = Vxx / I
            B = xs[:len(Rxx)]
    
            B_crop = B[::ni]
            Rxx_crop = Rxx[::ni]
    
            plot = ax.plot(B_crop, Rxx_crop/Rq if 'yx' in label else Rxx_crop, linewidth=1)
            ax.set_title(mc_0[f'sr830_{ind}'])
    
            # idx = np.isfinite(Rxx_crop) & np.isfinite(B_crop)
            # coeff = np.polyfit(B_crop, Rxx_crop[idx], 5)
            # fit = np.polyval(coeff, B_crop)
            # cleaned_Rxx = fit - Rxx_crop
            # ax.plot(B_crop, cleaned_Rxx, linewidth=1)
            # ax[1].set_title(mc_0[f'sr830_{ind}'] + ', background removed')

        for a in axs:
            a.set_xlabel(xlabel)
            a.set_ylabel(r'')
            # a.set_xlim(0, 0.5)

        plt.tight_layout()
        
