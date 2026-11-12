#!/usr/bin/env python3
"""Standard blind plot for one archived sweep dir: R_k = sr_k_X / I_bias vs swept axis.
1D -> line per channel; 2D -> log10|R| image per channel. Prints PNG path."""
import json, gzip, sys, ast, pathlib, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def load(d):
    d = pathlib.Path(d); m = json.load(open(d/'metadata.json'))
    arr = np.genfromtxt(gzip.open(d/'data.tsv.gz', 'rt'), delimiter='\t')
    L = lambda v: ast.literal_eval(v) if isinstance(v, str) and v[:1] in '[{' else v
    hdr = L(m['columns']); cfg = L(m['measurement_config'])
    # normalise 2D keys: fast/slow param name + setpoint list (first of co-swept group)
    if m['type'] == '2D':
        fp, sp = m.get('fast_params') or [m['fast_param']], m.get('slow_params') or [m['slow_param']]
        fs, ss = L(m['fast_setpoints']), L(m['slow_setpoints'])
        m['_fast'], m['_slow'] = fp[0], sp[0]
        m['_fs'] = fs[0] if isinstance(fs[0], list) else fs
        m['_ss'] = ss[0] if isinstance(ss[0], list) else ss
    return m, hdr, arr, cfg
def channels(hdr, arr, cfg):
    col = {h: i for i, h in enumerate(hdr)}
    I = arr[:, col['sr0_X']] / cfg.get('sr0_gain', -1e6) if 'sr0_X' in col else None
    out = {}
    for k in (1, 2, 3):
        c = f'sr{k}_X'
        if c in col: out[f'sr{k} ({cfg.get(f"sr{k}", "")})'] = arr[:, col[c]] / I if I is not None else arr[:, col[c]]
    return out
def plot(d, out_png):
    m, hdr, arr, cfg = load(d); ch = channels(hdr, arr, cfg); col = {h: i for i, h in enumerate(hdr)}
    cm = m['comments'] if isinstance(m['comments'], list) else ast.literal_eval(m['comments']); title = ' — '.join(cm[:2])
    if m['type'] == '1D':
        x = arr[:, col[m['param']]]
        fig, ax = plt.subplots(1, len(ch), figsize=(5 * len(ch), 3.6))
        for a, (k, v) in zip(np.atleast_1d(ax), ch.items()): a.plot(x, v, lw=.8); a.set(xlabel=m['param'], ylabel='R (Ω)', title=k)
    else:
        fs, ss = m['_fs'], m['_ss']; nf = len(fs); nrow = arr.shape[0] // nf
        fig, ax = plt.subplots(1, len(ch), figsize=(5.5 * len(ch), 4.2))
        for a, (k, v) in zip(np.atleast_1d(ax), ch.items()):
            Z = np.log10(np.abs(v[:nrow * nf].reshape(nrow, nf)))
            im = a.pcolormesh(fs, ss[:nrow], Z, shading='auto'); fig.colorbar(im, ax=a, label='log10 |R| (Ω)')
            a.set(xlabel=m['_fast'], ylabel=m['_slow'], title=k)
    fig.suptitle(title); fig.tight_layout(); fig.savefig(out_png, dpi=110); plt.close(fig); return out_png
if __name__ == '__main__':
    print(plot(sys.argv[1], sys.argv[2]))
