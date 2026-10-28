"""Column density and acquisition surface: does the ideal observer saturate as columns densify, and where does
acquisition (tau, delay, current, sens) start to cost evidence? -> scale.csv, acq_surface.csv"""
import sys, pickle, itertools
from multiprocessing import Pool
import numpy as np, pandas as pd
import io_core as C
D = {d['label']: d for d in pickle.load(open('designs.pkl', 'rb'))}
BASES = ['live 0822-r8', 'live 0825-r8', 'opus-corpus/20260923T013750-rkg9dn', 'live 0821-r8']
SIG = (0.5, 0.7, 1.0)


def evaluate(d, n, Brc=None, RB=None, RR=None):
    d = dict(d); d['nc'] = n.size
    if Brc is None:
        _, Brc = C.timing(d)
    w = C.weights(d)
    if RB is None:
        RB = C.clean_map(Brc, n, 'B', {}); RR = C.clean_map(Brc, n, 'R', {})
    I = d['I']
    muB, muR = C.blur(RB * I, w), C.blur(RR * I, w)
    mask = (np.abs(muB) < 1.092 * d['sens']) & (np.abs(muR) < 1.092 * d['sens'])
    var = C.noise_var(d, Brc, RB, n)
    tones = C.hb_tones(n, {})
    fl = np.array([t[0][0] if t else 0.0 for t in tones])
    kl, pat, _ = C.tone_kl(muB, muR, var, Brc, n, tones, w, mask=mask, M=3, Qe=1)
    We = C.w_eff(pat, Brc)
    out = dict(KL=kl.sum(), KL_med=float(np.median(kl[kl > 0])) if (kl > 0).any() else 0.0, cols_KL_gt1=int((kl > 1).sum()),
               clip_frac=float(1 - mask.mean()), sig_nV=float(np.sqrt(np.median(var)) * 1e9))
    for sa in SIG:
        e, cells, act = C.evidence(kl, fl, We, sa)
        out[f'nats{sa}'] = e
    out['cells'] = cells; out['active'] = act
    return out, (Brc, RB, RR)


def job_scale(args):
    lab, f = args
    d = D[lab]
    n0 = d['n'][(d['n'] >= C.N_LO) & (d['n'] <= C.N_HI)]
    m = max(2, int(round(n0.size * f)))
    n = np.linspace(n0[0], n0[-1], m)
    r, _ = evaluate(d, n)
    return dict(label=lab, factor=f, cols=m, h_approx=d['h'] * (m / n0.size), **r)


def job_acq(args):
    lab, tau, dly, I, sens = args
    d = dict(D[lab], tau=tau, fd=dly * tau, I=I, sens=sens)
    n = d['n'][(d['n'] >= C.N_LO) & (d['n'] <= C.N_HI)]
    r, _ = evaluate(d, n)
    return dict(label=lab, tau=tau, delay_over_tau=dly, I_nA=I * 1e9, sens=sens, **r)


if __name__ == '__main__':
    jobs = [(lab, f) for lab in BASES for f in (0.25, 0.5, 1.0, 2.0, 4.0)]
    with Pool(6) as p:
        S = pd.DataFrame(p.map(job_scale, jobs, chunksize=1))
    S.to_csv('scale.csv', index=False, float_format='%.5g')
    print(S.to_string())
    jobs = [('live 0822-r8', tau, dly, I, 1e-4) for tau in (0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0) for dly in (1, 4)
            for I in (1e-9, 10e-9, 50e-9)] + [('live 0822-r8', 0.3, 4, 10e-9, s) for s in (1e-3, 1e-2, 5e-2, 0.2)]
    with Pool(6) as p:
        A = pd.DataFrame(p.map(job_acq, jobs, chunksize=1))
    A.to_csv('acq_surface.csv', index=False, float_format='%.5g')
    print(A.to_string())
