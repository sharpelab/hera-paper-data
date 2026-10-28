# Aaron's verbatim analysis of data/145 — 20251103_ana.ipynb cell 17
# Extracted 2026-06-05 for the HERA analysis-reproduction test (input: data/145).

files = [145]

contact_pairs = {
    'long1': {'indices': [3, 5], 'norm': colors.SymLogNorm(linthresh=100, vmin=10, vmax=70), 'cmap': 'viridis', 'label': r'$R_{xx}$ ($\Omega$)'},
}



Rxx_vec = []
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
            # load in the new data
            data = sl.pload(file_path, file)
            mc_0 = data['measurement_config']
            xs = data['xs'][0] # top gate
            ys = data['ys'][0] # back gate
            
            phase = data[f'sr830_{ind}_P']

            I = data['sr830_4_X']
            Vxx = data[f'sr830_{ind}_X']
            Rxx = Vxx / I
            Rxx_vec.append(Rxx)

            Vbg = np.matlib.repmat(ys, len(xs), 1).T
            Vtg = np.matlib.repmat(xs, len(ys), 1)


            plot = ax.pcolormesh(xs, ys, Rxx, norm=norm)
            plt.colorbar(plot, ax=ax)
            ax.set_title(mc_0[f'sr830_{ind}'])
            ax.set_ylabel(r'$B$ (T)')
            ax.set_xlabel(r'$V_{bg}$ (V)')

            # ax.set_ylim(0, 2000)

            # ax1.plot(xs[:len(Rxx)], phase)
            plot = ax1.pcolormesh(xs, ys, phase, cmap='RdBu_r')
            plt.colorbar(plot, ax=ax1, label=r'Phase (deg)')
            ax1.set_ylabel(r'$B$ (T)')
            ax1.set_ylabel(r'$V_{bg}$ (V)')

            
            # ax.set_ylim(0, 0.1)
            

        plt.show()



