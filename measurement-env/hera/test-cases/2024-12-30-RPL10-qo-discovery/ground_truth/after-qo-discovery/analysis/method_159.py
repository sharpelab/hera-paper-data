# Aaron's verbatim analysis of data/159 — fans_ana.ipynb cell 8 (under '# D = 0.31 V/nm')
# Extracted 2026-06-05 for the HERA analysis-reproduction GT (input: data/159).
# Forms Rxx = sr830_{ind}_X / sr830_4_X (sr830_4 = current I_{7-20}); builds a
# Landau fan Rxx(n, B), an FFT of background-removed Rxx in 1/B (Landau-fan
# frequency f_nu), and a B=0 linecut. Ryx for the Hall indices [7,8].

file = 159

contact_pairs = {
    'long1': {'indices': [3],  'norm': colors.SymLogNorm(linthresh=100, vmin=0, vmax=1E3), 'cmap': 'viridis', 'label': r'$R_{xx}$ ($\Omega$)'},
}
contact_pairs = {
    'long1': {'indices': [1, 2, 3, 5, 6,],  'norm': colors.SymLogNorm(linthresh=100, vmin=0, vmax=1E2), 'cmap': 'viridis', 'label': r'$R_{xx}$ ($\Omega$)'},
    'hall1': {'indices': [7, 8], 'norm': None, 'cmap': 'RdBu_r', 'label': r'$R_{yx}$ ($h/e^{2}$)', 'vmin': -0.02, 'vmax': 0.02},
}

contact_pairs = {
    'long1': {'indices': [1, 2, 3, 5, 6,],  'norm': None, 'cmap': 'viridis', 'label': r'$R_{xx}$ ($\Omega$)', 'vmin': 0, 'vmax': 90},
    'hall1': {'indices': [7, 8], 'norm': None, 'cmap': 'RdBu_r', 'label': r'$R_{yx}$ ($h/e^{2}$)', 'vmin': -0.01, 'vmax': 0.01},
}

ylabel = r'$B$ (T)'
xlabel = r'$n$ ($10^{12}$ $cm^{-2}$)'

for pair, options in contact_pairs.items():
    indices = options['indices']
    norm = options.get('norm', None)
    cmap = options['cmap']
    label = options['label']
    vmin = options.get('vmin', None)
    vmax = options.get('vmax', None)

    for ind in indices:
        data = sl.pload(file_path, file)
        mc_0 = data['measurement_config']
        print(mc_0['sr830_4'])
        xs_tg = data['xs'][0]
        xs_bg = data['xs'][1]
        ys = data['ys'][0]
        b_cut_ind = 200

        I = data['sr830_4_X']
        Vxx = data[f'sr830_{ind}_X']
        Rxx = Vxx / I
        n = (xs_bg/dbg + xs_tg/dtg)*ep*5.52634936 # in units of cm^-2 assuming BN dielectric = 3
        D = 0.5*ep*(xs_tg/dtg - xs_bg/dbg)

        # limit the examined B field to everything between 1 and 0.02 T, found specific index by hand
        cB = ys[:b_cut_ind]
        cRxx = Rxx[:b_cut_ind]
        cleaned_Rxx = remove_fifth_deg_poly(cB, cRxx) # remove background
        interp_invB, interp_Rxx = interp_rxx(cB, cleaned_Rxx, nx=200) # invert B and interpolate for even spacing of points
        fft, freq_b = make_mat_fft(interp_invB, interp_Rxx, n, padding=5) # make fft

        # plotting original data
        fig, axs = plt.subplots(3, 1, figsize=(8*1.618, 10), sharex=True, layout='constrained')
        ax = axs[0]
        plot = ax.pcolormesh(n, cB, cRxx/Rq if 'yx' in label else cRxx, norm=norm, cmap=cmap, vmin=vmin, vmax=vmax)
        plt.colorbar(plot, ax=ax, label=label, pad=0.01)
        ax.set_title(mc_0[f'sr830_{ind}'])
        ax.set_ylabel(ylabel)

        # plotting normalized FFT
        ax = axs[1]
        plot = ax.pcolormesh(n, freq_b, fft, cmap=cmap, vmin=0, vmax=0.8)
        cb = plt.colorbar(plot, ax=ax, label=r'FFT of $R_{xx}$ (a.u.)', pad = 0.01)
        cb.set_ticks([])
        ax.axvline(-2.51, color='k', linestyle='dashed', alpha=0.6)
        ax.axvline(-2.675, color='k', linestyle='dashed', alpha=0.6)
        ax.axvline(-2.72, color='k', linestyle='dashed', alpha=0.6)
        ax.axvline(-2.2, color='k', linestyle='dashed', alpha=0.6)
        ax.set_ylabel(r'$f_{\nu}$')
        ax.set_ylim([0, 0.6])

        # plotting linecut at B=0
        ax = axs[2]
        ax.plot(n, Rxx[-1, :], 'k')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(r'$R_{xx}$ ($\Omega$)')
        ax.axvline(-2.51, color='k', linestyle='dashed', alpha=0.6)
        ax.axvline(-2.675, color='k', linestyle='dashed', alpha=0.6)
        ax.axvline(-2.72, color='k', linestyle='dashed', alpha=0.6)
        ax.axvline(-2.2, color='k', linestyle='dashed', alpha=0.6)
        ax.annotate(r'$B$ = 0', xy=(-2.9, 40), textcoords='axes fraction', xytext=(0.025, 0.85), fontsize=14)
        # plt.tight_layout()
        plt.show()

