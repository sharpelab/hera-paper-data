# Re-render of Aaron's Rxx = Vxx/I pipeline applied to data/1946 — the D-first
# rough re-map (NEXT move after the broaden map). POST-CUT — answer-key only.
#
# NOTE: unlike method_1944/1945 (which are Aaron's verbatim ana cells), Aaron did
# not re-analyze 1946 in a dedicated ana cell — he re-SWEPT D-first rather than
# re-plotting. This script is the faithful application of his same pipeline
# (current = sr830_4, Rxx = sr830_{1,2,3}_X / sr830_4_X, (n,D) axes, pcolorize)
# to data/1946 so the de-streaking can be seen side-by-side with data/1945.
# Generated 2026-06-08 for the after-broaden-map frontier.

files = [1946]
# D-first rough re-map: same landscape, D as the fast axis, coarse 101x101,
# positive-D extent (the quick check that D-first reduces streaks).
ns = np.array([0.2, 0.72, 1.8, 1.8, 0.2])
Ds = np.array([1.018, 1.065, 0.949, 0.4, 0.4])
nx, ny = 101, 101

verts = []
for n, D in zip(ns, Ds):
    verts.append([n, D])
verts = np.array(verts)

contact_pairs = {
    'long bot': {'indices': [1, 2, 3], 'norm': colors.SymLogNorm(linthresh=100, vmin=0, vmax=1E4), 'cmap': 'viridis', 'label': r'$R_{xx}$ ($\Omega$)'},
}

for pair, options in contact_pairs.items():
    for ind in options['indices']:
        for file in files:
            data = sl.pload(file_path, file)
            mc_0 = data['measurement_config']
            xs = data['xs'][0]  # top gate
            ys = data['xs'][1]  # back gate
            I = data['sr830_4_X']
            I = np.pad(I, (0, len(xs) - len(I)), 'constant', constant_values=(np.nan, np.nan))
            Vxx = data[f'sr830_{ind}_X']
            Vxx = np.pad(Vxx, (0, len(xs.ravel()) - len(Vxx)), 'constant', constant_values=(np.nan, np.nan))
            zs = Vxx / I
            xs, ys = calculate_n_D(xs, ys, dtg=17.25, dbg=25.5)
            # D-first raster: rev_y=False (forward). The forward/reverse pair is data/1946 vs data/1947.
            xs, ys, zs = raster.pcolorize_data(zs, verts, nx, ny, 0, rev_x=False, rev_y=False)

        fig, ax = plt.subplots(figsize=(5 * 1.618, 5))
        plot = ax.pcolormesh(xs, ys, zs, norm=options['norm'], cmap=options['cmap'], rasterized=True, lw=0)
        plt.colorbar(plot, ax=ax, label=options['label'])
        ax.set_ylabel(r'$D/\epsilon_0$ (V/nm)')
        ax.set_xlabel(r'$n$ ($10^{12}$ $\mathrm{cm^{-2}}$)')
        ax.set_title(mc_0[f'sr830_{ind}'] + " " + str(pair) + " (D-first)")
        plt.show()
