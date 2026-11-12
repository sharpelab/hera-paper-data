"""Fan fast-axis (n-line at D=0) + dynamic-range sizing + final grid/cost."""
import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import open_run, field_invB

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX = -0.3, 1.0
BG_MIN, BG_MAX = -1.3, 2.0

# --- where does the D=0 line hit the TG ceiling? ---
for n in np.arange(3.15, 3.35, 0.01):
    vtg, vbg = calc_gate_voltages(n, 0.0, **CAL)
    if vtg > TG_MAX - 0.005:
        print(f"TG ceiling: n={n:.3f}e12 -> Vtg={vtg:+.4f} (limit {TG_MAX}) -- stop here"); break
    last = (n, vtg, vbg)
print(f"highest n with >=5 mV TG margin: n={last[0]:.3f}e12 -> (Vtg,Vbg)=({last[1]:+.4f},{last[2]:+.4f})")

N_LO, N_HI = 2.00, 3.25
B_LO, B_HI = 0.65, 10.0
DINVB = 0.010
N_B = int(np.ceil((1/B_LO - 1/B_HI)/DINVB)) + 1
h, e = 6.62607015e-34, 1.602176634e-19
dn_ray = 4*(e/h)*B_LO/1e16
N_N = int(np.ceil((N_HI-N_LO)/(dn_ray/2))) + 1
print(f"\ngrid: N_B={N_B} (d(1/B)={((1/B_LO-1/B_HI)/(N_B-1)):.5f} 1/T), N_N={N_N} "
      f"(dn={(N_HI-N_LO)/(N_N-1):.4f}e12 vs ray/2={dn_ray/2:.4f}e12 at {B_LO} T)")

ns = np.linspace(N_LO, N_HI, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, 0.0, **CAL)
print(f"n-line: {ns[0]:.3f} -> {ns[-1]:.3f} e12; Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f}; Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f}")
print(f"validators ok: {Vtgs.min()>=TG_MIN and Vtgs.max()<=TG_MAX and Vbgs.min()>=BG_MIN and Vbgs.max()<=BG_MAX}")
print(f"TG margin to limit: {TG_MAX-Vtgs.max()*1:.4f} V; roundtrip n,D at ends: "
      f"{calc_nD(Vtgs[0],Vbgs[0],**CAL)} / {calc_nD(Vtgs[-1],Vbgs[-1],**CAL)}")
B_vec = field_invB(B_LO, B_HI, N_B)
print(f"B_vec: {B_vec[0]:.4f} -> {B_vec[-1]:.4f} T, {len(B_vec)} rows; "
      f"dB first {np.diff(B_vec)[0]*1e3:.1f} mT, last {np.diff(B_vec)[-1]*1e3:.0f} mT")
print(f"rows below 2 T: {(B_vec<2).sum()}; d(1/B) spread {np.ptp(np.diff(1/B_vec)):.2e}")

# --- dynamic range: R along D=0 at B=0 from run 5 gatemap ---
r5 = open_run("/home/hera/measurements/zack/20260822-vti-02/data/5")
vtg5, vbg5 = r5.col("k_2400_tg_volt"), r5.col("k_2400_bg_volt")
R5 = np.abs((r5.col("sr1_X")/1.0)/(r5.col("sr0_X")/-1e6))
n5, D5 = calc_nD(vtg5, vbg5, **CAL)
sel = np.abs(D5) < 0.012
print("\nR(n) along D=0 at B=0 (run 5):")
for lo in np.arange(1.8, 3.4, 0.2):
    m = sel & (n5 >= lo) & (n5 < lo+0.2)
    if m.sum(): print(f"  n {lo:.1f}-{lo+0.2:.1f}e12: R = {np.median(R5[m]):6.1f} Ohm  (N={m.sum()})")

# MR factors measured this session
for fid, lbl in ((6, "n=+3.2e12"), (7, "n=-1.2e12")):
    r = open_run(f"/home/hera/measurements/zack/20260822-vti-02/data/{fid}")
    B = r.col("magnet_field"); R = np.abs((r.col("sr1_X")/1.0)/(r.col("sr0_X")/-1e6))
    o = np.argsort(B); B, R = B[o], R[o]
    r0 = np.median(R[B < 0.15]) if (B < 0.15).sum() else np.median(R[:5])
    print(f"run {fid} {lbl}: R(B~0)={r0:.1f}, R(10T)={np.median(R[B>9.8]):.1f} -> MR x{np.median(R[B>9.8])/r0:.1f}")

R_LOWN_B0 = 95.0   # filled from the table above at n=2.0e12
for mr in (10, 15, 20):
    print(f"  worst corner estimate at MR x{mr}: R={R_LOWN_B0*mr:.0f} Ohm = {R_LOWN_B0*mr/5000*100:.0f}% of 50 uV FS (5 kOhm @ 10 nA)")

# --- cost ---
FAST_DELAY, OVH = 2.1, 0.098
SLOW_DELAY = 1.0
t_grid = N_B*N_N*(FAST_DELAY+OVH)
flyback = (Vtgs.max()-Vtgs.min())/0.005*0.006          # TG steps home at volt.step 5 mV, 6 ms/write
t_rows = N_B*(3.0 + SLOW_DELAY + flyback)               # 3 s magnet driver settle + slow_delay + flyback
t_trav = (B_HI-B_LO)/0.137*60
print(f"\ncost: grid {t_grid/3600:.2f} h + rows {t_rows/3600:.2f} h (flyback {flyback:.2f} s/row) + traverse {t_trav/3600:.2f} h")
print(f"  total = {(t_grid+t_rows+t_trav)/3600:.2f} h  (+10% session-evidence margin = {(t_grid+t_rows+t_trav)*1.10/3600:.2f} h)")
print(f"  pts = {N_B*N_N}")
