"""Plug-in tone model for the vti-02 fan grader (Bernal ABAB tetralayer, u_D = 0, actual density frame).

tone_fn(n_actual_1e12, side) -> (F_light, F_heavy, F_L) in tesla.
  Default = refit B: corpus ABAB SWMcC set with gamma2 = -0.0145 eV (fitted to 08-25 + 08-22 electron partitions)
  and gamma3 = 0.3 eV (graphite literature, not fitted; 2D solve). Tabulated in tone_table.csv (no solver at run time).
  F_L = (h/4e)|n| = 10.3392 |n|; F_light + F_heavy = F_L to grid precision.
tone_fn_empirical: linear partition p = 0.1095 + 0.00454 F_L fitted to the same points; electron side only.
Out-of-table densities raise; densities outside the data support warn.
Data support: electron |n| 1.14-3.15 (F_L 11.8-32.6 T); hole |n| 0.71-1.07."""
import warnings
from pathlib import Path
import numpy as np

_T = np.genfromtxt(Path(__file__).with_name('tone_table.csv'), delimiter=',', names=True)
FLN = 10.3392
SUPPORT = {'e': (1.14, 3.15), 'h': (0.71, 1.07)}


def _side(n, side):
    s = side if side in ('e', 'h') else {'electron': 'e', 'hole': 'h'}.get(side)
    if s is None:
        raise ValueError(f"side must be 'e'/'h' (or electron/hole), got {side!r}")
    if n != 0 and (n > 0) != (s == 'e'):
        raise ValueError(f'sign of n = {n} disagrees with side {side!r}')
    return s


def _check(a, s):
    lo, hi = SUPPORT[s]
    if not lo <= a <= hi:
        warnings.warn(f'|n| = {a:.2f}e12 is outside the vti-02 data support {lo}-{hi} ({s} side): model extrapolation', stacklevel=3)


def tone_fn(n_actual_1e12, side, model='B'):
    n = float(n_actual_1e12); s = _side(n, side); a = abs(n)
    sel = _T['n'] > 0 if s == 'e' else _T['n'] < 0
    na = np.abs(_T['n'][sel]); o = np.argsort(na); na = na[o]
    if not na[0] <= a <= na[-1]:
        raise ValueError(f'|n| = {a} outside the tabulated range {na[0]}-{na[-1]} ({s} side); do not clamp')
    _check(a, s)
    fl = np.interp(a, na, _T[f'F_light_{model}'][sel][o]); FL = FLN * a
    return float(fl), float(FL - fl), float(FL)


def tone_fn_empirical(n_actual_1e12, side):
    n = float(n_actual_1e12); s = _side(n, side)
    if s != 'e':
        raise ValueError('empirical partition is fitted on the electron side only')
    _check(abs(n), s)
    FL = FLN * abs(n); p = 0.1095 + 0.0908 * FL / 20.0
    return float(p * FL), float((1 - p) * FL), float(FL)


if __name__ == '__main__':
    for n, sd in ((1.2, 'e'), (2.0, 'e'), (3.0, 'e'), (-1.0, 'h')):
        print(n, sd, 'B', np.round(tone_fn(n, sd), 2), 'corpus', np.round(tone_fn(n, sd, 'corpus'), 2),
              'emp', np.round(tone_fn_empirical(n, sd), 2) if sd == 'e' else '-')
