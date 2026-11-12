"""Fan design numbers: model F(n) (SI units), e-side light-tone SNR at the record edge, grid + price."""
import numpy as np, sys, warnings
from hera.analysis import open_run, sdh_onset, field_invB, luttinger_frequency
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M

print("=== model F(n) electron side, n in m^-2 ===")
for n in (0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.2, 3.25):
    FL = luttinger_frequency(n * 1e16)
    ab = M.abab_fs(n * 1e16)[1]; mm = M.abab_mstar(n * 1e16)
    ac = M.abca_fs(n * 1e16); acm = M.abca_mstar(n * 1e16)
    print(f"  n={n:.2f}: F_L={FL:5.1f} | ABAB F={[round(f,1) for f,_ in ab]} frac={[round(f/FL,2) for f,_ in ab]} m*={[round(m,3) for _,m in mm]} | ABCA F={ac[4]:.1f} ({ac[1]}) m*={acm[1]:.3f}")
for n in (-1.0, -1.2):
    FL = luttinger_frequency(abs(n) * 1e16); ab = M.abab_fs(n * 1e16)[1]; mm = M.abab_mstar(n * 1e16)
    print(f"  n={n:.2f}: F_L={FL:5.1f} | ABAB F={[round(f,1) for f,_ in ab]} m*={[round(m,3) for _,m in mm]}")

print("\n=== run 6 light tone track on the usable record (b_lo = 1.0) ===")
run = open_run("data/6"); B = run.col("magnet_field"); R = run.col("sr1_X") / (run.col("sr0_X") / -1e6)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    on = sdh_onset(R, B, b_lo=1.0, r_full_scale=50e-6 / 9.9e-9)
t = on.tones[0]; print(f"  tone {t.freq:.2f} T: b_centers {np.round(t.b_centers,2)} snr {np.round(t.snr,1)}")
for t in on.tones[1:4]: print(f"  tone {t.freq:.2f} T: onset {t.onset_b:.2f}; b_centers {np.round(t.b_centers[-4:],2)} snr {np.round(t.snr[-4:],1)}")

print("\n=== grid ===")
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
F_MAX = 34.0; B_LO, B_HI = 0.7, 8.0
dinvB = 1 / (3 * F_MAX)
N_B = int(np.ceil((1 / B_LO - 1 / B_HI) / dinvB)) + 1
B_vec = field_invB(B_LO, B_HI, N_B)
print(f"  d(1/B) = {dinvB:.4f} 1/T -> N_B = {N_B}; B steps: first {B_vec[1]-B_vec[0]:.4f} T, last {B_vec[-1]-B_vec[-2]:.3f} T; pts/period at F=34: {1/(dinvB*34):.2f}; Nyquist F = {1/(2*dinvB):.1f} T")
n_hi, n_lo = 3.25, 1.0
dn_ray = 4 * 2.418e10 * B_LO / 1e12   # 1e12 cm^-2 per ray at B_LO
N_n = int(np.ceil((n_hi - n_lo) / (dn_ray / 2))) + 1
ns = np.linspace(n_hi, n_lo, N_n); Ds = np.zeros_like(ns)
Vt, Vb = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"  ray spacing at B_lo: {dn_ray:.4f}e12 -> N_n = {N_n} (dn = {(n_hi-n_lo)/(N_n-1):.4f}e12, {dn_ray/((n_hi-n_lo)/(N_n-1)):.2f} per ray)")
print(f"  Vtg {Vt.min():+.4f}..{Vt.max():+.4f} (lim -0.3/+1.0), Vbg {Vb.min():+.4f}..{Vb.max():+.4f} (lim -1.3/+2.0); retrace TG {np.ptp(Vt):.3f} V, BG {np.ptp(Vb):.3f} V -> flyback ~{(np.ptp(Vt)+np.ptp(Vb))/0.005*0.006:.1f} s")
print(f"  roundtrip endpoints n,D: {calc_nD(Vt[0],Vb[0],**CAL)}, {calc_nD(Vt[-1],Vb[-1],**CAL)}")
# price (run 5: 1.098 s/pt at fast_delay 1.0 -> 0.1 s read overhead; 5.8 s row turnaround at slow_delay 3; runs 6/7: 3.08 s per field step beyond the bare ramp)
for fd in (1.2, 1.8):
    t_pts = N_B * N_n * (fd + 0.10); t_rows = N_B * (5.8 + 3.1); t_ramp = (B_HI - B_LO) / 0.137 * 60 + B_LO / 0.137 * 60
    tot = t_pts + t_rows + t_ramp
    print(f"  fast_delay {fd}: points {t_pts/3600:.2f} h + rows {t_rows/3600:.2f} h + ramps {t_ramp/3600:.2f} h = {tot/3600:.2f} h  (+10% -> {1.1*tot/3600:.2f} h); row period ~{(N_n*(fd+0.1)+8.9):.0f} s + ramp")
# partner-tone period count at the low-n edge, with scale 0.91
for n in (1.0, 1.5, 2.0, 2.5):
    f_light = 0.23 * luttinger_frequency(n * 1e16) * 0.91
    print(f"  n={n}: light tone ~{f_light:.1f} T -> periods in [{B_LO},{B_HI}] = {f_light*(1/B_LO-1/B_HI):.1f}; dF = {1/(1/B_LO-1/B_HI):.2f} T")
print(f"  nu ladder: nu=8 at B_HI covers n <= {8*2.418e10*B_HI/1e12:.2f}e12; nu=12: n <= {12*2.418e10*B_HI/1e12:.2f}; nu=16: n <= {16*2.418e10*B_HI/1e12:.2f}")
