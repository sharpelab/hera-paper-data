"""ABAB electron-side light/heavy tones under parameter overrides.

Wraps the corpus builder (hera/models/tetralayer_fs_count/fs_count_b0.py, imported read-only)
and adds: a per-layer onsite potential U_l (for Hartree / D), a radial solver (gamma3 = 0) and
a 2D k-grid solver (gamma3 != 0) that return per-band signed Onsager areas and masses.
Densities in 1e12 cm^-2; frequencies in T; masses in m_e.
"""
import sys
from dataclasses import replace, dataclass
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, '/home/zack/sharpelab/measurement-env/hera/models/tetralayer_fs_count')
import fs_count_b0 as M  # noqa: E402

HBAR, E, ME = M.HBAR, M.E, M.ME
Params = M.Params
FL_PER_N = M.F_from_area((2 * np.pi) ** 2 * 1e16 / 4)   # 10.339 T per 1e12 cm^-2
N_LAY = 4


@dataclass(frozen=True)
class PX(M.Params):
    """Params plus optional middle-link (layers 2-3, 'bulk' bilayer) overrides G1/G3/G4 (eV)."""
    G1: float = None
    G3: float = None
    G4: float = None


def hamiltonian(kx, ky, p, U):
    """Corpus Bernal H + diagonal layer potential U (eV, length 4, both sublattices)
    + middle-link overrides when p is a PX with G1/G3/G4 set."""
    H = M.build_h(kx, ky, 'ABAB', p, 0.0)
    if isinstance(p, PX) and p.G1 is not None:
        ktp, _ = M._ktilde(kx, ky)
        d1, d3, d4 = p.G1 - p.g1, p.G3 - p.g3, p.G4 - p.g4
        blk = {(2, 4): -d4 * ktp, (2, 5): d1 + 0 * ktp, (3, 4): d3 * ktp, (3, 5): -d4 * ktp}
        for (i, j), v in blk.items():
            H[..., i, j] += v
            H[..., j, i] += np.conj(v)
    for l, u in enumerate(U):
        H[..., 2 * l, 2 * l] += u
        H[..., 2 * l + 1, 2 * l + 1] += u
    return H


def linear_U(ud):
    return (np.arange(N_LAY) - 1.5) * ud


# ---------------- radial (gamma3 = 0) ----------------

def radial_bands(p, U, kmax=4.5e8, nk=6000, vecs=False):
    kg = np.linspace(1e3, kmax, nk)
    H = hamiltonian(kg, 0.0, p, U)
    if vecs:
        w, v = np.linalg.eigh(H)
        return kg, w.T, v
    return kg, np.linalg.eigvalsh(H).T, None


def radial_band_areas(kg, Eb, EF):
    """Per-band signed area (m^-2 units of k^2): sum over crossings of +/- pi k^2."""
    out = np.zeros(Eb.shape[0])
    for b in range(Eb.shape[0]):
        cross = np.where((Eb[b, :-1] - EF) * (Eb[b, 1:] - EF) < 0)[0]
        for c in cross:
            # linear interpolation of k at the crossing
            e0, e1 = Eb[b, c] - EF, Eb[b, c + 1] - EF
            k = kg[c] + (kg[c + 1] - kg[c]) * e0 / (e0 - e1)
            out[b] += (1.0 if e1 > e0 else -1.0) * np.pi * k * k
    return out


def radial_solve(p, U, n12_list, kmax=4.5e8, nk=6000, ef_max=0.25, nef=5001):
    """For each density: E_F, per-band signed F (T), per-band m* (m_e, from dA/dE)."""
    kg, Eb, _ = radial_bands(p, U, kmax, nk)
    EFs = np.linspace(-ef_max, ef_max, nef)
    # drop rows where any band is occupied at the grid edge in a way that truncates a contour
    ok = []
    for ef in EFs:
        edge_cross = False
        for b in range(Eb.shape[0]):
            if Eb[b, -1] > Eb[b, -2] and Eb[b, -1] < ef:     # rising band still below EF at kmax
                edge_cross = True
            if Eb[b, -1] < Eb[b, -2] and Eb[b, -1] > ef:     # falling band still above EF at kmax
                edge_cross = True
        ok.append(not edge_cross)
    EFs = EFs[np.array(ok)]
    A = np.array([radial_band_areas(kg, Eb, ef) for ef in EFs])          # (nef, nb)
    n_tab = A.sum(1) * 4 / (2 * np.pi) ** 2 / 1e16                        # 1e12 cm^-2
    return _per_density(EFs, A, n_tab, n12_list)


