"""Ideal-observer scores for every design x nuisance setting. -> scores.csv (design x setting), columns_base.csv
(per column at the nominal setting), leak.csv (ABCA-world spurious tone content per column), timing.csv."""
import sys, pickle, time, itertools
from multiprocessing import Pool
import numpy as np, pandas as pd
import io_core as C
D = pickle.load(open('designs.pkl', 'rb'))
SIG = (0.5, 0.7, 1.0)
# (name, physics nuisance for H_B [and the H_R anchor], noise kw, analysis kw)
SETTINGS = [
    ('base', {}, {}, {}),
    ('env_lo', dict(tones='env_lo'), {}, {}), ('env_hi', dict(tones='env_hi'), {}, {}),
    ('s0.97', dict(n_scale=0.97), {}, {}), ('s1.03', dict(n_scale=1.03), {}, {}),
    ('T3', dict(T_K=3.0), {}, {}), ('T6', dict(T_K=6.0), {}, {}),
    ('w0.5', dict(wscale=0.5), {}, {}), ('w2', dict(wscale=2.0), {}, {}),
    ('Q0.5', {}, dict(Q=0.5), {}), ('Q2', {}, dict(Q=2.0), {}),
    ('band', {}, dict(band=True), {}),
    ('dingle', dict(T_K=1.2, p=dict(g_l=1.2, g_h=0.82)), {}, {}),
    ('mis_lo', dict(tones='env_lo'), {}, dict(basis='Halder_ABAB')), ('mis_hi', dict(tones='env_hi'), {}, dict(basis='Halder_ABAB')),
    ('nyq', {}, {}, dict(nyq=True)), ('support', {}, {}, dict(support=True)), ('quant_mean', {}, dict(quant_mean=True), {}),
    ('M4Q2', {}, {}, dict(M=4, Qe=2)), ('clutter', {}, {}, dict(clutter=True)), ('light2', {}, {}, dict(light2=True)),
]
PAIRS = [('env_lo', 'env_hi', 'mis_lo', 'mis_hi'), ('s0.97', 's1.03'), ('T3', 'T6', 'dingle'), ('w0.5', 'w2'), ('Q0.5', 'Q2')]
LEAK = {'R_w.5T3.5': dict(wscale=0.5, T_K=3.5), 'R_T6w2': dict(T_K=6.0, wscale=2.0), 'R_m.8': dict(mscale=0.8)}


def prep(d):
    d = dict(d)
    sel = (d['n'] >= C.N_LO) & (d['n'] <= C.N_HI)
    d['ns'] = d['n'][sel]; d['nc'] = int(sel.sum())
    return d


def run_setting(d, Brc, w, maps, name, nu, nkw, akw, per_col=False):
    n = d['ns']; I = d['I']
    key = tuple(sorted((k, str(v)) for k, v in nu.items()))
    if key not in maps:
        maps[key] = (C.clean_map(Brc, n, 'B', nu), C.clean_map(Brc, n, 'R', {k: v for k, v in nu.items() if k != 'tones'}))
    RB, RR = maps[key]
    muB, muR = C.blur(RB * I, w), C.blur(RR * I, w)
    mask = (np.abs(muB) < 1.092 * d['sens']) & (np.abs(muR) < 1.092 * d['sens']) if d['sens'] else np.ones(RB.shape, bool)
    var = C.noise_var(d, Brc, RB, n, Q=nkw.get('Q', 1.0), band=nkw.get('band', False), quant=not nkw.get('quant_mean'))
    if nkw.get('quant_mean') and d['sens']:
        q = C.vs.lsb(d['sens'])
        muB, muR = np.round(muB / q) * q, np.round(muR / q) * q
        var = var + q ** 2 / 12
    if akw.get('nyq'):
        mask = mask & C.nyquist_mask(Brc, n * nu.get('n_scale', 1.0))
    tnu = dict(nu, tones=akw['basis']) if 'basis' in akw else nu
    tones = C.hb_tones(n, tnu, light2=akw.get('light2', False))
    if akw.get('support'):
        tones = [t if 1.14 <= x * nu.get('n_scale', 1.0) <= 3.15 else [] for t, x in zip(tones, n)]
    fl = np.array([t[0][0] * 1.0 if t else 0.0 for t in tones])
    kl, pat, cr = C.tone_kl(muB, muR, var, Brc, n, tones, w, mask=mask, M=akw.get('M', 3), Qe=akw.get('Qe', 1),
                            clutter=akw.get('clutter', False))
    We = C.w_eff(pat, Brc)
    row = dict(label=d['label'], setting=name, KL=kl.sum(), KL_med=float(np.median(kl[kl > 0])) if (kl > 0).any() else 0.0,
               clip_frac=float(1 - mask.mean()) if mask is not None else 0.0, Weff_med=float(np.median(We[kl > 0])) if (kl > 0).any() else 0.0)
    for sa in SIG:
        e, cells, act = C.evidence(kl, fl, We, sa)
        row[f'nats{sa}'] = e
    row['cells'] = cells; row['active'] = act
    cols = None
    if per_col:
        cols = pd.DataFrame(dict(label=d['label'], n=n, F_light=fl, KL=kl, Weff=We, clutter_ratio=cr,
                                 sig_nV=np.sqrt(np.median(var, 0)) * 1e9, osc_uV=np.std(muB - muR, 0) * 1e6))
    return row, cols, (kl, pat, var, muR, tones)


