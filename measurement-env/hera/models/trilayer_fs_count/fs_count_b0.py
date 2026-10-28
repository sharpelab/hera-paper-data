#!/usr/bin/env python3
"""
B=0 Fermi-surface counting: ABA vs ABC trilayer graphene.

Tests the stacking-extraction premise (docs/stacking-extraction-survey.md):
  ABA -> >=2 distinct Fermi surfaces (ML Dirac + BL parabolic, coexisting)
  ABC -> 1 Fermi surface at high n (after the trigonal-warping Lifshitz cascade)

ABA: continuum 6-site SWMcC Hamiltonian, ll_spectrum.py's Datta params plus
     gamma4 = 0.04 eV per McCann-Koshino (Datta's fit carries no gamma4;
     Aaron's call 2026-07-18). gamma3 = 0 -> isotropic: only gamma3 breaks
     rotational symmetry, and it (like gamma4) acts on the BL sector alone,
     so the ML discriminator tone is exact either way.
ABC: MacDonald PRB 82,035409 (2010) effective 2-band model (Eq.6/7), with
     trigonal warping (gamma3) -> the 3-pocket->annulus->single cascade.
     E^+ (conduction) and E^- (valence) branches; the sign of the input
     density selects the side.

Counts distinct extremal-orbit frequencies F = (hbar/2 pi e) * A_k for both
carrier signs: n_target > 0 = electron doping, n_target < 0 = hole doping.
Solvers raise ValueError outside the solved density domain (never clamp);
the solved window covers at least |n| = 8e12 cm^-2 on both sides.
No external deps beyond numpy/scipy.
Run: uv run --no-project --with numpy --with scipy python3 fs_count_b0.py
"""
import numpy as np
import scipy.constants as cst
from scipy.ndimage import label

HBAR, E = cst.hbar, cst.e
A0 = 0.246e-9

def F_from_area(A_k):
    """Onsager frequency (Tesla) from a k-space area (1/m^2)."""
    return HBAR * A_k / (2 * np.pi * E)

def _interp_domain_checked(n_target, nvals, EFs, model):
    """np.interp with a loud out-of-domain failure instead of the silent clamp.
    nvals must be increasing; raises ValueError naming the covered range."""
    if not (nvals[0] <= n_target <= nvals[-1]):
        raise ValueError(
            f"{model}: requested n = {n_target:.3e} m^-2 is outside the solved "
            f"density domain [{nvals[0]:.3e}, {nvals[-1]:.3e}] m^-2 "
            f"(E_F/k grid limited) — extend the grids; do not clamp.")
    return np.interp(n_target, nvals, EFs)

# ---------------- ABA: continuum 6-site SWMcC ----------------
G0, G1, G2, G5, DELTA = 3.1, 0.39, -0.028, 0.01, 0.021   # eV (Datta)
G4 = 0.04    # eV, McCann-Koshino — BL-sector e-h mass asymmetry (not in Datta's fit)
VF = np.sqrt(3)/2 * A0 * (G0 * E) / HBAR                  # m/s

def H_aba(k, U=0.0):
    """6x6 ABA Hamiltonian (eV) at |k| (1/m), isotropic (g3=0; g4 kept — it
    preserves rotational symmetry and carries the BL-sector e-h asymmetry).
    Basis A1,B1,A2,B2,A3,B3. U = layer potential (eV) for displacement field."""
    w = HBAR * VF * k / E                                 # intralayer Dirac, eV
    w4 = np.sqrt(3)/2 * A0 * G4 * k                       # gamma4 interlayer, eV
    H = np.zeros((6, 6))
    # on-site: delta on dimers B1,A2,B3 ; layer potential +U,0,-U
    diag = np.array([0,0,0,0,0,0], float)
    for s in (1,2,5): diag[s] += DELTA
    for s in (0,1): diag[s] += U
    for s in (4,5): diag[s] -= U
    np.fill_diagonal(H, diag)
    # intralayer Dirac A_i-B_i
    for a,b in ((0,1),(2,3),(4,5)): H[a,b]=H[b,a]=w
    # interlayer constants
    for s1,s2,v in ((1,2,G1),(2,5,G1),(0,4,G2/2),(1,5,G5/2)): H[s1,s2]=H[s2,s1]=v
    # gamma4: adjacent-layer same-sublattice, -v4*pi alongside +v*pi (McCann-Koshino sign)
    for a,b in ((0,2),(1,3),(2,4),(3,5)): H[a,b]=H[b,a]=-w4
    return H

