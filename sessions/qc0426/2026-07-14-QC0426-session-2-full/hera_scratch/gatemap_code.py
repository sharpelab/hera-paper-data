# === Step 1: 0 T gate map — TG fast (121 pts, -3..+3), BG slow (61 rows, -3..+3) ===
_T = T_sample(); _B = magnet.field()
print(f"precheck: T={_T:.3f} K (<2), B={_B:+.4f} T (~0), Vtg={k_tg.volt():+.3f}, "
      f"Vbg={k_bg.volt():+.3f}, Vsi={dc205.voltage():+.3f} (all ~0)")
assert _T < 2.0 and abs(_B) < 0.05
assert abs(k_tg.volt()) < 1e-3 and abs(k_bg.volt()) < 1e-3 and abs(dc205.voltage()) < 1e-3

# sr0 headroom: 5 nA x 1 MOhm = 5 mV sits at 99.7% of the 5 mV range -> 10 mV
sr0.sensitivity(10e-3)

vtg_fast = np.linspace(-3.0, 3.0, 121)   # 50 mV step, inside validators
vbg_slow = np.linspace(-3.0, 3.0, 61)    # 0.1 V step, ridge in-window to |Vbg|~2.7

s = sweep.AsyncStation(meas_config)
s.add_comment('gatemap')
s.add_comment(f'TG fast -3..+3 (121 pts), BG slow -3..+3 (61 rows), Vsi=0, B=0, '
              f'T={_T:.2f} K, I_bias=5 nA, sens sr1-3 2e-5 / sr0 1e-2, fast_delay=1.2 (4 tau)')

s.ramp(k_tg.volt, vtg_fast[0])
s.ramp(k_bg.volt, vbg_slow[0])

s.fp(T_sample)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
s.plot(k_tg.volt, k_tg.curr)      # live leakage, swept gate
s.plot('time', k_bg.curr)         # live leakage, stepped gate
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)
    s.plot(k_tg.volt, lia.X)

try:
    s.megasweep(k_bg.volt, vbg_slow, k_tg.volt, vtg_fast,
                slow_delay=3, fast_delay=1.2)
finally:
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
print("gatemap done; gates parked at 0")
