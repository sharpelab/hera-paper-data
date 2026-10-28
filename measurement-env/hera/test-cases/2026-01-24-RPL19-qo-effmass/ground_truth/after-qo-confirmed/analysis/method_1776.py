# Aaron's verbatim analysis of data/1776 — 20260124_ana.ipynb cell 78
# Extracted 2026-06-05 for the HERA analysis-reproduction test (input: data/1776).

# Incorrectly labeled MC_25
files= [1776]

cmapplt = plt.get_cmap('inferno')


contact_pairs = {
    'curr': {'indices': [], 'norm': colors.Normalize(vmin=0, vmax=1), 'cmap': 'viridis', 'label': r'$I/I_0$'},
    'long1': {'indices': [1, 2,3], 'norm': colors.SymLogNorm(linthresh=100, vmin=0, vmax=1E4), 'cmap': 'viridis', 'label': r'$R_{xx}$ ($\Omega$)'},
    'fakehall': {'indices': [], 'norm': colors.SymLogNorm(linthresh=3E4, vmin=-5E3, vmax=5E3), 'cmap': 'RdBu_r', 'label': r'$R_{yx}$ ($\Omega$)'},
    'realhall': {'indices': [5, 6], 'norm': colors.SymLogNorm(linthresh=3E4, vmin=-1E5, vmax=1E5), 'cmap': 'RdBu_r', 'label': r'$R_{yx}$ ($\Omega$)'},
    'nl': {'indices': [], 'norm': colors.SymLogNorm(linthresh=3E4, vmin=-1E5, vmax=1E5), 'cmap': 'RdBu_r', 'label': r'$R_{yx}$ ($\Omega$)'},
}


gates = True
for pair, options in contact_pairs.items():
    indices = options['indices']
    norm = options.get('norm', None)
    cmap = options['cmap']
    label = options['label']
    vmin = options.get('vmin', None)
    vmax = options.get('vmax', None)
    for ind in indices:
        fig, ax = plt.subplots(figsize=(5*1.618, 5))
        for file in files:
            # load in the new data
            data = sl.pload(file_path, file)
            mc_0 = data['measurement_config']
            md = sl.load_meta(file_path, file)
            vtg = data['xs'][0]
            vbg = data['xs'][1]
            xs, _ = calculate_n_D(vtg, vbg, dtg=17.25, dbg=25.5)
            ys = data['ys'][0]
            phase = data[f'sr830_{ind}_P']

            # print(Ds)
    
            if pair=='curr':
                I = data['sr830_4_X']
                zs= I/np.nanmax(I)
            else:
                I = data['sr830_4_X']
                Vxx = data[f'sr830_{ind}_X']
                zs = Vxx/I
                
                mask = np.abs(I) < 0.0 * np.nanmax(np.abs(I))
                zs = np.ma.array(zs, mask=mask)
    
            plot = ax.pcolormesh(xs, ys, zs, norm=norm, cmap=cmap, rasterized=True, lw=0)
        plt.colorbar(plot, ax=ax, label=label)
        ax.set_title(f'AH contrib {mc_0[f'sr830_{ind}']} symmetric')
        ax.set_ylabel(r'$D/\epsilon_0$ (V/nm)')
        ax.set_xlabel(r'$n$ ($10^{12}$ $\mathrm{cm^{-2}}$)')
        # plt.colorbar(plot, ax=ax, label=label)
        ax.set_title(mc_0[f'sr830_{ind}'])
        
        
        
        ax.set_ylabel(md['slow_param'])
        ax.set_xlabel('n')
        # ax.set_ylim(1.3, 1.5)

        # ax.set_ylim(0, 2E3)






