"""Landau-fan design check: grid, validator headroom, Nyquist/resolution, price."""
import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB, luttinger_frequency

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX = -0.3, 1.0
BG_MIN, BG_MAX = -1.3, 2.0

N_FAST, N_ROWS = 177, 71
n_vec = np.linspace(-1.20, 3.20, N_FAST)          # 1e12 cm^-2, D = 0 line
Vtg, Vbg = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
B_vec = field_invB(1.0, 10.0, N_ROWS)             # ascending, uniform in 1/B

print(f"n: {n_vec[0]:+.3f} .. {n_vec[-1]:+.3f} e12, dn = {np.diff(n_vec)[0]*1000:.1f} e9 cm^-2, {N_FAST} pts")
print(f"Vtg: {Vtg.min():+.4f} .. {Vtg.max():+.4f} V  (limits {TG_MIN}, {TG_MAX}; margin {Vtg.min()-TG_MIN:+.4f} / {TG_MAX-Vtg.max():+.4f})")
print(f"Vbg: {Vbg.min():+.4f} .. {Vbg.max():+.4f} V  (limits {BG_MIN}, {BG_MAX}; margin {Vbg.min()-BG_MIN:+.4f} / {BG_MAX-Vbg.max():+.4f})")
nn, DD = calc_nD(Vtg, Vbg, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"roundtrip: max|dn| {np.abs(nn-n_vec).max():.2e} e12, D = {np.min(DD):+.5f}..{np.max(DD):+.5f} V/nm")
print(f"dVtg/step = {np.diff(Vtg)[0]*1000:.2f} mV (Keithley step 5 mV -> {np.diff(Vtg)[0]/0.005:.1f} sub-steps/pt)")
print(f"dVbg/step = {np.diff(Vbg)[0]*1000:.2f} mV")

inv = 1 / B_vec
print(f"\nB: {B_vec[0]:.3f} .. {B_vec[-1]:.3f} T, {N_ROWS} rows; 1/B span {inv.min():.4f}..{inv.max():.4f}")
d_inv = np.abs(np.diff(inv))
print(f"  d(1/B) = {d_inv.mean():.5f} (spread {d_inv.min():.5f}..{d_inv.max():.5f}) -> F_Nyquist = {1/(2*d_inv.max()):.1f} T")
print(f"  FFT resolution dF = {1/(inv.max()-inv.min()):.2f} T")
print(f"  dB per row: {np.diff(B_vec).min()*1000:.0f} .. {np.diff(B_vec).max()*1000:.0f} mT")

# Onsager expectations along the line (single 4-fold FS carrying full n)
for nx in (-1.2, -0.6, 1.0, 2.0, 3.2):
    F = luttinger_frequency(nx * 1e16)
    print(f"  n = {nx:+.2f}e12 -> F_full = {F:.1f} T ; nu at 10 T = {4*F/10:.1f}, at 1 T = {4*F/1:.0f}")

# n-resolution vs LL spacing
for B in (1.0, 2.0, 5.0, 10.0):
    dn4 = 4 * 1.602176634e-19 * B / 6.62607015e-34 * 1e-16   # e12 cm^-2 per 4-fold gap
    print(f"  B = {B:4.1f} T: 4-fold LL spacing {dn4:.4f}e12 -> {dn4/np.diff(n_vec)[0]:.1f} pts/gap; "
          f"1-fold {dn4/4:.4f}e12 -> {dn4/4/np.diff(n_vec)[0]:.1f} pts")

# --- price (calibrated on run 5: 4158 pts / 4873 s = 1.172 s/pt at fast_delay = 1.0) ---
PT = 1.172
ramp_s = (B_vec[-1] - B_vec[0]) / 0.137 * 60
settle_s = 3.0 * N_ROWS
flyback_s = ((Vtg.max() - Vtg.min()) + (Vbg.max() - Vbg.min())) / 0.005 * 0.006
slow_delay = 3.0
row_s = N_FAST * PT + flyback_s + slow_delay
tot = ramp_s + settle_s + N_ROWS * row_s
print(f"\nprice: flyback {flyback_s:.1f} s/row, row {row_s:.0f} s, ramp {ramp_s/60:.0f} min, settle {settle_s/60:.1f} min")
print(f"  total = {tot/3600:.2f} h  (+8%% overrun -> {tot*1.08/3600:.2f} h) ; {N_ROWS*N_FAST} points")
