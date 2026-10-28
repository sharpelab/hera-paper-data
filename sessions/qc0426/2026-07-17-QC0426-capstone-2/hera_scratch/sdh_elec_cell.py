# === SdH spot check E — electron side: n = +3.0e12, D = 0; B 8 -> 0.7 T ===
# Same grid as run 5 reversed (never re-traverse; ends low for the fan).
# Sens change from H's read: sr1 -> 1e-4 (H hit 2.73 kOhm at 8 T, ~109% of
# the 2.5 kOhm nominal ceiling; descending hits high B first).

# -- preconditions (assumed, not set)
B = magnet.field()
Ts = T_sample()
print(f"precheck: B={B:+.3f} T (expect ~8), T={Ts:.3f} K")
assert abs(B - 8.0) < 0.1, f"STOP: field not at 8 T: {B} T"
assert Ts < 1.5, f"STOP: not at base T: {Ts} K"

sr1.sensitivity(1e-4)   # Rxx ceiling 5 kOhm @ 20 nA (H topped 2.73 kOhm)
print(f"sens: sr1 {sr1.sensitivity()}, sr2 {sr2.sensitivity()}, sr3 {sr3.sensitivity()}")

vtg_e, vbg_e = gates_for(+3.0, 0.0)
print(f"gates: Vtg={vtg_e:+.4f}, Vbg={vbg_e:+.4f}")

F_L = 31.02
d_invB = 1.0 / (3 * F_L)
B_LO, B_HI = 0.7, 8.0
dB = d_invB * B_LO**2
NPTS = int(np.floor((B_HI - B_LO) / dB)) + 1
B_vec = np.linspace(B_HI, B_LO, NPTS)   # descending
print(f"grid: {NPTS} pts, dB={dB*1e3:.2f} mT, uniform B descending")

meas_config["comments"] = (
    "sdh-spot-check: electron side n=+3.0e12 cm^-2, D=0 "
    f"(Vtg={vtg_e:+.3f}, Vbg={vbg_e:+.3f}); B 8->0.7 T uniform, dB=5.26 mT "
    "(1/3-Nyquist on F_L=31 T at B_lo); 20 nA bias @ 13 Hz; settle_s=1.2; "
    "sr1 sens 1e-4 after run-5 near-rail"
)
s = sweep.AsyncStation(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment(f'(Vtg, Vbg) = ({vtg_e:.4f}, {vbg_e:.4f}), n = +3.0, D = 0')

# gate switch at 8 T: hole point -> electron point through CNP, paced by
# volt.step (5 mV); stays inside validators the whole path
s.ramp(k_2400_tg.volt, vtg_e)
s.ramp(k_2400_bg.volt, vbg_e)
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

s.sweep(magnet.field, B_vec, delay=0)
print(f"spot check E done; B at {magnet.field():+.3f} T (low — fan-ready)")
