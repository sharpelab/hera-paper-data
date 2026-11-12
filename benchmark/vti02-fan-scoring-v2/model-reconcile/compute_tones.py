"""Tone tables for every candidate grader model, both carrier signs -> tone_table_all.csv.
Solver: model-literature/abab_lib.py (corpus build_h + middle-pair override + layer potential), 2D grid
(kmax 3.8e8, 701^2) for every model incl. corpus (gamma3 = 0 grid == radial to ~0.001 T, checked in check_solver.py).
Per n: light / heavy = smaller / larger |F| of the two carrier-sign bands nearest E_F (e: bands 4,5; h: 3,2);
masses from dA/dE; 'extra' = |F| of any opposite-sign pocket (bands 3 for e, 4 for h), flagged.
graphite_eps5.7: graphite_DD + self-consistent D = 0 Hartree, eps_z 5.7, Fermi-sea only (as model-literature)."""
import sys
from dataclasses import replace
from concurrent.futures import ProcessPoolExecutor
import numpy as np, pandas as pd
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/model-literature')
sys.dont_write_bytecode = True
import abab_lib as L
from litsets_defs import SETS

GRAPHITE = L.PX(g0=3.16, g1=0.39, g2=-0.020, g3=0.315, g4=0.044, g5=0.038, dp=0.050)
MODELS = {
    'corpus': (L.M.ABAB, None),
    'B': (replace(L.M.ABAB, g2=-0.0145, g3=0.3), None),
    'B_g2lo': (replace(L.M.ABAB, g2=-0.0161, g3=0.3), None),   # -0.0145 - 0.0016 (stat+syst, 2x)
    'B_g2hi': (replace(L.M.ABAB, g2=-0.0129, g3=0.3), None),
    'Halder_ABAB': (SETS['Halder_ABAB'], None),
    'Shi_ABAB': (SETS['Shi_ABAB'], None),
    'graphite_eps5.7': (GRAPHITE, 5.7),
}
NE = np.round(np.arange(0.30, 4.0001, 0.05), 3)
NH = -np.round(np.arange(0.30, 2.0001, 0.05), 3)
NN = np.concatenate([NH[::-1], NE])


def rows_from(res, name):
    out = []
    for r in res:
        n = r['n']; b = list(r['bands'])
        car = (4, 5) if n > 0 else (3, 2)
        opp = 3 if n > 0 else 4
        F = {bb: abs(r['F'][b.index(bb)]) for bb in b}
        m = {bb: r['m'][b.index(bb)] for bb in b}
        lo, hi = sorted(car, key=lambda bb: F[bb])
        out.append(dict(model=name, n=round(n, 3), EF_meV=r['EF'] * 1e3, F_light=F[lo], F_heavy=F[hi],
                        m_light=m[lo], m_heavy=m[hi], F_extra=F[opp], F_L=L.FL_PER_N * abs(n)))
    return out


def grid_multi(p, U, ns, kmax=3.8e8, ng=701, nef=3000, ef_max=0.25):
    """abab_lib.grid_solve with one grid for all densities; densities outside the solved domain are dropped."""
    Eg, dA, edge, bands = L.grid_bands(p, U, kmax, ng)
    cond = np.array([b >= L.N_LAY for b in bands])
    lo_ok = max(Eg[i][edge].max() for i in range(len(bands)) if not cond[i])
    hi_ok = min(Eg[i][edge].min() for i in range(len(bands)) if cond[i])
    EFs = np.linspace(max(lo_ok, -ef_max), min(hi_ok, ef_max), nef)
    A = np.zeros((nef, len(bands)))
    for i in range(len(bands)):
        srt = np.sort(Eg[i]); c = np.searchsorted(srt, EFs)
        A[:, i] = (c if cond[i] else -(srt.size - c)) * dA
    n_tab = A.sum(1) * 4 / (2 * np.pi) ** 2 / 1e16
    out = []
    for n in ns:
        try:
            out += [dict(r, bands=bands) for r in L._per_density(EFs, A, n_tab, [n])]
        except ValueError:
            pass
    return out


def plain(name):
    p, _ = MODELS[name]
    return rows_from(grid_multi(p, np.zeros(4), list(NN)), name)


def hartree_one(args):
    name, n = args
    p, eps = MODELS[name]
    try:
        U, _ = L.hartree_U(p, n, eps, include_valence=False)
        res = grid_multi(p, U, [n])
    except ValueError:
        return []
    rows = rows_from(res, name)
    for r in rows:
        r['U_outer_meV'] = float((U[0] - U[1]) * 1e3)
    return rows


if __name__ == '__main__':
    plain_names = [k for k, v in MODELS.items() if v[1] is None]
    hart = [(k, n) for k, v in MODELS.items() if v[1] is not None for n in NN]
    with ProcessPoolExecutor(30) as ex:
        fa = [ex.submit(plain, k) for k in plain_names]
        hb = list(ex.map(hartree_one, hart, chunksize=1))
        rows = [r for f in fa for r in f.result()] + [r for x in hb for r in x]
    T = pd.DataFrame(rows).sort_values(['model', 'n'])
    T['frac'] = T.F_light / T.F_L
    T['lutt'] = (T.F_light + T.F_heavy) / T.F_L - 1
    T.to_csv('tone_table_all.csv', index=False, float_format='%.5f')
    piv = T.pivot_table(index='n', columns='model', values='frac')
    print(piv.loc[[x for x in piv.index if round(abs(x), 2) in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.5)]].round(3).to_string())
    print('max |Luttinger| by model:', T.groupby('model').lutt.apply(lambda s: s.abs().max()).round(4).to_dict())
    print('max F_extra by model:', T.groupby('model').F_extra.max().round(3).to_dict())
