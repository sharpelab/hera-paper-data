# === SdH spot check H — hole side: n = -3.0e12, D = 0; B 0.7 -> 8 T ===
# Blocking rate-limited magnet -> uniform-B grid, Nyquist held at the low-B edge
# (sdh-spot-check recipe step 1b). Design numbers (step 2):
#   F_L = (h/4e)*3.0e16 = 31.0 T ;  D(1/B) = 1/(3 F_L) = 0.01074 1/T
#   dB = D(1/B) * B_lo^2 = 0.01074 * 0.49 = 5.26 mT ;  N = 1389
#   dF resolution (step 3): assuming onset ~1 T: dF = 1/(1/1 - 1/8) = 1.14 T
#     -> separates f_BL from F_L when ML fraction > ~7%; ABA small tone f_ML
#        at a few T resolvable against 0.

# -- preconditions (assumed, not set)
B = magnet.field()
Ts = T_sample()
print(f"precheck: B={B:+.4f} T (expect ~0), T={Ts:.3f} K")
assert abs(B) < 0.05, f"STOP: field not near zero: {B} T"
assert Ts < 1.5, f"STOP: not at base T: {Ts} K"

# -- drive & sensitivities (high-|n| metallic regime, device card + run-4 scales)
sr1.amplitude(2.0)   # 2 V / 100 MOhm = 20 nA bias
sr1.sensitivity(5e-5)   # Rxx ceiling 2.5 kOhm @ 20 nA; quantization ~0.08 Ohm
sr2.sensitivity(5e-5)
sr3.sensitivity(5e-5)   # Rxy(8 T, 3e12) = B/ne ~ 1.67 kOhm < 2.5 kOhm ceiling
sr0.sensitivity(5e-2)   # drain 20 nA x 1e6 = 20 mV
print(f"drive {sr1.amplitude()} V -> 20 nA; sens sr1/2/3 = 5e-5, sr0 = 5e-2")

# -- field-step dwell: settle_s = 1.2 s (= 4*tau lock-in floor; default 3 s is
#    a flat dwell on top of the ramp — 1.2 s serves both field settle and
#    filter settle after a 5 mT step). Stated bend, not a safety surface.
magnet.settle_s = 1.2

# -- gates to (n, D) = (-3.0e12, 0)
vtg_h, vbg_h = gates_for(-3.0, 0.0)
print(f"gates: Vtg={vtg_h:+.4f}, Vbg={vbg_h:+.4f}")

F_L = 31.02
d_invB = 1.0 / (3 * F_L)
B_LO, B_HI = 0.7, 8.0
dB = d_invB * B_LO**2
NPTS = int(np.floor((B_HI - B_LO) / dB)) + 1
B_vec = np.linspace(B_LO, B_HI, NPTS)
print(f"grid: {NPTS} pts, dB={dB*1e3:.2f} mT, uniform B ascending")

meas_config["comments"] = (
    "sdh-spot-check: hole side n=-3.0e12 cm^-2, D=0 "
    f"(Vtg={vtg_h:+.3f}, Vbg={vbg_h:+.3f}); B 0.7->8 T uniform, dB=5.26 mT "
    "(1/3-Nyquist on F_L=31 T at B_lo); 20 nA bias @ 13 Hz; settle_s=1.2"
)
s = sweep.AsyncStation(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment(f'(Vtg, Vbg) = ({vtg_h:.4f}, {vbg_h:.4f}), n = -3.0, D = 0')

s.ramp(k_2400_tg.volt, vtg_h)
s.ramp(k_2400_bg.volt, vbg_h)
s.ramp(magnet.field, B_LO)   # blocking ramp ~5 min from 0
interruptible_sleep(10)

s.fp(magnet.field)
s.fp(k_2400_tg.volt).fp(k_2400_tg.curr)
s.fp(k_2400_bg.volt).fp(k_2400_bg.curr)
s.fp(T_sample)
s.plot(magnet.field, k_2400_tg.curr)
s.plot(magnet.field, k_2400_bg.curr)
s.plot(magnet.field, T_sample)
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)
    s.plot(magnet.field, lia.X)

s.sweep(magnet.field, B_vec, delay=0)   # settle_s provides the post-step dwell
print(f"spot check H done; B at {magnet.field():+.3f} T (stay for cell E)")