def aba_bands(kgrid, U=0.0):
    """Return E[band, k] for conduction-relevant bands (all 6)."""
    return np.array([np.linalg.eigvalsh(H_aba(k, U)) for k in kgrid]).T

def _aba_table(U, kmax, nk, ef_max, nef):
    """Solve the signed-density table n(E_F). Returns (kg, Eb, EFs, nvals).
    E_F rows whose Fermi contour would cross kmax (a band still on its occupied
    side at the grid edge while heading away from E_F) are dropped, so requests
    beyond the covered density raise instead of silently clamping."""
    kg = np.linspace(1e3, kmax, nk)
    Eb = aba_bands(kg, U)                                  # (6, nk) eV
    EFs = np.linspace(-ef_max, ef_max, nef)
    rising_edge = (Eb[:, -1] > Eb[:, -2])[:, None]
    occ_edge = Eb[:, -1][:, None] < EFs[None, :]
    EFs = EFs[~np.any(occ_edge == rising_edge, axis=0)]
    # signed density vs E_F: n(E_F) = sum_pockets +-kF^2/pi (g_s g_v = 4)
    def density(EF):
        tot = 0.0
        for b in range(6):
            cross = np.where((Eb[b,:-1]-EF)*(Eb[b,1:]-EF) < 0)[0]
            for c in cross:
                sgn = 1.0 if Eb[b,c+1] > Eb[b,c] else -1.0
                tot += sgn * kg[c]**2/np.pi
        return tot
    nvals = np.array([density(ef) for ef in EFs])
    return kg, Eb, EFs, nvals

def aba_fs(n_target, U=0.0, kmax=6e8, nk=6000, ef_max=0.25, nef=10001):
    """Find E_F for signed carrier density n_target (m^-2; >0 electrons, <0 holes);
    return (E_F, list of (F, kF) per Onsager orbit at E_F).

    Signed density over a symmetric E_F sweep: a rising band crossing is an
    electron pocket (occupied disk, +kF^2/pi), a falling crossing a hole pocket
    (empty disk, -kF^2/pi); g_s*g_v = 4. Annular pockets come out automatically
    as a falling+rising crossing pair. The orbit list carries every crossing —
    electron- and hole-like — with F positive and area-based; the sign of
    n_target selects the side. Raises ValueError outside the solved density
    domain (never clamps)."""
    kg, Eb, EFs, nvals = _aba_table(U, kmax, nk, ef_max, nef)
    EF = _interp_domain_checked(n_target, nvals, EFs, "ABA")
    # extract every Onsager orbit at EF
    fs = []
    for b in range(6):
        cross = np.where((Eb[b,:-1]-EF)*(Eb[b,1:]-EF) < 0)[0]
        for c in cross:
            kF = kg[c]
            fs.append((F_from_area(np.pi*kF**2), kF))
    return EF, sorted(fs)

def aba_mstar(n_target, U=0.0, kmax=6e8, nk=6000, ef_max=0.25, nef=10001):
    """Per-orbit cyclotron masses at signed density n_target: list of
    (F, m*/m_e) sorted by F — the same orbits, in the same order, as aba_fs.

    m* = (hbar^2/2pi) dA/dE, which for an isotropic band is hbar^2 kF/|dE/dk|
    evaluated at each Fermi crossing. m* is positive for electron- and
    hole-like orbits alike (carrier sign comes from n_target); it diverges if
    E_F sits exactly at a band extremum (dE/dk -> 0). Same domain rules as
    aba_fs (raises out of the solved range)."""
    kg, Eb, EFs, nvals = _aba_table(U, kmax, nk, ef_max, nef)
    EF = _interp_domain_checked(n_target, nvals, EFs, "ABA")
    out = []
    for b in range(6):
        cross = np.where((Eb[b,:-1]-EF)*(Eb[b,1:]-EF) < 0)[0]
        for c in cross:
            kF = kg[c]
            dEdk = abs(Eb[b,c+1] - Eb[b,c]) / (kg[c+1] - kg[c]) * E   # J*m
            out.append((F_from_area(np.pi*kF**2), HBAR**2 * kF / dEdk / cst.m_e))
    return sorted(out)

