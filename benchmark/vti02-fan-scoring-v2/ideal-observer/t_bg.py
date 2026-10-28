"""Background-model sensitivity: add Legendre(1/B) degree 2-4 to the smooth background (the analyst cannot
assume the background is a degree-5 polynomial in B), with and without the Nyquist gate. -> bg_sens.csv"""
import pickle
from multiprocessing import Pool
import numpy as np, pandas as pd
import io_core as C
D = {d['label']: d for d in pickle.load(open('designs.pkl', 'rb'))}
LABS = ['live 0822-r8', 'live 0825-r8', 'live 0821-r8', 'live 0824-r4', 'live 0823-r6', 'fable-corpus/20260922T163113',
        'sol-none/20260923T013751-ls25bv', 'astra-none/20260923T020213-9t26k2 #1', 'opus-corpus/20260923T013750-rkg9dn',
        'fable-corpus/20260922T192335', 'fable-corpus/20260922T232408', 'opus-none/20260923T013750-ou2xbh']


def job(lab):
    d = dict(D[lab]); n = d['n'][(d['n'] >= C.N_LO) & (d['n'] <= C.N_HI)]; d['nc'] = n.size
    t, Brc = C.timing(d); w = C.weights(d); I = d['I']
    RB = C.clean_map(Brc, n, 'B', {}); RR = C.clean_map(Brc, n, 'R', {})
    muB, muR = C.blur(RB * I, w), C.blur(RR * I, w)
    var = C.noise_var(d, Brc, RB, n)
    tones = C.hb_tones(n, {}); fl = np.array([x[0][0] if x else 0.0 for x in tones])
    out = []
    for nyq in (False, True):
        mask = (np.abs(muB) < 1.092 * d['sens']) & (np.abs(muR) < 1.092 * d['sens'])
        if nyq:
            mask &= C.nyquist_mask(Brc, n)
        for ud in (0, 2, 3, 4):
            kl, pat, _ = C.tone_kl(muB, muR, var, Brc, n, tones, w, mask=mask, M=3, Qe=1, clutter=False, udeg=ud)
            e, cells, act = C.evidence(kl, fl, C.w_eff(pat, Brc), 0.5)
            out.append(dict(label=lab, nyq=nyq, udeg=ud, KL=kl.sum(), nats=e, cells=cells, active=act, h=d['h']))
    return out


if __name__ == '__main__':
    with Pool(6) as p:
        R = pd.DataFrame([r for x in p.map(job, LABS, chunksize=1) for r in x])
    R.to_csv('bg_sens.csv', index=False, float_format='%.4g')
    print(R.pivot_table(index='label', columns=['nyq', 'udeg'], values='nats').round(1).to_string())
