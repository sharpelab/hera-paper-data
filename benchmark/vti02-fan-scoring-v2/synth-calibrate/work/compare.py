"""Live vs sim on one fan: maps, columns, FFT metrics. usage: compare.py params.json fan [seed] [tones]"""
import sys, json
import numpy as np, pandas as pd
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check')
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/synth-calibrate')
sys.path.insert(0, '.')
from load import load
from fft_q1 import SIGV
import vti02_sim as vs
from evalfan import analyse_arr, spectra
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

SCALE = {'0825-r8': 0.95, '0822-r8': 1.02, '0821-r8': 1.007, '0824-r4': 1.0}
WINS = {'0821-r8': [(2.0, None, 'o2.0'), (1.53, None, 'o1.53')],
        '0822-r8': [(2.0, None, 'o2.0'), (1.53, None, 'o1.53'), (1.0, None, 'full1.0'), (1.0, 2.0, 'sub1-2')],
        '0825-r8': [(2.0, None, 'o2.0'), (1.53, None, 'o1.53'), (1.0, None, 'full1.0'), (1.0, 2.0, 'sub1-2')],
        '0824-r4': [(2.0, None, 'o2.0'), (1.53, None, 'o1.53'), (0.75, None, 'full0.75')]}


def fan_settings(d):
    lk = d['lk']['sr1']
    return dict(I=float(np.median(np.abs(d['I']))), tau=lk['time_constant'], sens=lk['sensitivity'],
                slope=int(lk['filter_slope']), delay=float(d['meta']['fast_delay']))


def sim_fan(p, nm, seed=0, tones='observed', scale=None, d=None):
    d = d or load(nm); st = fan_settings(d)
    s = scale if scale is not None else p.get('n_scale_fans', {}).get(nm, SCALE[nm])
    n_true = d['n'] * s
    ok = n_true > 0.25
    tf = (lambda nn: vs.observed_tones(nn, p['r0'], p['r1'])) if tones == 'observed' else vs.corpus_tones
    R = np.full(d['R'].shape, np.nan)
    rng = np.random.default_rng(seed)
    Rs = vs.simulate(d['B'], n_true[ok], st['I'], st['tau'], st['sens'], rng, tf, params=p,
                     slope_db=st['slope'], delay_s=st['delay'])
    R[:, ok] = Rs
    return d, R, st


def metrics(nm, R, d, st):
    out = []
    for lo, hi, tag in WINS[nm]:
        sel = d['n'] > 0.3
        df = analyse_arr(R[:, sel], d['B'], d['n'][sel], st['I'], SIGV[nm], lo, hi, tag)
        df['col'] = np.where(sel)[0][df.col.values]
        out.append(df)
    return pd.concat(out, ignore_index=True)


if __name__ == '__main__':
    p = json.load(open(sys.argv[1]))
    p = p.get('params', p)
    nm = sys.argv[2]; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    tones = sys.argv[4] if len(sys.argv) > 4 else 'observed'
    d, Rs, st = sim_fan(p, nm, seed, tones)
    L = metrics(nm, d['R'], d, st); S = metrics(nm, Rs, d, st)
    pd.set_option('display.width', 250)
    for tag in L.win.unique():
        a, b = L[L.win == tag], S[S.win == tag]
        print(f'{nm} {tag}: live/sim  light_true {a.light_true.sum()}/{b.light_true.sum()}  FL {a.det_FL.sum()}/{b.det_FL.sum()}  '
              f'split {a.split_true.sum()}/{b.split_true.sum()}  heavy {a.det_heavy.sum()}/{b.det_heavy.sum()}  '
              f'floor/noise med {np.nanmedian(a.floor / a.floor_noise):.2f}/{np.nanmedian(b.floor / b.floor_noise):.2f}  '
              f'SNR ratio sim/live med light {np.nanmedian(b.snr_light.values / a.snr_light.values):.2f} heavy {np.nanmedian(b.snr_heavy.values / a.snr_heavy.values):.2f} '
              f'FL {np.nanmedian(b.snr_FL.values / a.snr_FL.values):.2f}  floor ratio {np.nanmedian(b.floor.values / a.floor.values):.2f}')
    B = d['B']; o = np.argsort(B); on = np.argsort(d['n'])
    fig, axs = plt.subplots(2, 3, figsize=(20, 10))
    vmax = np.nanpercentile(d['R'], 97)
    for ax, R, t in ((axs[0, 0], d['R'], 'live'), (axs[0, 1], Rs, 'sim')):
        ax.pcolormesh(d['n'][on], B[o], R[o][:, on], shading='nearest', vmin=0, vmax=vmax); ax.set_title(f'{nm} {t}')
    ax = axs[0, 2]
    for j, c in zip(np.linspace(3, len(d['n']) - 4, 3).astype(int), 'kbr'):
        ax.plot(B[o], d['R'][o, j], c + '.-', lw=0.8, ms=2, label=f'live n={d["n"][j]:.2f}')
        ax.plot(B[o], Rs[o, j], c + ':', lw=1.0)
    ax.legend(fontsize=7); ax.set_yscale('symlog', linthresh=20)
    # FFT spectra on the full window
    lo = max(1.0, B.min())
    for ax, R, t in ((axs[1, 0], d['R'], 'live'), (axs[1, 1], Rs, 'sim')):
        sp = spectra(R[:, d['n'] > 0.3], B, d['n'][d['n'] > 0.3], lo)
        ns = np.array([s[0] for s in sp]); F = sp[0][1]; Z = np.array([np.interp(F, s[1], s[2]) for s in sp]); oo = np.argsort(ns)
        ax.pcolormesh(F, ns[oo], np.log10(np.maximum(Z[oo], 1e-3)), shading='nearest', cmap='magma', vmin=np.log10(np.nanmedian(Z)) - 1, vmax=np.log10(Z.max()))
        ax.set_xlim(0, 45); ax.set_title(f'{t} |FFT| window [{lo}, Bmax]')
    ax = axs[1, 2]
    for j, c in zip(np.linspace(3, len(d['n']) - 4, 3).astype(int), 'kbr'):
        for R, ls in ((d['R'], '-'), (Rs, ':')):
            sp = spectra(R[:, [j]], B, d['n'][[j]], lo)[0]
            ax.semilogy(sp[1], sp[2], c + ls, lw=0.8)
    ax.set_xlim(0, 60); ax.set_title('spectra live (solid) vs sim (dotted)')
    fig.tight_layout(); fig.savefig(f'cmp_{nm}_{tones}.png', dpi=65)
    L.to_csv(f'live_metrics_{nm}.csv', index=False); S.to_csv(f'sim_metrics_{nm}_{tones}_s{seed}.csv', index=False)
