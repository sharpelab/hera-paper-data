"""Simulate every design x tone model x acquisition x excess noise x seed; live-check detection; -> sim_episodes.csv, sim_columns.csv.gz"""
import sys, pickle, itertools, warnings
warnings.filterwarnings('ignore'); sys.dont_write_bytecode = True
from multiprocessing import Pool
import numpy as np, pandas as pd
import simcore as S
import vti02_sim as vs

D = pickle.load(open('designs.pkl', 'rb'))
TONES = ['halder', 'observed', 'corpus']
NOISE = [55e-9, 87e-9, 165e-9]
SEEDS = [0, 1, 2, 3, 4]
REF = dict(I=50e-9, tau=0.3, sens=100e-6, fd=2.1)


def acqs(d):
    return {'own': dict(I=d['I'], tau=d['tau'], sens=d['sens'], fd=d['fd']),
            'ref': REF,
            'own_noclip': dict(I=d['I'], tau=d['tau'], sens=10.0, fd=d['fd']),   # no clip, LSB ~ 0.6 mV/2^15.. negligible? see below
            'own_I50': dict(I=50e-9, tau=d['tau'], sens=d['sens'] * 5, fd=d['fd'])}


def job(args):
    i, tone = args
    d = D[i]
    Rc = S.clean(d, tone)
    B, n = d['B'], d['n_sim']
    ref = S.light_ref(tone, n)
    wins = {'own': B.min(), 'clip075': max(0.75, B.min())}
    ep, col = [], []
    for aname, a in acqs(d).items():
        st = S.acq_stats(Rc, a['I'], a['tau'], a['sens'], 87e-9)
        for exc in NOISE + [None]:
            seeds = SEEDS if exc is not None else [0]
            for s in seeds:
                rng = np.random.default_rng(1000 * i + s)
                if exc is None:   # noise-free: filter, clip, quantization only
                    R = vs.acquire(Rc, B, a['I'], a['tau'], a['sens'], rng, S.P, 24, a['fd'], e_n=0.0)
                else:
                    R = S.acquire(Rc, B, a['I'], a['tau'], a['sens'], a['fd'], rng, exc)
                if aname == 'own_noclip':
                    rng = np.random.default_rng(1000 * i + s)
                    V = vs._blur_rows(Rc * a['I'], vs.step_weights(a['fd'], a['tau'], 24))
                    if exc is not None:
                        V = V + np.hypot(S.P['e_n_V_rtHz'], exc) * np.sqrt(vs.ENBW[24] / a['tau']) * rng.standard_normal(V.shape)
                    R = V / a['I']
                for wname, lo in wins.items():
                    z = S.detect(R, B, n, ref, lo)
                    both = z['light'] & z['split']
                    b = S.capped(both, ref, z['W'])
                    ep.append(dict(label=d['label'], tone=tone, acq=aname, excess=exc if exc is not None else 0.0, seed=s, win=wname,
                                   ncols=n.size, light=int(z['light'].sum()), light_rfit=int(z['light_rfit'].sum()), split=int(z['split'].sum()),
                                   a=int(both.sum()), b=b, c=b / d['h'], W=z['W'], lo=z['lo'], floor_missing=int((~z['floor_ok']).sum()),
                                   **{k: v for k, v in st.items()}))
                    if tone == 'halder' and wname in ('own', 'clip075') and exc in (87e-9, None):
                        for j in range(n.size):
                            col.append(dict(label=d['label'], acq=aname, excess=exc or 0.0, seed=s, win=wname, n=n[j], F_ref=ref[j],
                                            light=z['light'][j], split=z['split'][j], snr_light=z['snr_light'][j],
                                            snr_heavy=z['snr_heavy'][j], snr_FL=z['snr_FL'][j], Fpk=z['Fpk'][j], W=z['W']))
    return ep, col


if __name__ == '__main__':
    jobs = list(itertools.product(range(len(D)), TONES))
    with Pool(24) as p:
        res = p.map(job, jobs, chunksize=1)
    E = pd.DataFrame([r for e, c in res for r in e]); Cc = pd.DataFrame([r for e, c in res for r in c])
    E.to_csv('sim_episodes.csv', index=False, float_format='%.5g'); Cc.to_csv('sim_columns.csv.gz', index=False, float_format='%.5g')
    print(E.shape, Cc.shape)
