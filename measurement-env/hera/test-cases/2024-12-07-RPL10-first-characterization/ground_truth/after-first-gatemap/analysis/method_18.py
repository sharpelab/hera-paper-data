files = [18]
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
        fig, [ax, ax1] = plt.subplots(1, 2, figsize=(10*1.618, 5))
        for file in files:
            data = sl.pload(file_path, file)
            mc_0 = data['measurement_config']
            print(mc_0['sr830_4'])
            xs = data['xs']
            ys = data['ys']
            phase = data[f'sr830_{ind}_P']

            Vbg = np.matlib.repmat(ys, len(xs), 1).T
            Vtg = np.matlib.repmat(xs, len(ys), 1)

            dbg = 40
            dtg = 26

            n = (Vbg/dbg + Vtg/dtg)*ep*5.52634936 # in units of cm^-2 assuming BN dielectric = 3
            D = 0.5*ep*(Vtg/dtg - Vbg/dbg)
            nu = 4*n/3
            # xs = n
            # ys = D
            I = data['sr830_4_X']
            Vxx = data[f'sr830_{ind}_X']
            Rxx = Vxx / I

            
            plot = ax.pcolormesh(xs, ys, Rxx/Rq if 'yx' in label else Rxx, norm=norm, cmap=cmap, vmin=vmin, vmax=vmax)
            plt.colorbar(plot, ax=ax, label=label)

            plot1 = ax1.pcolormesh(xs, ys, phase, cmap='RdBu_r')
            plt.colorbar(plot1, ax=ax1, label='Phase')

        ax.set_title(mc_0[f'sr830_{ind}'])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_ylim(-9, -6)
        ax.plot(0.825, -8.5, '.r')
        # ax.axhline(-8.5)
        # ax.axvline(0.825)
        # ax.set_xlim(2.5, 4.1)

        ax1.set_title(mc_0[f'sr830_{ind}'])
        # ax1.set_xlabel(r'n ($10^{12}$ $cm^{-2}$)')
        # ax1.set_ylabel(r'D (V/nm)')
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(ylabel)
        ax1.set_ylim(-9, -6)
        # ax1.set_xlim(-4, 0)
        # ax1.set_ylim(0.2, 0.4)
        plt.show()


fig, ax = plt.subplots(figsize=(5*1.618, 5))
plot = ax.pcolormesh(xs, ys, I*(1E9), norm=colors.SymLogNorm(linthresh=100, vmin=0.9, vmax=1.1), cmap=cmap)
plt.colorbar(plot, ax=ax, label='I (nA)')
ax.set_title(mc_0[f'sr830_{ind}'])
ax.set_xlabel(xlabel)
ax.set_ylabel(ylabel)
# ax.set_ylim(-9, -6)