# ---------------- ABC: MacDonald effective 2-band ----------------
# Table I (ABC trilayer): gamma0 set to 3.16 to fix energy scale
G0c, G1c, G2c, G3c, G4c, DELTAc = 3.16, 0.502, -0.0171, -0.377, -0.099, -0.0014  # eV
def vi(g): return np.sqrt(3)/2 * A0 * (g*E)/HBAR
V0,V3,V4 = vi(G0c), vi(G3c), vi(G4c)

def E_abc(kx, ky, ud=0.0, band=+1):
    """ABC low-energy band energy (eV) at (kx,ky) from the two-band projection.
    band=+1 -> conduction E^+ (default); band=-1 -> valence E^-.
    ud = displacement (eV)."""
    p = HBAR*np.hypot(kx,ky)/E            # eV*s/m units folded: treat v*p in eV
    phi = np.arctan2(ky, kx)
    vp = V0*HBAR*np.hypot(kx,ky)/E        # v0*p in eV
    h_ch = vp**3 / G1c**2
    h_s  = DELTAc - 2*V0*V4*(HBAR*np.hypot(kx,ky)/E)**2/G1c
    h_tr = G2c/2 - 2*V0*V3*(HBAR*np.hypot(kx,ky)/E)**2/G1c
    h_gap = ud*(1 - (vp/G1c)**2)
    root = np.sqrt(h_ch**2 + h_tr**2 + h_gap**2 + 2*np.cos(3*phi)*h_ch*h_tr)
    return h_s + band*root

def _abc_table(band, ud, kmax, ng, nef):
    """Solve the ABC density table n(E_F) for one band branch.
    Returns (Egrid, dk, EFs, nvals). The E_F window stops where the Fermi
    contour would touch the grid-box edge, so requests beyond the covered
    density raise instead of silently clamping."""
    kx = np.linspace(-kmax, kmax, ng); KX,KY = np.meshgrid(kx, kx)
    Egrid = E_abc(KX, KY, ud, band=band)
    dk = kx[1]-kx[0]
    Esort = np.sort(Egrid.ravel())
    edge = np.concatenate([Egrid[0], Egrid[-1], Egrid[:,0], Egrid[:,-1]])
    # pocket area * (g/(2pi)^2) = |n| ; g=4
    if band > 0:
        # E_F from the band floor up to where the pocket touches the box edge
        EFs = np.linspace(Egrid.min(), edge.min(), nef)
        nvals = 4*(np.searchsorted(Esort, EFs)*dk*dk)/(2*np.pi)**2
    else:
        # hole side: E_F from where the hole pocket touches the edge to band top
        EFs = np.linspace(edge.max(), Egrid.max(), nef)
        nempty = Esort.size - np.searchsorted(Esort, EFs, side="right")
        nvals = -4*(nempty*dk*dk)/(2*np.pi)**2
    return Egrid, dk, EFs, nvals

