"""Minimal tight-binding model of tetralayer graphene, ABAB / ABCA / ABCB, D = 0.
Per band: occupied k-area at the Fermi level -> SdH frequency F_i = n_i h / (4e), fraction F_i / F_L vs n.
Parameters (SWMcC-like, eV): g0 3.1, g1 0.38, g3 0.30, g4 0.14 (ABAB also g2 -0.02, g5 0.04 folded as nnn
vertical hops is omitted — this is a coarse model for design, not a fit).
Output: table of per-band fractions at the fan densities, plus m* (cyclotron mass from dA/dE)."""
import numpy as np, json

a = 0.246e-9; hbar = 1.0546e-34; e = 1.602e-19; h = 6.626e-34; me = 9.109e-31
g0, g1, g3, g4 = 3.1, 0.38, 0.30, 0.14
v0 = np.sqrt(3) / 2 * a * g0 * e / hbar; v3 = np.sqrt(3) / 2 * a * g3 * e / hbar; v4 = np.sqrt(3) / 2 * a * g4 * e / hbar

def H(kx, ky, stack):
    """4 layers x (A,B) basis. stack: string of positions per layer, e.g. 'ABAB'. Layer l sublattice A_l,B_l.
    Position letters: layer with 'A' has its A site over... use the standard rule: between consecutive layers,
    the dimer bond g1 couples the pair of sites that sit on top of each other."""
    pi = hbar * (kx + 1j * ky) / e  # eV*s/m * 1/m -> scaled below
    p = v0 * hbar * (kx + 1j * ky) / e  # energy units eV (v0*hbar*k/e)
    p3 = v3 * hbar * (kx - 1j * ky) / e
    p4 = v4 * hbar * (kx + 1j * ky) / e
    N = 4; Hm = np.zeros((2 * N, 2 * N), complex)
    for l in range(N):
        Hm[2 * l, 2 * l + 1] = p.conjugate(); Hm[2 * l + 1, 2 * l] = p
    # stacking: each layer described by offset s in {0,1,2} (A=0,B=1,C=2). Site A_l at s_l, B_l at s_l+1 (mod 3).
    off = {"A": 0, "B": 1, "C": 2}
    s = [off[c] for c in stack]
    for l in range(N - 1):
        # positions of sites
        posA1, posB1 = s[l] % 3, (s[l] + 1) % 3
        posA2, posB2 = s[l + 1] % 3, (s[l + 1] + 1) % 3
        i1 = {posA1: 2 * l, posB1: 2 * l + 1}; i2 = {posA2: 2 * l + 2, posB2: 2 * l + 3}
        common = set(i1) & set(i2)
        assert len(common) == 1, stack
        c = common.pop()
        d1, d2 = i1[c], i2[c]          # dimer sites
        n1 = [x for x in i1.values() if x != d1][0]; n2 = [x for x in i2.values() if x != d2][0]  # non-dimer
        Hm[d1, d2] += g1; Hm[d2, d1] += g1
        # skew g3 between the two non-dimer sites (hop direction sign convention approximate)
        Hm[n1, n2] += p3 if (s[l + 1] - s[l]) % 3 == 1 else p3.conjugate()
        Hm[n2, n1] += np.conj(Hm[n1, n2])
        # g4 dimer<->non-dimer (approximate)
        Hm[d1, n2] += p4; Hm[n2, d1] += np.conj(p4)
        Hm[n1, d2] += p4; Hm[d2, n1] += np.conj(p4)
    return Hm

def bands(stack, kmax=0.35e9, nk=241):
    k = np.linspace(-kmax, kmax, nk); KX, KY = np.meshgrid(k, k)
    E = np.zeros((nk, nk, 8))
    for i in range(nk):
        for j in range(nk):
            E[i, j] = np.linalg.eigvalsh(H(KX[i, j], KY[i, j], stack))
    dk2 = (k[1] - k[0]) ** 2
    return E, dk2

def analyze(stack, dens):
    E, dk2 = bands(stack)
    # density vs E: electron side count states above 0 in bands 4..7 below E; hole side similarly
    g = 4 / (2 * np.pi) ** 2 * dk2 * 1e-16  # per k-cell, in 1e12 cm^-2... (m^-2 -> 1e12 cm^-2 is 1e-16)
    out = {}
    Es = np.linspace(0, 0.25, 1001)
    for n in dens:
        sign = np.sign(n)
        if sign > 0:
            bs = [4, 5, 6, 7]; occ = lambda Ef: [g * np.sum(E[:, :, b] < Ef) - (g * np.sum(E[:, :, b] < 0)) for b in bs]
            # simpler: electrons in band b = count(0<E_b<Ef) for conduction bands
            nb = lambda Ef: [g * np.sum((E[:, :, b] < Ef) & (E[:, :, b] > -1)) - g * np.sum(E[:, :, b] < 0) for b in bs]
            tot = lambda Ef: sum(nb(Ef)) - sum(g * np.sum(E[:, :, b] < 0) * 0 for b in bs)
        # generic: n(Ef) = sum_b [count(E_b < Ef) - count(E_b < E_cnp)] with E_cnp from neutrality
        pass
    return out

def fermi_table(stack, dens):
    E, dk2 = bands(stack)
    g = 4 / (2 * np.pi) ** 2 * dk2 * 1e-16
    flat = E.reshape(-1, 8)
    # neutrality: 4 bands filled -> find E0 such that total count below E0 = 4*Nk
    Nk = flat.shape[0]
    allE = np.sort(flat.ravel()); E0 = 0.5 * (allE[4 * Nk - 1] + allE[4 * Nk])
    def n_of(Ef):
        per = [(np.sum(flat[:, b] < Ef) - np.sum(flat[:, b] < E0)) * g for b in range(8)]
        return sum(per), per
    rows = []
    for n in dens:
        lo, hi = (E0, E0 + 0.4) if n > 0 else (E0 - 0.4, E0)
        for _ in range(50):
            mid = 0.5 * (lo + hi); t, _ = n_of(mid)
            if (t < n): lo = mid
            else: hi = mid
        t, per = n_of(mid)
        # per-band carriers: for n>0 electron pockets = positive counts in bands; for n<0 holes = -counts
        pk = [abs(p) for p in per if abs(p) > 0.004 * abs(n)]
        # m* per band: dn_b/dE * pi hbar^2 / (2 * me) ... n_b = g_s g_v m A/(2 pi hbar^2)*E => m = (2 pi hbar^2/4) dn/dE
        dE = 0.002
        _, perp = n_of(mid + dE); _, perm = n_of(mid - dE)
        ms = []
        for b in range(8):
            if abs(per[b]) > 0.004 * abs(n):
                dndE = abs(perp[b] - perm[b]) / (2 * dE) * 1e16 / e  # m^-2 per J
                ms.append(round(2 * np.pi * hbar ** 2 / 4 * dndE / me, 3))
        rows.append(dict(n=n, Ef_meV=round(1e3 * (mid - E0), 1), frac=[round(p / abs(n), 3) for p in pk], mstar=ms))
    return rows

if __name__ == "__main__":
    dens = [-1.2, -0.6, -0.3, 0.3, 0.6, 1.2, 2.0, 3.2]
    res = {}
    for st in ["ABAB", "ABCA", "ABCB"]:
        res[st] = fermi_table(st, dens)
        print(st)
        for r in res[st]:
            print(f"  n={r['n']:+.1f}  Ef={r['Ef_meV']:+6.1f} meV  band fractions {r['frac']}  m*/me {r['mstar']}")
    json.dump(res, open("hera_scratch/tb_model.json", "w"), indent=1)