def _per_density(EFs, A, n_tab, n12_list):
    order = np.argsort(n_tab)
    res = []
    for n12 in n12_list:
        if not (n_tab.min() <= n12 <= n_tab.max()):
            raise ValueError(f'n={n12} outside solved table [{n_tab.min():.2f}, {n_tab.max():.2f}]')
        ef = np.interp(n12, n_tab[order], EFs[order])
        i = np.searchsorted(EFs, ef)
        lo, hi = max(i - 6, 0), min(i + 6, len(EFs) - 1)
        Ab = np.array([np.interp(ef, EFs, A[:, b]) for b in range(A.shape[1])])
        dAdE = (A[hi] - A[lo]) / ((EFs[hi] - EFs[lo]) * E)
        F = M.F_from_area(Ab)
        m = HBAR ** 2 / (2 * np.pi) * np.abs(dAdE) / ME
        res.append(dict(n=n12, EF=ef, F=F, m=m))
    return res


# ---------------- 2D grid (gamma3 != 0) ----------------

def grid_bands(p, U, kmax=3.8e8, ng=701, bands=(2, 3, 4, 5), chunk=60000):
    kx = np.linspace(-kmax, kmax, ng)
    KX, KY = np.meshgrid(kx, kx)
    kxf, kyf = KX.ravel(), KY.ravel()
    out = np.empty((len(bands), kxf.size))
    for s in range(0, kxf.size, chunk):
        e = s + chunk
        w = np.linalg.eigvalsh(hamiltonian(kxf[s:e], kyf[s:e], p, U))
        out[:, s:e] = w[:, list(bands)].T
    edge = np.zeros((ng, ng), bool)
    edge[0] = edge[-1] = edge[:, 0] = edge[:, -1] = True
    return out, (kx[1] - kx[0]) ** 2, edge.ravel(), bands


def grid_solve(p, U, n12_list, kmax=3.8e8, ng=701, nef=3000, ef_max=0.25):
    Eg, dA, edge, bands = grid_bands(p, U, kmax, ng)
    nb = len(bands)
    # valence bands (index < 4): signed area = -(area above EF); conduction: +(area below EF)
    cond = np.array([b >= N_LAY for b in bands])
    lo_ok = max(Eg[i][edge].max() for i in range(nb) if not cond[i])
    hi_ok = min(Eg[i][edge].min() for i in range(nb) if cond[i])
    EFs = np.linspace(max(lo_ok, -ef_max), min(hi_ok, ef_max), nef)
    srt = [np.sort(Eg[i]) for i in range(nb)]
    A = np.zeros((nef, nb))
    for i in range(nb):
        cnt_below = np.searchsorted(srt[i], EFs)
        A[:, i] = (cnt_below if cond[i] else -(srt[i].size - cnt_below)) * dA
    n_tab = A.sum(1) * 4 / (2 * np.pi) ** 2 / 1e16
    res = _per_density(EFs, A, n_tab, n12_list)
    return [dict(r, bands=bands) for r in res]


def tones(res, bands):
    """Map per-band signed F to (light, heavy, hole) — light = the smaller of the two lowest
    conduction bands' electron areas, heavy = the larger; hole = valence-band hole area."""
    bands = list(bands)
    ci = [bands.index(b) for b in (4, 5) if b in bands]
    vi = [bands.index(b) for b in (3,) if b in bands]
    out = []
    for r in res:
        Fc = sorted(r['F'][ci], key=abs)
        mc = [r['m'][i] for i in sorted(ci, key=lambda i: abs(r['F'][i]))]
        Fh = r['F'][vi[0]] if vi else 0.0
        out.append(dict(n=r['n'], EF_meV=r['EF'] * 1e3, F_light=Fc[0], F_heavy=Fc[1],
                        F_hole=Fh, m_light=mc[0], m_heavy=mc[1],
                        FL=FL_PER_N * r['n'], frac=Fc[0] / (FL_PER_N * r['n'])))
    return out


