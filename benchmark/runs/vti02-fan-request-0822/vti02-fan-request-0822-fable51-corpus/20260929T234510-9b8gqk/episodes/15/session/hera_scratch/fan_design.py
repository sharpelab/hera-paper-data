"""Fan design numbers (landau-fan step 1/2 + investigation step 2) from the spot checks + model.
Also: run-6 onset restricted to the 10 mT segment; run-7 FFT peaks with |F_L| (bugfix)."""
import sys, json, warnings
import numpy as np
import scipy.constants as cst
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M
from sharpelab_nb.gates import calc_gate_voltages

DATA = "/home/hera/measurements/zack/20260822-vti-02/data"
FL = lambda n12: cst.h / (4 * cst.e) * abs(n12) * 1e16
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

def load(rid):
    r = open_run(f"{DATA}/{rid}"); B = r.col("magnet_field"); R = r.col("sr1_X") / (r.col("sr0_X") / -1e6)
    o = np.argsort(B); return B[o], R[o]

# --- run 6 onset on the 10 mT segment only ---
B6, R6 = load(6)
for blo in (1.0, 1.2):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R6, B6, b_lo=blo, r_full_scale=5000)
            print(f"--- run 6 sdh_onset b_lo={blo}: onset_b {on.onset_b:.2f} T (tone {on.onset_freq:.1f})")
            print(on.summary())
        except SdhOnsetError as e:
            print("SdhOnsetError", e)
        for ww in w: print("  warn:", str(ww.message)[:200])
# light-tone visibility by eye: bg-subtracted amplitude envelope in 1-3 T
m = (B6 >= 1.0) & (B6 <= 4.0); cf = np.polyfit(B6[m], R6[m], 5); dR = R6[m] - np.polyval(cf, B6[m])
for a, b in [(1.0, 1.3), (1.3, 1.6), (1.6, 2.0), (2.0, 2.5), (2.5, 3.0), (3.0, 4.0)]:
    s = (B6[m] >= a) & (B6[m] < b); print(f"  run6 dR rms in [{a},{b}] T: {np.std(dR[s]):.2f} Ohm (ptp {np.ptp(dR[s]):.1f})")

# --- run 7 FFT peaks with |F_L| ---
B7, R7 = load(7); fl7 = FL(-1.2)
for (a, b) in [(0.72, 10.0), (0.72, 4.0), (1.2, 6.0), (3.0, 10.0)]:
    f, sp = sdh_fft(R7[:, None], B7, b_range=(a, b), bg_degree=5, log=False, nfft=2048)
    s = sp[0] / sp[0][f > 2].max(); sel = (f > 1.5) & (f < 5 * fl7)
    pk, _ = find_peaks(s[sel], prominence=0.08)
    print(f"run 7 FFT [{a},{b}] dF={1/(1/a-1/b):.2f}: " + ", ".join(f"{x:.1f}T({y:.2f})" for x, y in zip(f[sel][pk], s[sel][pk])))
# LL filling of the run-7 minima under the run-5 calibration
mins7 = np.array([0.84, 0.96, 1.12, 1.34, 1.7, 2.04, 2.76, 3.4, 4.14, 4.94, 6.04, 6.94, 8.4, 9.12])
print("run 7 minima nu = 4 F_L / B:", np.round(4 * fl7 / mins7, 1).tolist())
# same for run 6 deep minima
fl6 = FL(3.2); print("run 6 F_L", round(fl6, 2), "nu at 6.0/7.2/9.9 T:", np.round(4 * fl6 / np.array([6.0, 7.2, 9.9]), 1).tolist())

# --- model table across the electron fan window ---
print("\n--- model F(n), m*(n) electron side (u_D = 0) ---")
print(" n12 |  F_L  | ABAB light, heavy (T) | m* light, heavy | heavy/F_L | ABCA F, m*")
rows = []
for n12 in [1.0, 1.5, 2.0, 2.5, 3.0, 3.27]:
    n = n12 * 1e16
    EF, orbs = M.abab_fs(n); ms = M.abab_mstar(n)
    Fa = [o[0] for o in orbs]; ma = [x[1] for x in ms]
    EFc, topo, ncomp, nfreq, Fc = M.abca_fs(n); Fct, mc = M.abca_mstar(n)
    rows.append((n12, FL(n12), Fa, ma, Fc, mc))
    print(f"{n12:4.2f} | {FL(n12):5.1f} | {', '.join(f'{x:5.1f}' for x in Fa)} | {', '.join(f'{x:.3f}' for x in ma)} | {max(Fa)/FL(n12):.3f} | {Fc:5.1f}, {mc:.3f} ({topo})")
