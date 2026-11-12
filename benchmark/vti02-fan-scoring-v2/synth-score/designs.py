"""Design inventory for synth-score: dev-set fans at the 08-22 cut (graded + prereg hand extractions)
plus live 0821-r8 / 0822-r8 / 0824-r4 / 0825-r8. Grid and densities via prereg common.design (grade.field_axis,
grade.columns, case_of, n_scale, grade.derived hours). Grader component scores: common.score with Halder tones
(model-reconcile rescore.use) at the 0.75 T clip."""
import sys, warnings, pickle
warnings.filterwarnings('ignore'); sys.dont_write_bytecode = True
from pathlib import Path
import numpy as np
TOP = Path('/data/sharpelab/hera-data/vti02-fan-scoring-v2')
sys.path[:0] = [str(TOP / 'prereg-stats'), str(TOP / 'model-reconcile')]
import common as C
import tone_fn as TF
LIVE_KEEP = {'live 0821-r8', 'live 0822-r8', 'live 0824-r4', 'live 0825-r8'}
N_LO, N_HI = 0.35, 3.45          # simulated electron columns (sim is electron-only; tone tables start at 0.30)


def halder_fl(n):
    out = []
    for x in np.atleast_1d(np.asarray(n, float)):
        try:
            out.append(TF.tone_fn(x, 'e' if x > 0 else 'h', 'Halder_ABAB', warn=False)[0] if x != 0 else np.nan)
        except ValueError:
            out.append(np.nan)
    return np.array(out)


def use_halder():
    C.f_light = lambda n, tones='model': halder_fl(n)


def short(key):
    return key.replace('vti02-fan-design-', '').replace('/episodes/', '#').replace('/00', '').replace('/0', ' #')


def build():
    use_halder()
    eps = [r for r in C.inventory() if r['ending'] == 'fan' and r['cut'] == C.CUT_0822]
    eps += [dict(r, model='live', corpus='-', source='grader') for r in C.live_fans() if r['key'] in LIVE_KEEP]
    out = []
    for r in eps:
        doc = r['doc']
        B, n, h, acq = C.design(r)
        li = {x['name']: x for x in doc['lockins']}
        Bp = np.unique(B[B > 0])
        sim = (n >= N_LO) & (n <= N_HI)
        g_all = C.score(B, n, dict(clip=0.75), acq)
        g_e = C.score(B, n[sim], dict(clip=0.75), acq)
        g_own = C.score(B, n, dict(clip=None), acq)
        out.append(dict(key=r['key'], label=short(r['key']), model=r['model'], corpus=r['corpus'], source=r.get('source'),
                        form=doc.get('form'), field_mode=doc.get('field_mode'), B=Bp, n=n, n_sim=n[sim], had_B0=bool((B <= 0).any()),
                        I=acq['I'], tau=acq['tau'], sens=acq['sens'], fd=float(doc['fast_delay_s']), h=h, snr=acq['snr'],
                        quant_pred=acq['quant'], g=g_all, g_e=g_e, g_own=g_own))
    return out


if __name__ == '__main__':
    D = build()
    pickle.dump(D, open('designs.pkl', 'wb'))
    for d in D:
        print(f"{d['label'][:44]:44s} {d['model']:6s} B {d['B'].min():.2f}-{d['B'].max():.1f}x{d['B'].size:<4d} n {d['n'].min():+.2f}..{d['n'].max():+.2f}x{d['n'].size:<3d} sim {d['n_sim'].size:3d}  "
              f"I {d['I']*1e9:4.0f} tau {d['tau']} sens {d['sens']:.0e} fd {d['fd']} h {d['h']:5.2f} | band {d['g']['band']:3d} (e {d['g_e']['band']:3d}) cells {d['g']['cells']:.2f} credit {d['g']['credit']:.1f} acq {d['g']['cells_acq']:.2f}")