def solve(p, n12_list, U=(0, 0, 0, 0), grid=None):
    """Radial when gamma3 == 0 and grid is not forced, else 2D grid."""
    use_grid = (p.g3 != 0) if grid is None else grid
    if use_grid:
        res = grid_solve(p, U, n12_list)
        return tones(res, res[0]['bands'])
    res = radial_solve(p, U, n12_list)
    return tones(res, range(2 * N_LAY))


# ---------------- self-consistent Hartree (symmetric dual gating, D = 0 or finite) ----------

def layer_density(p, U, n12, kmax=4.5e8, nk=4000, include_valence=True, U0_ref=None):
    """Layer-resolved excess electron density (1e12 cm^-2) at total n12, radial (gamma3 = 0).
    Excess = conduction occupation - valence emptiness (Fermi-sea part) plus, optionally,
    the valence-sea polarization relative to U = 0 (integrated to kmax)."""
    kg, Eb, V = radial_bands(p, U, kmax, nk, vecs=True)
    res = radial_solve(p, U, [n12], kmax=kmax, nk=nk)
    EF = res[0]['EF']
    w = np.abs(V) ** 2                                         # (nk, site, band)
    wl = w[:, 0::2, :] + w[:, 1::2, :]                         # (nk, layer, band)
    En = Eb.T                                                  # (nk, band)
    occ = (En < EF).astype(float)
    ref = np.zeros_like(occ); ref[:, :N_LAY] = 1.0             # neutral: lower N bands full
    dk = kg[1] - kg[0]
    meas = 4 / (2 * np.pi) * kg * dk                           # g * k dk / 2pi -> per m^2
    excess = ((occ - ref)[:, None, :] * wl).sum(2)             # (nk, layer)
    nl = (excess * meas[:, None]).sum(0) / 1e16
    if include_valence:
        if U0_ref is None:
            _, _, V0 = radial_bands(p, (0, 0, 0, 0), kmax, nk, vecs=True)
            U0_ref = V0
        w0 = np.abs(U0_ref) ** 2
        wl0 = w0[:, 0::2, :] + w0[:, 1::2, :]
        pol = (wl[:, :, :N_LAY].sum(2) - wl0[:, :, :N_LAY].sum(2))
        nl = nl + (pol * meas[:, None]).sum(0) / 1e16
    return nl, EF


def hartree_U(p, n12, eps_z, d=0.335e-9, D_Vnm=0.0, iters=60, mix=0.3, include_valence=True):
    """Self-consistent layer potential (eV) for electrons at density n12 between symmetric gates
    plus an external displacement field D (V/nm, D/eps0 convention; field between the gates'
    contributions). U_{l+1}-U_l = e^2 d (sum_{>l} n - sum_{<=l} n)/(2 eps0 eps_z) - e d D/eps_z."""
    U = np.zeros(N_LAY)
    _, _, V0 = radial_bands(p, (0, 0, 0, 0), 4.5e8, 4000, vecs=True)
    pref = E * d / (2 * M.cst.epsilon_0 * eps_z) * 1e16       # eV per (1e12 cm^-2)
    for _ in range(iters):
        nl, EF = layer_density(p, U, n12, include_valence=include_valence, U0_ref=V0)
        Unew = np.zeros(N_LAY)
        for l in range(N_LAY - 1):
            diff = nl[l + 1:].sum() - nl[:l + 1].sum()
            Unew[l + 1] = Unew[l] + pref * diff - d * 1e9 * D_Vnm / eps_z
        Unew -= Unew.mean()
        if np.max(np.abs(Unew - U)) < 2e-5:
            U = Unew
            break
        U = (1 - mix) * U + mix * Unew
    return U, nl
