# Aaron's verbatim analysis of data/1945 — 20260217_ana.ipynb cell 141 (the "Fine nD map" cell, the NEXT move).
# Extracted 2026-06-05 for the HERA analysis-reproduction test. POST-CUT — answer-key only.
# NOTE (2026-06-08): despite the "Fine" label, the MOVE here is a COVERAGE extension — the polygon
# extends D down to -0.4 V/nm to map the full reachable range (the rough map stopped at +0.70). The
# grid is also denser (nx, ny = 201, 251, oversample flag 1, rev_y=False), but that is incidental.
# Same Rxx = Vxx/I pipeline as method_1944.

files= [1945]
ns = np.array([0.2, 0.72, 1.8, 1.8, 0.2])
Ds = np.array([1.018, 1.065, 0.949, -0.4, -0.4])

nx, ny = 201, 251

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
    'long bot': {'indices': [1, 2, 3,], 'norm': colors.SymLogNorm(linthresh=100, vmin=0, vmax=1E4), 'cmap': 'viridis', 'label': r'$R_{xx}$ ($\Omega$)'},
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

        #ax.set_ylim(0.7,1.05)
        #ax.set_xlim(0.2, 1)
        plt.show()
