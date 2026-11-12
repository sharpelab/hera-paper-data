# === Step 1 (locate): constant-D n-linecuts to find the SC arc ===
# sc-characterization Step 1 "locate with linecuts first": the coarse map
# (data/4) gave cap ratio 1.183 + overview but cannot resolve the ~5e10 cm^-2
# proximity-SC arc (sub-pixel at 0.16 V steps). Fine n-linecuts at fixed D
# scan for a low-Rxx dip. Prior: holes->WSe2 favours one D sign (|D|>~0.5),
# n ~ -0.4..-0.6 e12 cm^-2; scan WIDER than that, and cover BOTH D signs
# because the D-sign convention is not yet physically anchored (D_offset=0).
from sharpelab_nb.gates import stack_capacitance, calc_nD, calc_gate_voltages

# --- preconditions (field still pristine; do NOT touch it) ---
print("T:", temperature(), "K  B:", magnet.field(), "T  gates:", k_tg.volt(), k_bg.volt())
assert temperature() < 0.060, "not at base T"
assert abs(magnet.field()) < 0.005, "field not near zero"

# calibration from data/4 CNP fit
c_tg = stack_capacitance([(23.6, 3)])
c_bg = c_tg * 1.1833                       # ratio data-calibrated (CNP slope)
n_off = -calc_nD(0.1634, 0.0, c_tg, c_bg)[0]   # CNP intercept -> n=0
print("c_tg=%.4e c_bg=%.4e n_off=%.4f" % (c_tg, c_bg, n_off))

# sensitivity: resolve a dip toward 0 across a ~0-200 ohm range (4T)
sr830_3.sensitivity(2e-5)                  # full-scale ~ 200 ohm at 1 nA, gain 100

n_vec = np.linspace(0.3, -1.5, 181)        # e12 cm^-2 (calc_nD units); wide of the -0.4..-0.6 prior
D_list = [-0.7, -0.6, -0.5, +0.5]          # V/nm; favoured (neg) side spans prior window + higher-n, +0.5 control

TG_MIN, TG_MAX = -7.0, 6.0
BG_MIN, BG_MAX = -4.0, 4.2

for D0 in D_list:
    Vtg, Vbg = calc_gate_voltages(n_vec, np.full_like(n_vec, D0), c_tg, c_bg, n_offset=n_off)
    inb = (Vtg >= TG_MIN) & (Vtg <= TG_MAX) & (Vbg >= BG_MIN) & (Vbg <= BG_MAX)
    vtg, vbg, nn = Vtg[inb], Vbg[inb], n_vec[inb]
    print("D=%+.2f: %d/%d pts in-box  Vtg[%.2f,%.2f] Vbg[%.2f,%.2f]  n[%.2f,%.2f]"
          % (D0, inb.sum(), len(n_vec), vtg.min(), vtg.max(), vbg.min(), vbg.max(), nn.min(), nn.max()))

    s = sweep.AsyncStation(meas_config)
    s.add_comment('cnp-and-dline-calibration')   # constant-D line designer (caps from CNP fit)
    s.add_comment(f'Step1 locate: constant-D n-linecut, D={D0:+.2f} V/nm')
    s.add_comment(f'n[{nn.min():+.2f},{nn.max():+.2f}] e12 cm^-2; caps ratio 1.183, n_off {n_off:.3f}, D_off 0')

    s.ramp(k_tg.volt, float(vtg[0]))
    s.ramp(k_bg.volt, float(vbg[0]))
    interruptable_sleep(5)

    s.fp(temperature)
    s.fp(k_tg.volt).fp(k_tg.curr)
    s.fp(k_bg.volt).fp(k_bg.curr)
    for lia in (sr830_1, sr830_2, sr830_3):
        s.fp(lia.X).fp(lia.P)
    s.plot(k_tg.volt, sr830_3.X)    # 4T Rxx vs the line
    s.plot(k_tg.volt, k_tg.curr)    # leakage

    s.multisweep([k_tg.volt, k_bg.volt], [vtg, vbg], delay=0.6)

# park gates (field untouched)
s.ramp(k_tg.volt, 0)
s.ramp(k_bg.volt, 0)
