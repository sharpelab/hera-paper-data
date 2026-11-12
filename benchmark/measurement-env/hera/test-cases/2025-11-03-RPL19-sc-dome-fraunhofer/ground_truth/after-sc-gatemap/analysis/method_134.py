# Aaron's verbatim analysis of data/134 — 20251103_ana.ipynb cell 12
# Extracted 2026-06-05 for the HERA analysis-reproduction test (input: data/134).

def draw_line_through_point(point=(-5.2, 0.47), slope=0.3, extent=0.2, npoints=100):
    x0, y0 = point
    x = np.linspace(x0 - extent, x0 + extent, npoints)
    y = y0 + slope * (x - x0)
    return x, y


files = [134]

contact_pairs = {
    'long1': {'indices': [3, 5], 'norm': colors.SymLogNorm(linthresh=100, vmin=0, vmax=100), 'cmap': 'viridis', 'label': r'$R_{xx}$ ($\Omega$)'},
}

# points to take frauns at BG, TG
pts = [(-5.5,0.57), (-5.27,0.45), (-5.0,0.4), (-4.75,0.33), (-4.5,0.25), (-4.25,0.18), (-4.0,0.12)] 

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
            xs = data['xs'] # top gate
            ys = data['ys'] # back gate
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
            ax.set_ylabel(r'$V_{tg}$ (V)')
            ax.set_xlabel(r'$V_{bg}$ (V)')

            # ax.set_ylim(0, 2000)

            # ax1.plot(xs[:len(Rxx)], phase)
            plot = ax1.pcolormesh(xs, ys, phase, cmap='RdBu_r')
            plt.colorbar(plot, ax=ax1, label=r'Phase (deg)')
            ax1.set_xlabel(r'$V_{tg}$ (V)')
            ax1.set_ylabel(r'$V_{bg}$ (V)')

            ax.plot(-5.2, 0.47, '.r')
            #ax.set_ylim(0.1,0.6)
            #ax.set_xlim(-5.5,-4.0)
            x, y = draw_line_through_point()
            ax.plot(x, y, 'r')

            for pt in pts:
                ax.scatter(pt[0], pt[1], s=20, color='cyan')

        plt.show()



