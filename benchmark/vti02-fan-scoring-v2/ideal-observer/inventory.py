"""Design inventory for the ideal observer: every fan-ending dev-set episode at both case cuts (prereg-stats
inventory, labelled by observed model) plus every live vti-02 fan (incl. 0823-r6 ramp and 0825-r5).
Grid, densities (actual frame, case n_scale), hours via prereg common.design; component score = capped cells with
Halder tones at the 0.75 T clip (synth-score convention). -> designs.pkl"""
import sys, warnings, pickle
warnings.filterwarnings('ignore'); sys.dont_write_bytecode = True
from pathlib import Path
import numpy as np
TOP = Path('/data/sharpelab/hera-data/vti02-fan-scoring-v2')
sys.path[:0] = [str(TOP / 'prereg-stats'), str(TOP / 'synth-score')]
import common as C
import designs as SD           # synth-score: halder_fl, use_halder, short
HERE = Path(__file__).resolve().parent


def build():
    SD.use_halder()
    eps = [r for r in C.inventory() if r['ending'] == 'fan' and r['cut'] in (C.CUT_0822, C.CUT_0821)]
    eps += [dict(r, model='live', corpus='-', cut='live') for r in C.live_fans() if r['ending'] == 'fan']
    out = []
    for r in eps:
        doc = r['doc']
        B, n, h, acq = C.design(r)
        case = C.g.case_of(Path(r['session'])) if r.get('session') else None
        ramp = None
        if C.g.is_ramp(doc):
            cost = C.g.cost_model(case)
            ramp = dict(start=float(doc['B_ramp_start_T']), target=float(doc['B_ramp_target_T']),
                        rate_T_per_s=(doc.get('ramp_rate_T_per_min') or cost['ramp_T_per_min']) / 60.0,
                        rows=int(doc.get('n_rows_declared') or B.size))
        g075 = C.score(B, n, dict(clip=0.75), acq)
        g_def = C.score(B, n, dict(clip=None), acq)
        out.append(dict(key=r['key'], label=SD.short(r['key']), model=r['model'], corpus=r['corpus'], cut=r['cut'],
                        source=r.get('source'), form=doc.get('form'), field_mode=doc.get('field_mode'),
                        B=np.unique(B[B > 0]), n=np.asarray(n, float), I=acq['I'], tau=acq['tau'], sens=acq['sens'],
                        fd=float(doc['fast_delay_s']), slow_delay=float(doc.get('slow_delay_s') or 0.0), h=float(h),
                        ramp=ramp, cells075=g075['cells'], band075=g075['band'], cells_own=g_def['cells'],
                        snr_mult=acq['snr']))
    return out


if __name__ == '__main__':
    D = build()
    pickle.dump(D, open(HERE / 'designs.pkl', 'wb'))
    for d in D:
        ne = ((d['n'] >= 0.35) & (d['n'] <= 3.45)).sum()
        print(f"{d['label'][:44]:44s} {d['model']:6s} {d['cut'][:8]:8s} B {d['B'].min():.2f}-{d['B'].max():.1f}x{d['B'].size:<4d} "
              f"n {d['n'].min():+.2f}..{d['n'].max():+.2f}x{d['n'].size:<3d} e{ne:<3d} I {d['I']*1e9:4.1f} tau {d['tau']} sens {d['sens']} "
              f"fd {d['fd']} sd {d['slow_delay']} h {d['h']:5.2f} cells075 {d['cells075']:.2f} {'RAMP' if d['ramp'] else ''}")
    print(len(D))
