# Aaron's verbatim analysis of data/1944 — 20260217_ana.ipynb cell 140 (section "# After power loss").
# Extracted 2026-06-05 for the HERA analysis-reproduction test (input: data/1944, the rough nD map).
# Loads via sl.pload, forms Rxx = sr830_{1,2,3}_X / sr830_4_X (sr830_4 = current),
# converts the gate axes to (n, D) via calculate_n_D(dtg=17.25, dbg=25.5), rasterizes the
# polygon onto a 101x101 grid (pcolorize_data, oversample 0, rev_y=True), and pcolormeshes Rxx(n, D).

files= [1944]

ns = np.array([0.2, 0.72, 2., 2.0, 0.2])
Ds = np.array([1.018, 1.065, 0.949, 0.70, 0.70])


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
    'long bot': {'indices': [1, 2, 3,], 'norm': colors.SymLogNorm(linthresh=100, vmin=0, vmax=1E5), 'cmap': 'viridis', 'label': r'$R_{xx}$ ($\Omega$)'},
    'long top': {'indices': [], 'norm': colors.SymLogNorm(linthresh=1e3, vmin=1e2, vmax=1E5), 'cmap': 'viridis', 'label': r'$R_{xx}$ ($\Omega$)'},
    'realhall': {'indices': [], 'norm': colors.SymLogNorm(linthresh=3E4, vmin=-1E5, vmax=1E5), 'cmap': 'RdBu_r', 'label': r'$R_{yx}$ ($\Omega$)'},
    'nl hall': {'indices': [], 'norm': colors.SymLogNorm(linthresh=3E4, vmin=-1E5, vmax=1E5), 'cmap': 'RdBu_r', 'label': r'$R_{yx}$ ($\Omega$)'},
}

for pair, options in contact_pairs.items():
    indices = options['indices']
    norm = options.get('norm', None)
    cmap = options['cmap']
    label = options['label']
    vmin = options.get('vmin', None)
    vmax = options.get('vmax', None)
    for ind in indices:
        z_arr = []
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
            z_arr.append(zs)
        
        fig, ax = plt.subplots(figsize=(5*1.618, 5))

        plot = ax.pcolormesh(xs, ys, zs, norm=norm, cmap=cmap, rasterized=True, lw=0)
        plt.colorbar(plot, ax=ax, label="R")
        # ax.set_title(f'AH contrib {mc_0[f'sr830_{ind}']} symmetric')
        ax.set_ylabel(r'$D/\epsilon_0$ (V/nm)')
        ax.set_xlabel(r'$n$ ($10^{12}$ $\mathrm{cm^{-2}}$)')
        ax.set_title(mc_0[f'sr830_{ind}'] + " " +  str(pair))


        plt.show()