# LK thermal factor at T_e for the key tones at a few B
def lk(m, T, B): x = 2 * np.pi**2 * cst.k * T * m * cst.m_e / (cst.hbar * cst.e * B); return x / np.sinh(x)
for Te in (1.2, 4.0, 8.0):
    print(f"T_e={Te} K: light m*0.028 @1/1.5/2 T: {lk(0.028,Te,1):.2f}/{lk(0.028,Te,1.5):.2f}/{lk(0.028,Te,2):.2f}; heavy m*0.061 @2/3/4 T: {lk(0.061,Te,2):.2f}/{lk(0.061,Te,3):.2f}/{lk(0.061,Te,4):.2f}; ABCA m*0.075 @2/3/4: {lk(0.075,Te,2):.2f}/{lk(0.075,Te,3):.2f}/{lk(0.075,Te,4):.2f}")

# --- fan design ---
print("\n--- fan design (electron side, D = 0) ---")
n_lo, n_hi = 1.0, 3.27
Vt, Vb = calc_gate_voltages(np.array([n_lo, n_hi]), np.zeros(2), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"n {n_lo}..{n_hi}: Vtg {Vt[0]:+.4f}..{Vt[1]:+.4f}, Vbg {Vb[0]:+.4f}..{Vb[1]:+.4f}")
Flmax = FL(n_hi); B_hi = 10.0
for B_lo in (0.8, 1.0, 1.2, 1.5):
    for nyq in (3, 4):
        d = 1 / (nyq * Flmax); NB = int(np.ceil((1 / B_lo - 1 / B_hi) / d)) + 1
        dn_ray = 4 * cst.e / cst.h * B_lo * 1e-16  # 1e12 cm^-2 per LL ray at B_lo
        Nn2 = int(np.ceil((n_hi - n_lo) / (dn_ray / 2))) + 1
        dF = 1 / (1 / B_lo - 1 / B_hi)
        # partner-tone 5-period floor: the light tone at density n has F_light(n) (model); need 1/B_lo-1/B_hi >= 5/F
        Fl_needed = 5 / (1 / B_lo - 1 / B_hi)
        n_partner_ok = [r[0] for r in rows if min(r[2]) >= Fl_needed]
        print(f"B_lo {B_lo} T, Nyq 1/{nyq}: d(1/B) {d:.5f} (dB {d*B_lo**2*1e3:.1f} mT at B_lo, {d*B_hi**2:.2f} T at top), N_B {NB}; ray dn {dn_ray:.3f}e12 -> N_n>= {Nn2}; dF {dF:.2f} T; "
              f"5-period floor F>= {Fl_needed:.1f} T -> partner resolvable from n >= {min(n_partner_ok) if n_partner_ok else 'none'}")
# cost model: bare traverse + rows x (settle 3 s + N_n x per_pt + flyback ~1 s + slow_delay)
for B_lo, NB, Nn, per_pt, sd in [(1.0, 109, 51, 1.1, 1.0), (1.0, 109, 61, 1.1, 1.0), (1.2, 100, 51, 1.1, 1.0), (1.0, 109, 51, 2.1, 1.0), (0.8, 148, 61, 1.1, 1.0)]:
    trav = (B_hi - B_lo) / 0.137
    grid = NB * (3.0 + Nn * per_pt + 1.0 + sd) / 60
    print(f"B_lo {B_lo}: N_B {NB} x N_n {Nn} @ {per_pt} s/pt: traverse {trav:.0f} min + grid {grid:.0f} min = {(trav+grid)/60:.1f} h (+10% -> {(trav+grid)*1.1/60:.1f} h); pts {NB*Nn}")
# dynamic range: worst corner low n x high B; run 6 max 530 Ohm at n=3.2; CNP-side R at 10 T (run 7, n=-1.2) 590 Ohm
print("R max seen: run6 530 Ohm (n=+3.2, 8.8 T); run7 587 Ohm (n=-1.2, 10 T); at n=+1.0 expect R(0)~100-150 Ohm x MR; 50 uV = 5 kOhm FS; 100 uV = 10 kOhm FS")
