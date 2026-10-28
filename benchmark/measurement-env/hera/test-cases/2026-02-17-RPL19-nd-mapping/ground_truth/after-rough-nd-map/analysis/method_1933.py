# Aaron's verbatim analysis of data/1933 — 20260217_ana.ipynb cell 136 (section "## nD map zoom in on AHC").
# Extracted 2026-06-05 as the prior-section context for the HERA analysis-reproduction test. PRE-power-loss.
# Same Rxx = Vxx/I pipeline; a NEGATIVE-D (n, D) zoom on this device's AHC corner (n in [0.2,0.8], D in [-0.4,-0.8]).

files= [1933]

ns = np.array([0.2, 0.8, 0.8, 0.2])
Ds = np.array([-0.4, -0.4, -0.68, -0.80])


nx, ny = 101, 101

verts = []
for n, D in zip(ns, Ds):
    verts.append([n, D])
verts = np.array(verts)


Vtgs, Vbgs = calculate_gate_voltages(ns, Ds, dtg=17.25, dbg=25.5)

verts_gates = []
for Vtg, Vbg in zip(Vtgs, Vbgs):
    verts_gates.append([Vtg, Vbg])
verts_gates = np.array(verts_gates)


contact_pairs = {
    'curr': {'indices': [4], 'norm': colors.Normalize(vmin=0, vmax=1), 'cmap': 'viridis', 'label': r'$I/I_0$'},
    'long bot': {'indices': [1, 2, 3,], 'norm': colors.SymLogNorm(linthresh=100, vmin=0, vmax=1E5), 'cmap': 'viridis', 'label': r'$R_{xx}$ ($\Omega$)'},
    'long top': {'indices': [5, 6, ], 'norm': colors.SymLogNorm(linthresh=100, vmin=0, vmax=1E4), 'cmap': 'viridis', 'label': r'$R_{xx}$ ($\Omega$)'},
    'fakehall': {'indices': [], 'norm': colors.Normalize(vmin=-1000, vmax=1000), 'cmap': 'RdBu_r', 'label': r'$R_{yx}$ ($\Omega$)'},
    'realhall': {'indices': [7, 8], 'norm': colors.SymLogNorm(linthresh=3E4, vmin=-1E5, vmax=1E5), 'cmap': 'RdBu_r', 'label': r'$R_{yx}$ ($\Omega$)'},
    'nl hall': {'indices': [9], 'norm': colors.SymLogNorm(linthresh=3E4, vmin=-1E5, vmax=1E5), 'cmap': 'RdBu_r', 'label': r'$R_{yx}$ ($\Omega$)'},
}

for pair, options in contact_pairs.items():
    indices = options['indices']
    norm = options.get('norm', None)
    cmap = options['cmap']
    label = options['label']
    vmin = options.get('vmin', None)
    vmax = options.get('vmax', None)
    for ind in indices:
        for file in files:
            data = sl.pload(file_path, file)
            mc_0 = data['measurement_config']
            xs = data['xs'][0] # top gate
            ys = data['xs'][1] # back gate
    
    
            I = data['sr830_4_X']
            I = np.pad(I, (0, len(xs) - len(I)), 'constant', constant_values=(np.nan, np.nan))
            Vxx = data[f'sr830_{ind}_X']
            Vxx = np.pad(Vxx, (0, len(xs.ravel()) - len(Vxx)), 'constant', constant_values=(np.nan, np.nan))
            zs = Vxx / I
            phase = data[f'sr830_{ind}_P']
            phase = np.pad(phase, (0, len(xs.ravel()) - len(phase)), 'constant', constant_values=(np.nan, np.nan))
            
            xs, ys = calculate_n_D(xs, ys, dtg=17.25, dbg=25.5)
            xs, ys, I = raster.pcolorize_data(I, verts, nx, ny, 0, rev_x=False, rev_y=True)
            xs, ys, zs = raster.pcolorize_data(zs, verts, nx, ny, 0, rev_x=False, rev_y=True)
            xs, ys, phase = raster.pcolorize_data(phase, verts, nx, ny, 0, rev_x=False, rev_y=True)

        
        fig, [ax, ax1] = plt.subplots(1, 2, figsize=(10*1.618, 5))

        if pair == "curr":
            # normalize current while plotting 
            I0 = 1e-9 # enter expected current here
            plot = ax.pcolormesh(xs, ys, I/I0, norm=norm, cmap=cmap, rasterized=True, lw=0)
        else:
            plot = ax.pcolormesh(xs, ys, zs, norm=norm, cmap=cmap, rasterized=True, lw=0)
        plt.colorbar(plot, ax=ax, label=label)
        # ax.set_title(f'AH contrib {mc_0[f'sr830_{ind}']} symmetric')
        ax.set_ylabel(r'$D/\epsilon_0$ (V/nm)')
        ax.set_xlabel(r'$n$ ($10^{12}$ $\mathrm{cm^{-2}}$)')
        ax.set_title(mc_0[f'sr830_{ind}'] + " " +  str(pair))

        plot = ax1.pcolormesh(xs, ys, phase, cmap='RdBu_r', rasterized=True, lw=0)
        plt.colorbar(plot, ax=ax1, label=label)

        # plt.savefig(os.path.join('figures', f'rmg19_mc22_gatemap_{ind}.pdf'), dpi=300, bbox_inches='tight')

        #for a in [ax, ax1]:
        #     a.set_xlim(0.2,0.8)
        #     a.set_ylim(-0.8,-0.4)
        plt.show()
