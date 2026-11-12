"""Plug-in tone model for the vti-02 fan grader (Bernal ABAB tetralayer, D = 0, actual density frame).

tone_fn(n_actual_1e12, side, model='Halder_ABAB') -> (F_light, F_heavy, F_L) in tesla.
Same interface as model-fit/tone_fn.py. Table-backed (tone_table.csv, built by compute_tones.py + make_table.py);
no solver at call time. F_L = (h/4e)|n| = 10.3392 |n|; F_heavy = F_L - F_light (Luttinger, exact in every model here).

Models (none is fitted to vti-02 unless named):
  'Halder_ABAB'     published ABAB set with middle-pair couplings, gamma3 0.3, no added screening  [default]
  'Shi_ABAB'        its twin (Delta' 0.041 instead of 0.0303)
  'graphite_eps5.7' graphite SWMcC set + self-consistent D = 0 Hartree, eps_z 5.7, Fermi sea only
  'B'               corpus set with gamma2 = -0.0145 (FITTED to 08-25 + 08-22 electron partitions), gamma3 0.3
  'corpus'          the corpus ABAB model (gamma3 0)
  'env_lo'/'env_hi' min / max F_light over B, Halder_ABAB, Shi_ABAB, graphite_eps5.7 (the model band)
Table: electron |n| 0.30-3.60, hole |n| 0.30-2.00. Outside raises (never clamps); outside the vti-02 data
support (electron 1.14-3.15, hole 0.71-1.07) warns."""
import warnings
from pathlib import Path
import numpy as np

_T = np.genfromtxt(Path(__file__).with_name('tone_table.csv'), delimiter=',', names=True)
FLN = 10.3392
SUPPORT = {'e': (1.14, 3.15), 'h': (0.71, 1.07)}
MODELS = ('Halder_ABAB', 'Shi_ABAB', 'graphite_eps5.7', 'B', 'corpus', 'env_lo', 'env_hi')
_COL = {m: 'F_light_' + m.replace('.', '') for m in MODELS}   # genfromtxt drops '.' from names


def _side(n, side):
    s = side if side in ('e', 'h') else {'electron': 'e', 'hole': 'h'}.get(side)
    if s is None:
        raise ValueError(f"side must be 'e'/'h' (or electron/hole), got {side!r}")
    if n != 0 and (n > 0) != (s == 'e'):
        raise ValueError(f'sign of n = {n} disagrees with side {side!r}')
    return s


def _grid(s, col):
    sel = _T['n'] > 0 if s == 'e' else _T['n'] < 0
    na = np.abs(_T['n'][sel]); o = np.argsort(na)
    return na[o], _T[col][sel][o]


def tone_fn(n_actual_1e12, side, model='Halder_ABAB', warn=True):
    if model not in MODELS:
        raise ValueError(f'model must be one of {MODELS}, got {model!r}')
    n = float(n_actual_1e12); s = _side(n, side); a = abs(n)
    na, fl = _grid(s, _COL[model])
    if not na[0] <= a <= na[-1]:
        raise ValueError(f'|n| = {a} outside the tabulated range {na[0]}-{na[-1]} ({s} side); do not clamp')
    lo, hi = SUPPORT[s]
    if warn and not lo <= a <= hi:
        warnings.warn(f'|n| = {a:.2f}e12 is outside the vti-02 data support {lo}-{hi} ({s} side): model extrapolation', stacklevel=2)
    f = float(np.interp(a, na, fl)); FL = FLN * a
    return f, FL - f, FL


def mstar_fn(n_actual_1e12, side, model='Halder_ABAB'):
    """(m_light, m_heavy) in m_e for the four solved models (not the envelope)."""
    n = float(n_actual_1e12); s = _side(n, side); a = abs(n)
    key = model.replace('.', '')
    na, ml = _grid(s, 'm_light_' + key); _, mh = _grid(s, 'm_heavy_' + key)
    if not na[0] <= a <= na[-1]:
        raise ValueError(f'|n| = {a} outside the tabulated range')
    return float(np.interp(a, na, ml)), float(np.interp(a, na, mh))


if __name__ == '__main__':
    warnings.simplefilter('ignore')
    for n, sd in ((1.2, 'e'), (2.0, 'e'), (3.0, 'e'), (-1.0, 'h')):
        print(f'{n:+.1f}', '  '.join(f'{m}: {tone_fn(n, sd, m)[0]:.2f}' for m in MODELS))