def abc_fs(n_target, ud=0.0, kmax=6.5e8, ng=1301, nef=6000):
    """Count ABC FS topology + frequencies at signed density n_target (m^-2).
    n_target >= 0 fills the conduction band E^+ from the band floor;
    n_target < 0 fills the valence band E^- with holes from the band top
    (occupied/empty test and signs flipped; F stays positive/area-based).
    Raises ValueError outside the solved density domain (never clamps)."""
    band = 1 if n_target >= 0 else -1
    Egrid, dk, EFs, nvals = _abc_table(band, ud, kmax, ng, nef)
    ng = Egrid.shape[0]
    EF = _interp_domain_checked(n_target, nvals, EFs, "ABC")
    occ = (Egrid < EF) if band > 0 else (Egrid > EF)   # electron / hole pocket
    ncc, _ = label(occ)
    n_components = ncc.max()
    center_occ = occ[ng//2, ng//2]
    A_occ = occ.sum()*dk*dk
    # topology -> n distinct frequencies
    if center_occ and n_components == 1:
        topo, nfreq = "single", 1
    elif (not center_occ) and n_components == 1:
        topo, nfreq = "annulus", 2
    else:
        topo, nfreq = f"{n_components}-pocket", 1
    # representative frequency from total enclosed area (single pocket case)
    F_tot = F_from_area(A_occ)
    return EF, topo, n_components, nfreq, F_tot

def abc_mstar(n_target, ud=0.0, kmax=6.5e8, ng=1301, nef=6000, fit_mev=0.5):
    """Cyclotron mass at signed density n_target: returns (F_tot, m*/m_e).

    m* = (hbar^2/2pi) dA_tot/dE from the same density table as abc_fs:
    dA/dE = ((2pi)^2/g) dn/dE_F with g = 4, so m* = (pi/2) hbar^2 |dn/dE_F|.
    dn/dE_F is a linear fit over +-fit_mev around the solved E_F (smooths the
    pixel-count quantization). In the multi-pocket cascade region this is the
    mass summed over pockets; above the cascade it is the single pocket's
    cyclotron mass. Positive for both carrier signs. Same domain rules as
    abc_fs (raises out of the solved range)."""
    band = 1 if n_target >= 0 else -1
    Egrid, dk, EFs, nvals = _abc_table(band, ud, kmax, ng, nef)
    EF = _interp_domain_checked(n_target, nvals, EFs, "ABC")
    win = np.abs(EFs - EF) <= fit_mev * 1e-3
    if win.sum() < 10:
        raise ValueError(
            f"ABC: m* fit window (+-{fit_mev} meV) falls off the solved E_F table "
            f"at n = {n_target:.3e} m^-2 — too close to the domain edge.")
    slope = np.polyfit(EFs[win], nvals[win], 1)[0] / E      # m^-2 per J
    mstar = np.pi/2 * HBAR**2 * abs(slope) / cst.m_e
    occ = (Egrid < EF) if band > 0 else (Egrid > EF)
    return F_from_area(occ.sum()*dk*dk), mstar

# ---------------- run ----------------
if __name__ == "__main__":
    print(f"VF(ABA) = {VF:.3e} m/s ; v0(ABC) = {V0:.3e} m/s\n")
    F_L = lambda n: F_from_area((2*np.pi)**2 * abs(n) / 4)   # Luttinger (h/4e)|n|
    ns_e = np.array([0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0]) * 1e16   # m^-2
    ns_h = -np.array([0.5, 1.0, 2.0, 3.0, 6.0, 8.0]) * 1e16
    print("=== ABA (D=0) ===  n[1e12]  EF[meV]  #FS  frequencies[T] (sorted)   sum[T]  F_L[T]")
    for n in np.concatenate([ns_h[::-1], ns_e]):
        EF, fs = aba_fs(n)
        freqs = [F for F,_ in fs]
        fstr = ", ".join(f"{F:5.1f}" for F in freqs)
        print(f"   {n/1e16:5.2f}     {EF*1e3:6.1f}   {len(fs)}   [{fstr}]   {sum(freqs):5.1f}  {F_L(n):5.1f}")
    print("\n=== ABC (D=0) ===  n[1e12]  EF[meV]  topo        #cc  #freq  F_tot[T]  F_L[T]")
    for n in np.concatenate([ns_h[::-1], ns_e]):
        EF, topo, ncc, nfreq, Ft = abc_fs(n)
        print(f"   {n/1e16:5.2f}     {EF*1e3:6.1f}   {topo:10s}  {ncc}    {nfreq}     {Ft:5.1f}    {F_L(n):5.1f}")
    # D check for ABA at n=1e12: does the small ML pocket survive finite D?
    print("\n=== ABA at n=1e12, vs displacement U ===  U[meV]  #FS  frequencies[T]")
    for U in (0.0, 0.005, 0.010, 0.020, 0.040):
        EF, fs = aba_fs(1e16, U=U)
        print(f"   {U*1e3:5.0f}   {len(fs)}   [{', '.join(f'{F:.2f}' for F,_ in fs)}]")
    # cyclotron masses (the LK mass-labeling cross-check consumes these)
    print("\n=== m* (units m_e) ===  n[1e12]   ABA per-orbit (F[T], m*)              ABC (F_tot, m*)")
    for n in (-6e16, -3e16, -1e16, 1e16, 3e16, 6e16):
        astr = ", ".join(f"({F:5.1f}, {m:.4f})" for F, m in aba_mstar(n))
        Ft, mc = abc_mstar(n)
        print(f"   {n/1e16:+5.1f}   [{astr}]   ({Ft:5.1f}, {mc:.4f})")
    # out-of-domain must fail loudly, both signs, both models
    print("\n=== out-of-domain (must raise, not clamp) ===")
    for fn, n in ((aba_fs, 2e17), (aba_fs, -2e17), (abc_fs, 2e17), (abc_fs, -2e17)):
        try:
            fn(n)
            print(f"   {fn.__name__}({n:+.1e}): NO ERROR — BUG")
        except ValueError as e:
            print(f"   {fn.__name__}({n:+.1e}): ValueError ok — {e}")
