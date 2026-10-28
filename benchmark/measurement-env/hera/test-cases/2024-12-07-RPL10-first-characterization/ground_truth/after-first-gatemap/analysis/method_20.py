files = np.arange(395, 399, 1)

files = [20]
contact_pairs = {
    'long1': {'indices': [1, 2, 3, 5, 6, 8], 'norm': colors.SymLogNorm(linthresh=100, vmin=0, vmax=1E4), 'cmap': 'viridis', 'label': r'$R_{xx}$ ($\Omega$)'},
    'long2': {'indices': [7], 'norm': colors.SymLogNorm(linthresh=100, vmin=5E3, vmax=5E4), 'cmap': 'viridis', 'label': r'$R_{xx}$ ($\Omega$)'},
}

xlabel = r'$V_{tg}$ (V)'
ylabel = r'$V_{bg}$ (V)'

for pair, options in contact_pairs.items():
    indices = options['indices']
    norm = options.get('norm', None)
    cmap = options['cmap']
    label = options['label']
    vmin = options.get('vmin', None)
    vmax = options.get('vmax', None)

    for ind in indices:
        fig, ax = plt.subplots(1, 1, figsize=(5*1.618, 5))
        for file in files:
            data = sl.pload(file_path, file)
            mc_0 = data['measurement_config']
            print(mc_0['sr830_4'])
            xs = data['xs'] * 10
            I = data['sr830_4_X']
            Vxx = data[f'sr830_{ind}_X']
            Rxx = Vxx / I
            phase = data[f'sr830_{ind}_P']
            T = np.nanmean(data['T'])
            ax.axvline(20)
            print(T)
            
            plot = ax.plot(xs[:len(Rxx)], Rxx)
            ax.set_title(mc_0[f'sr830_{ind}'])
            ax.set_xlabel(r'$I_{DC}$ (nA)')
            ax.set_ylabel(label)

