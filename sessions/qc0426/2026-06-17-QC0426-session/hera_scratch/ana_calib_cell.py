# 0 T gate map (run 2) -> CNP line + (n,D) calibration.
# RAW first: per-channel Rxx(V_tg,V_bg) maps; then the CNP-ridge fit and the
# capacitance calibration that every downstream (n,D) claim inherits.
from scipy.ndimage import gaussian_filter1d

m = load_meta(2); cols = m['columns']
raw = np.loadtxt(os.path.join(file_path, '2', 'data.tsv.gz'))
ci = {c: i for i, c in enumerate(cols)}
Ib = m['measurement_config']['bias_voltage'] / m['measurement_config']['bias_resistor']
BGv = np.unique(raw[:, ci['k_bg_volt']]); TGv = np.unique(raw[:, ci['DC_bias']])
nBG, nTG = len(BGv), len(TGv)
R = {nm: (raw[:, ci[c]] / Ib).reshape(nBG, nTG)
     for nm, c in [('sr1', 'sr1_X'), ('sr2', 'sr2_X'), ('sr3', 'sr3_X')]}

def ridge(Rg):
    tg = np.full(nBG, np.nan); rm = np.full(nBG, np.nan); edge = np.zeros(nBG, bool)
    for i in range(nBG):
        j = int(np.nanargmax(gaussian_filter1d(Rg[i], 1.5)))
        tg[i], rm[i], edge[i] = TGv[j], Rg[i][j], (j <= 1 or j >= nTG - 2)
    return tg, rm, edge

# --- RAW maps + ridge overlay ---
ext = [TGv.min(), TGv.max(), BGv.min(), BGv.max()]
fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))
for a, nm, ttl in [(ax[0], 'sr1', 'sr1 Rxx T3-T4'), (ax[1], 'sr2', 'sr2 Rxx B4-B5'), (ax[2], 'sr3', 'sr3 Rxy T5-B6')]:
    im = a.imshow(R[nm] / 1e3, origin='lower', aspect='auto', extent=ext, cmap='viridis',
                  vmin=0, vmax=np.nanpercentile(R[nm] / 1e3, 99))
    a.set_xlabel('$V_{TG}$ (V)'); a.set_ylabel('$V_{BG}$ (V)'); a.set_title(ttl)
    plt.colorbar(im, ax=a, label='k$\\Omega$')
tg1, _, e1 = ridge(R['sr1'])
ax[0].plot(tg1[~e1], BGv[~e1], 'r.', ms=4); ax[0].plot(tg1[e1], BGv[e1], 'rx', ms=6)
plt.show()

# --- per-channel CNP fits ---
fits = {}
for nm in ('sr1', 'sr2'):
    tg, rm, edge = ridge(R[nm]); g = ~edge & np.isfinite(tg)
    s, b = np.polyfit(BGv[g], tg[g], 1)
    fits[nm] = dict(slope=s, intc=b, rmin=np.nanmin(rm[g]), rmax=np.nanmax(rm[g]),
                    resid=(tg[g] - np.polyval([s, b], BGv[g])).std(), tg=tg, rm=rm, edge=edge)
    print(f'{nm}: V_tg = {s:+.4f} V_bg {b:+.4f}  | ratio c_bg/c_tg={-s:.4f} | '
          f'resid {fits[nm]["resid"]:.3f} V | CNP R {rm[g].min()/1e3:.1f}k..{rm[g].max()/1e3:.1f}k')

# --- device calibration (ratio confirmed = geometry; anchor c_bg at geometry) ---
# c_tg, c_bg already defined in the (n,D) setup cell from geometry (t_tg, t_bg).
ratio_geom = c_bg / c_tg
b_dev = 0.5 * (fits['sr1']['intc'] + fits['sr2']['intc'])
n_offset = -(c_tg * b_dev) / cst_e          # n=0 along CNP line
D_offset = 0.0                               # stated assumption: gates define D=0
print(f'\nADOPTED: c_tg={c_tg:.4e} c_bg={c_bg:.4e} F/m^2 (ratio {ratio_geom:.4f}); '
      f'n_offset={n_offset/1e4:.3e} cm^-2; D_offset=0')

def nD(Vtg, Vbg): return calc_nD(Vtg, Vbg, c_tg, c_bg, n_offset, D_offset)

# closure + CNP-R vs D
g = ~fits['sr1']['edge'] & np.isfinite(fits['sr1']['tg'])
nr, Dr = nD(fits['sr1']['tg'][g], BGv[g])
print(f'closure: max|n| on ridge {np.abs(nr).max()/1e4:.2e} cm^-2; D span {Dr.min()/1e9:+.2f}..{Dr.max()/1e9:+.2f} V/nm')
fig2, a2 = plt.subplots(figsize=(6, 4))
a2.plot(Dr / 1e9, fits['sr1']['rm'][g] / 1e3, 'o-')
a2.set_xlabel('D (V/nm)'); a2.set_ylabel('CNP $R_{xx}$ (k$\\Omega$)')
a2.set_title('CNP resistance vs D (sr1) — min locates D=0'); a2.grid(alpha=.3)
plt.show()
jmin = np.argmin(fits['sr1']['rm'][g])
print(f'CNP-R min at D={Dr[jmin]/1e9:+.3f} V/nm (R={fits["sr1"]["rm"][g][jmin]/1e3:.1f}k) -> '
      f'possible small built-in D offset; keeping D_offset=0, will check D-robustness at SdH.')

# --- D=0 line designer (clip to validators by dropping) ---
TG_LIMS, BG_LIMS = (-6.0, 7.0), (-4.5, 4.5)
def D0_gates(n_cm):
    Vbg = (n_cm * 1e4 - n_offset) * cst_e / (2 * c_bg); Vtg = (c_bg / c_tg) * Vbg
    return Vtg, Vbg
print('\nD=0 operating points (n in cm^-2 -> gate volts):')
for ncm in (-1e13, -8e12, -4e12, 0, 4e12, 8e12, 1e13):
    Vtg, Vbg = D0_gates(ncm)
    ok = TG_LIMS[0] <= Vtg <= TG_LIMS[1] and BG_LIMS[0] <= Vbg <= BG_LIMS[1]
    print(f'  n={ncm:+.1e}: Vtg={Vtg:+.3f} Vbg={Vbg:+.3f}  {"OK" if ok else "OUT"}')
Vbg_hi = min(BG_LIMS[1], TG_LIMS[1] * c_tg / c_bg); Vbg_lo = max(BG_LIMS[0], TG_LIMS[0] * c_tg / c_bg)
print(f'realized D=0 n-window within validators: '
      f'{(2*c_bg*Vbg_lo/cst_e+n_offset)/1e4:+.2e} .. {(2*c_bg*Vbg_hi/cst_e+n_offset)/1e4:+.2e} cm^-2')
