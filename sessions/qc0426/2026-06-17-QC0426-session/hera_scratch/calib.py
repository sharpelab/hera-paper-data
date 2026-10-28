import numpy as np, json
from scipy.ndimage import gaussian_filter1d
import scipy.constants as cst
e, eps0, kap = cst.e, cst.epsilon_0, 3.0

m = json.load(open('data/2/metadata.json')); cols = m['columns']
raw = np.loadtxt('data/2/data.tsv.gz'); ci = {c: i for i, c in enumerate(cols)}
mc = m['measurement_config']; Ib = mc['bias_voltage']/mc['bias_resistor']
BGv = np.unique(raw[:, ci['k_bg_volt']]); TGv = np.unique(raw[:, ci['DC_bias']])
nBG, nTG = len(BGv), len(TGv)
R1 = (raw[:, ci['sr1_X']]/Ib).reshape(nBG, nTG)
R2 = (raw[:, ci['sr2_X']]/Ib).reshape(nBG, nTG)

def ridge(R):
    tg = np.full(nBG, np.nan); rm = np.full(nBG, np.nan); edge = np.zeros(nBG, bool)
    for i in range(nBG):
        j = int(np.nanargmax(gaussian_filter1d(R[i], 1.5)))
        tg[i] = TGv[j]; rm[i] = R[i][j]; edge[i] = (j <= 1 or j >= nTG-2)
    return tg, rm, edge

# Per-channel fits
fits = {}
for nm, R in [('sr1', R1), ('sr2', R2)]:
    tg, rm, edge = ridge(R); good = ~edge & np.isfinite(tg)
    s, b = np.polyfit(BGv[good], tg[good], 1)
    fits[nm] = dict(slope=s, intc=b, n=int(good.sum()),
                    resid=float((tg[good]-np.polyval([s, b], BGv[good])).std()),
                    rmin=float(np.nanmin(rm[good])), rmax=float(np.nanmax(rm[good])),
                    tg=tg, rm=rm, edge=edge)

# --- Adopt device calibration ---
# ratio confirmed = geometry (1.305/1.298 vs 1.300). Anchor c_bg at geometry
# (single-dielectric back gate), c_tg from geometry (ratio matches).
t_tg, t_bg = 15.6e-9, 12e-9
c_tg = eps0*kap/t_tg
c_bg = eps0*kap/t_bg               # SiO2 term zeroed (Si is a screening gate)
ratio_fit = 0.5*(fits['sr1']['slope']+fits['sr2']['slope'])   # avg slope
b_dev = 0.5*(fits['sr1']['intc']+fits['sr2']['intc'])          # avg intercept (TG @ BG=0)
n_offset = -(c_tg*b_dev)/e         # so n=0 along the CNP line (n const = c_tg*b/e there)
D_offset = 0.0                     # stated assumption: gates define D=0 geometrically

def calc_nD(Vtg, Vbg):
    n = (c_tg*Vtg + c_bg*Vbg)/e + n_offset
    D = 0.5*(c_tg*Vtg - c_bg*Vbg)/eps0 + D_offset
    return n, D

print(f'c_tg={c_tg:.4e} F/m^2  c_bg={c_bg:.4e} F/m^2  (geometry; ratio c_bg/c_tg={c_bg/c_tg:.4f})')
print(f'fitted slope avg={ratio_fit:.4f} -> ratio {-ratio_fit:.4f} ; intercept avg b={b_dev:+.4f} V')
print(f'n_offset = {n_offset/1e4:.3e} cm^-2 ;  D_offset = 0')

# Closure: n along each channel ridge should be ~0
for nm in ('sr1', 'sr2'):
    f = fits[nm]; g = ~f['edge'] & np.isfinite(f['tg'])
    nr, Dr = calc_nD(f['tg'][g], BGv[g])
    print(f'  closure {nm}: |n| along ridge max {np.abs(nr).max()/1e4:.2e} cm^-2, '
          f'D span {Dr.min()/1e9:+.3f}..{Dr.max()/1e9:+.3f} V/nm')

# CNP-R vs D check (where along the ridge is CNP least resistive -> D=0 sanity)
f = fits['sr1']; g = ~f['edge'] & np.isfinite(f['tg'])
nr, Dr = calc_nD(f['tg'][g], BGv[g]); rm = f['rm'][g]
jmin = int(np.argmin(rm))
print(f'  CNP-R min (sr1): {rm[jmin]/1e3:.1f}k at D={Dr[jmin]/1e9:+.3f} V/nm  '
      f'(expect near D=0 if gates define symmetry); CNP-R range {rm.min()/1e3:.1f}k..{rm.max()/1e3:.1f}k')

# --- D=0 line design, clipped to validators ---
TG_LIMS, BG_LIMS = (-6.0, 7.0), (-4.5, 4.5)
def gate_volts_D0(n_target):   # along D=0: c_tg*Vtg=c_bg*Vbg -> Vtg=(c_bg/c_tg)Vbg
    # n = (c_tg*Vtg+c_bg*Vbg)/e+n_off ; with Vtg=(c_bg/c_tg)Vbg -> n=2*c_bg*Vbg/e+n_off
    Vbg = (n_target - n_offset)*e/(2*c_bg)
    Vtg = (c_bg/c_tg)*Vbg
    return Vtg, Vbg
print('\nD=0 line endpoints (target n -> required gates):')
for nt_cm in (-1.0e13, -8e12, -4e12, 0, 4e12, 8e12, 1.0e13):
    Vtg, Vbg = gate_volts_D0(nt_cm*1e4)
    ok = (TG_LIMS[0] <= Vtg <= TG_LIMS[1]) and (BG_LIMS[0] <= Vbg <= BG_LIMS[1])
    nn, DD = calc_nD(Vtg, Vbg)
    print(f'  n={nt_cm:+.2e}: Vtg={Vtg:+.3f} Vbg={Vbg:+.3f}  ->check n={nn/1e4:+.2e} D={DD/1e9:+.4f}V/nm  {"OK" if ok else "OUT-OF-RANGE"}')
# realized n-window on D=0 within validators
Vbg_max = min(BG_LIMS[1], TG_LIMS[1]*c_tg/c_bg)
Vbg_min = max(BG_LIMS[0], TG_LIMS[0]*c_tg/c_bg)
n_hi = (2*c_bg*Vbg_max)/e + n_offset; n_lo = (2*c_bg*Vbg_min)/e + n_offset
print(f'realized D=0 n-window within validators: {n_lo/1e4:+.2e} .. {n_hi/1e4:+.2e} cm^-2')
