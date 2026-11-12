import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import scipy.constants as cst

m = json.load(open('data/2/metadata.json')); cols = m['columns']
raw = np.loadtxt('data/2/data.tsv.gz')
ci = {c: i for i, c in enumerate(cols)}
mc = m['measurement_config']
Ibias = mc['bias_voltage'] / mc['bias_resistor']

BGv = np.unique(raw[:, ci['k_bg_volt']])     # slow, 25
TGv = np.unique(raw[:, ci['DC_bias']])        # fast, 61
nBG, nTG = len(BGv), len(TGv)
print(f'grid: {nBG} BG x {nTG} TG ; Ibias={Ibias*1e9:.2f} nA ; npts={len(raw)}')

def grid(col):
    g = (raw[:, ci[col]] / Ibias).reshape(nBG, nTG)
    return g
R1 = grid('sr1_X'); R2 = grid('sr2_X'); R3 = grid('sr3_X')
# BG ascending in setpoints (-4.5..+4.5); TG ascending (-6..+6) within each row.
# raw row order: slow ascending, fast ascending -> reshape(nBG,nTG) rows=BG.

# --- CNP ridge per channel: argmax over TG per BG row, smoothed; edge guard ---
def ridge(R):
    tg_cnp = np.full(nBG, np.nan); rmax = np.full(nBG, np.nan); edge = np.zeros(nBG, bool)
    for i in range(nBG):
        prof = gaussian_filter1d(R[i], 1.5)
        j = int(np.nanargmax(prof))
        tg_cnp[i] = TGv[j]; rmax[i] = R[i][j]
        if j <= 1 or j >= nTG - 2:
            edge[i] = True
    return tg_cnp, rmax, edge

for name, R in [('sr1 T3-T4', R1), ('sr2 B4-B5', R2)]:
    tg_cnp, rmax, edge = ridge(R)
    good = ~edge & np.isfinite(tg_cnp)
    p = np.polyfit(BGv[good], tg_cnp[good], 1)
    resid = tg_cnp[good] - np.polyval(p, BGv[good])
    slope, intc = p
    c_bg_over_c_tg = -slope
    print(f'\n[{name}]  rows used {good.sum()}/{nBG} (edge-excluded {edge.sum()})')
    print(f'  CNP line: V_tg = {slope:+.4f}*V_bg + {intc:+.4f}')
    print(f'  ratio c_bg/c_tg = -slope = {c_bg_over_c_tg:.4f}   (geometry prior 15.6/12 = 1.300)')
    print(f'  fit resid: rms {resid.std():.4f} V, max|{np.abs(resid).max():.4f}| V')
    print(f'  CNP Rxx range over good rows: {np.nanmin(rmax[good])/1e3:.1f}k .. {np.nanmax(rmax[good])/1e3:.1f}k')

# --- render both maps with sr1 ridge overlay ---
ext = [TGv.min(), TGv.max(), BGv.min(), BGv.max()]
fig, ax = plt.subplots(1, 3, figsize=(16, 5))
for a, R, ttl in [(ax[0], R1, 'sr1 Rxx T3-T4'), (ax[1], R2, 'sr2 Rxx B4-B5'), (ax[2], R3, 'sr3 Rxy T5-B6')]:
    im = a.imshow(R/1e3, origin='lower', aspect='auto', extent=ext,
                  cmap='viridis', vmin=0, vmax=np.nanpercentile(R/1e3, 99))
    a.set_xlabel('V_TG (V)'); a.set_ylabel('V_BG (V)'); a.set_title(ttl)
    plt.colorbar(im, ax=a, label='kOhm')
tg1, _, e1 = ridge(R1)
ax[0].plot(tg1[~e1], BGv[~e1], 'r.', ms=4, label='CNP ridge')
ax[0].plot(tg1[e1], BGv[e1], 'rx', ms=5, label='edge-clipped')
p1 = np.polyfit(BGv[~e1], tg1[~e1], 1)
ax[0].plot(np.polyval(p1, BGv), BGv, 'w--', lw=1, label=f'fit {p1[0]:+.2f}Vbg{p1[1]:+.2f}')
ax[0].legend(fontsize=7, loc='lower left')
fig.tight_layout(); fig.savefig('hera_scratch/ana_gatemap.png', dpi=100)
print('\nsaved hera_scratch/ana_gatemap.png')