def job(i):
    d = prep(D[i])
    if d['nc'] == 0:
        return [dict(label=d['label'], setting=s[0], KL=0.0, **{f'nats{sa}': 0.0 for sa in SIG}, cells=0.0, active=0) for s in SETTINGS], None, None, None
    t0 = time.time()
    t, Brc = C.timing(d); w = C.weights(d)
    maps = {}
    rows, cols = [], None
    base = None
    for name, nu, nkw, akw in SETTINGS:
        r, c, aux = run_setting(d, Brc, w, maps, name, nu, nkw, akw, per_col=(name == 'base'))
        rows.append(r)
        if name == 'base':
            cols, base = c, aux
    # least-favourable corner: the worse member of each pair (by nats at sigma_a 0.7), combined
    by = {r['setting']: r for r in rows}
    worst = [min(p, key=lambda s: by[s]['nats0.7']) for p in PAIRS]
    nu, nkw, akw = {}, {}, {}
    for s in worst:
        spec = next(x for x in SETTINGS if x[0] == s)
        nu.update(spec[1]); nkw.update(spec[2]); akw.update(spec[3])
    r, _, _ = run_setting(d, Brc, w, maps, 'corner', nu, nkw, akw)
    r['corner_of'] = '+'.join(worst)
    rows.append(r)
    r, _, _ = run_setting(d, Brc, w, maps, 'corner_nyq', nu, nkw, dict(akw, nyq=True))
    r['corner_of'] = '+'.join(worst) + '+nyq'
    rows.append(r)
    # ABCA worlds with other nuisances: spurious tone content (the within-model mimic)
    kl0, pat0, var0, muR0, tones0 = base
    lk = []
    for name, nu in LEAK.items():
        RRx = C.clean_map(Brc, d['ns'], 'R', nu)
        klx, _, _ = C.tone_kl(C.blur(RRx * d['I'], w), muR0, var0, Brc, d['ns'], tones0, w, M=3, Qe=1)
        lk.append(pd.DataFrame(dict(label=d['label'], world=name, n=d['ns'], KL_leak=klx, KL_B=kl0)))
    tm = dict(label=d['label'], rows=Brc.shape[0], cols=d['nc'], maps=len(maps), seconds=time.time() - t0)
    print(f"{d['label'][:40]:40s} {Brc.shape} {tm['seconds']:.0f}s", flush=True)
    return rows, cols, pd.concat(lk), tm


if __name__ == '__main__':
    idx = list(range(len(D)))
    idx.sort(key=lambda i: -D[i]['B'].size * D[i]['n'].size)
    with Pool(6) as p:
        res = p.map(job, idx, chunksize=1)
    pd.DataFrame([r for x in res for r in x[0]]).to_csv('scores.csv', index=False, float_format='%.5g')
    pd.concat([x[1] for x in res if x[1] is not None]).to_csv('columns_base.csv', index=False, float_format='%.5g')
    pd.concat([x[2] for x in res if x[2] is not None]).to_csv('leak.csv', index=False, float_format='%.5g')
    pd.DataFrame([x[3] for x in res if x[3] is not None]).to_csv('timing.csv', index=False, float_format='%.4g')
