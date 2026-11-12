# Aaron's verbatim analysis of data/1777 — 20260124_ana.ipynb cell 79
# Extracted 2026-06-05 for the HERA analysis-reproduction test (input: data/1777).

# Incorrectly labeled MC_25
files= [1777]

cmapplt = plt.get_cmap('inferno')


contact_pairs = {
    'curr': {'indices': [4], 'norm': colors.Normalize(vmin=0, vmax=1), 'cmap': 'viridis', 'label': r'$I/I_0$'},
    'long1': {'indices': [1, 2,3], 'norm': colors.SymLogNorm(linthresh=10, vmin=-3E4, vmax=3E4), 'cmap': 'RdBu_r', 'label': r'$R_{xx}$ ($\Omega$)'},
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
        fig, ax = plt.subplots(figsize=(10*1.618, 5))
        for file in files:
            # load in the new data
            data = sl.pload(file_path, file)
            mc_0 = data['measurement_config']
            md = sl.load_meta(file_path, file)
            xs = data['xs']
            phase = data[f'sr830_{ind}_P']

            # print(Ds)
    
            if pair=='curr':
                I = data['sr830_4_X']
                zs= I
            else:
                I = data['sr830_4_X']
                Vxx = data[f'sr830_{ind}_X']
                zs = Vxx/I
                
                mask = np.abs(I) < 0.0 * np.nanmax(np.abs(I))
                zs = np.ma.array(zs, mask=mask)
    
            plot = ax.semilogy(xs[:len(zs)], zs)

            # ax.set_ylim(0, 5E4)
    
            # ax.set_ylim(0, 2000)
    
            # ax1.plot(xs[:len(Rxx)], phase)
            plot2 = ax1.plot(xs[:len(zs)], phase)

        # plt.colorbar(plot, ax=ax, label=label)
        ax.set_title(mc_0[f'sr830_{ind}'])
        
        
        
        ax.set_ylabel(label)
        ax.set_xlabel(md['param'])
        ax1.set_ylabel('phase')
        ax1.set_xlabel(md['param'])
        # ax.set_ylim(0, 2E3)
        # ax.set_xlim(0.75, 1.25)






