# === Liveness discriminators: is the 90 pA even device current? ===
# R_SD ~ 109 MOhm is flat vs TG (+/-0.8), BG (+/-5), Si (+/-20) — total gate-
# flatness suggests a fixed parasitic S-D path with the device open/blocking.
# Test 1: frequency scaling (capacitive path: |I| ~ f; resistive: flat).
# Test 2: drive-amplitude linearity + headroom for a high-drive BG look.
# All settings restored at the end; no run dir (point reads, printed).

_T = T_sample()
print(f"preconditions: T={_T:.3f} K, Vsi={dc205.voltage():+.2f} V (held -20), "
      f"Vtg={k_tg.volt():+.4f}, Vbg={k_bg.volt():+.4f}")
assert _T < 1.5

def _read(tag):
    x0, p0 = sr0.X(), sr0.P()
    print(f"{tag}: sr0 X={x0*1e6:+8.2f} uV P={p0:+7.1f} deg  -> |I|={abs(x0)/1e6*1e12:7.1f} pA | "
          f"sr1 X={sr1.X()*1e9:+8.1f} nV  sr2 X={sr2.X()*1e9:+8.1f} nV  sr3 X={sr3.X()*1e9:+8.1f} nV")

print("--- Test 1: frequency (10 mV drive) ---")
for f in [6.777, 13.777, 27.777]:
    sr1.frequency(f)
    interruptible_sleep(8)   # >= 10 tau of the slowest (sr0, 0.3 s) + margin at low f
    _read(f"f={f:6.3f} Hz")
sr1.frequency(13.777)

print("--- Test 2: amplitude linearity (13.777 Hz) ---")
for a in [0.010, 0.050, 0.100]:
    sr1.amplitude(a)
    interruptible_sleep(5)
    _read(f"A={a*1e3:5.1f} mV")
sr1.amplitude(0.010)
interruptible_sleep(3)
_read("restored 10 mV")
print("settings restored: f=13.777 Hz, A=10 mV")
