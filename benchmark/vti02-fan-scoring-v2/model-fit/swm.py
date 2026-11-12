"""SWMcC ABAB tone model on the corpus builders (read-only import of hera/models/tetralayer_fs_count).
tones(p, n12_array, ud) -> per n: (F_light, F_heavy, F_L) with light/heavy the two largest-|F| pockets of
the carrier sign's two bands. Parameters via corpus Params; defaults = corpus ABAB."""
import sys
from dataclasses import replace
import numpy as np
sys.dont_write_bytecode = True
sys.path.insert(0, '/home/zack/sharpelab/measurement-env/hera/models/tetralayer_fs_count')
import fs_count_b0 as M

ABAB = M.ABAB
FL_PER_N = 10.3392   # T per 1e12 cm^-2, h/(4e)


def params(**kw):
    return replace(ABAB, **kw)


def table(p, ud=0.0, kmax=5e8, nk=5000, ef_max=0.15, nef=6001):
    return M._radial_table('ABAB', p, ud, kmax, nk, ef_max, nef)


def tones(p, n12, ud=0.0, tab=None):
    kg, Eb, EFs, nv = tab if tab is not None else table(p, ud)
    out = []
    for n in np.atleast_1d(n12):
        EF = M._interp_domain_checked(n * 1e16, nv, EFs, 'ABAB')
        orb = M._radial_orbits(kg, Eb, EF)
        # pockets of the carrier sign: electron = rising crossings for n>0, falling for n<0
        want = 1 if n > 0 else -1
        sel = sorted(F for F, k, b, c in orb if (1 if Eb[b, c + 1] > Eb[b, c] else -1) == want)
        other = sum(F for F, k, b, c in orb if (1 if Eb[b, c + 1] > Eb[b, c] else -1) != want)
        if len(sel) >= 2:
            fl, fh = sel[-2], sel[-1]
        elif len(sel) == 1:
            fl, fh = 0.0, sel[0]
        else:
            fl, fh = np.nan, np.nan
        out.append((fl, fh, FL_PER_N * abs(n), len(sel), other))
    return np.array(out)


def mstar(p, n12, ud=0.0):
    out = []
    for n in np.atleast_1d(n12):
        ms = M.bernal_mstar(n * 1e16, 'ABAB', p, ud, kmax=5e8, nk=5000, ef_max=0.15, nef=6001)
        out.append(ms)
    return out


def tones_2d(p, n12, ud=0.0, kmax=4.5e8, ng=401):
    """2D-grid solve (needed when gamma3 != 0: trigonal warping breaks the radial symmetry).
    Per-band occupied areas at E_F; returns rows (F_light, F_heavy, F_L, n_components_light, n_components_heavy)."""
    from scipy.ndimage import label
    kx = np.linspace(-kmax, kmax, ng); KX, KY = np.meshgrid(kx, kx); dk = kx[1] - kx[0]
    E = np.empty((ng * ng, 8))
    kxf, kyf = KX.ravel(), KY.ravel()
    for s in range(0, kxf.size, 40000):
        E[s:s + 40000] = np.linalg.eigvalsh(M.build_h(kxf[s:s + 40000], kyf[s:s + 40000], 'ABAB', p, ud))
    E = E.reshape(ng, ng, 8)
    EFs = np.linspace(-0.12, 0.12, 4801)
    cond = [np.sort(E[..., b].ravel()) for b in (4, 5, 6, 7)]
    val = [np.sort(E[..., b].ravel()) for b in (0, 1, 2, 3)]
    cnt = sum(np.searchsorted(c, EFs) for c in cond) - sum(v.size - np.searchsorted(v, EFs, side='right') for v in val)
    nv = cnt * dk * dk / np.pi ** 2          # m^-2 (g = 4)
    out = []
    for n in np.atleast_1d(n12):
        EF = np.interp(n * 1e16, nv, EFs)
        if n > 0:
            occ = [E[..., b] < EF for b in (4, 5)]
        else:
            occ = [E[..., b] > EF for b in (3, 2)]
        A = [o.sum() * dk * dk for o in occ]
        edge = any(o[0].any() or o[-1].any() or o[:, 0].any() or o[:, -1].any() for o in occ)
        F = sorted(M.F_from_area(a) for a in A)
        nc = [label(o)[1] for o in occ]
        out.append((F[0], F[1], FL_PER_N * abs(n), min(nc), max(nc) + (100 if edge else 0)))
    return np.array(out)
