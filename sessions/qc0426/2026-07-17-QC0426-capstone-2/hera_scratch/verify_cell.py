# VERIFY — session-start checklist (brief, 2026-07-17). Read-only by
# construction: every line is a get/read; no instrument writes anywhere.
# The last printed line is the machine-readable verdict the E1 grant keys on.
import os

checks = []  # (name, ok, detail)

def check(name, ok, detail):
    checks.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")

# -- 1. Magnet at 0 T (measured readback, both query paths)
B = magnet.field()
B_status = magnet._status()["field"]
check("magnet-zero", abs(B) < 0.01 and abs(B_status) < 0.01,
      f"field()={B:.4f} T, _status={B_status:.4f} T")

# -- 2. PS heater / output enabled (silent precondition; field() raises otherwise)
ps, out = magnet.persistent_switch_on(), magnet.output_enabled()
check("magnet-ps-output", ps and out,
      f"persistent_switch_on={ps}, output_enabled={out}")

# -- 3. SAFETIES committed == device-card operating limits (numbers, not eyeball)
def vrange(param):
    v = param.vals
    return (v._min_value, v._max_value)

expected = {
    "k_tg.volt":                ((-3.0, 3.0),   k_2400_tg.volt),
    "k_bg.volt":                ((-4.5, 4.5),   k_2400_bg.volt),
    "dc205.smart_voltage":      ((-50.0, 50.0), dc205.smart_voltage),
    "dc205.voltage":            ((-50.0, 50.0), dc205.voltage),
    "magnet.field (B cap)":     ((-8.0, 8.0),   magnet.field),
    "heater.sample_setpoint":   ((0.0, 50.0),   heater.sample_setpoint),
    "heater.vaporizer_setpoint":((0.0, 50.0),   heater.vaporizer_setpoint),
}
for nm, (want, param) in expected.items():
    got = vrange(param)
    check(f"safeties:{nm}", got == want, f"committed={got}, card={want}")

# -- 4. Base T holding + vaporizer tracking base
Ts, Tv = T_sample(), T_vaporizer()
check("base-T", 1.0 <= Ts <= 1.5, f"T_sample={Ts:.3f} K (nominal ~1.2-1.3 K)")
check("vaporizer-tracks-base", Tv < 2.0, f"T_vaporizer={Tv:.3f} K")

# -- 5. Heaters off (both ranges 0)
hr1, hr2 = heater.sample_range(), heater.vaporizer_range()
check("heaters-off", hr1 == 0 and hr2 == 0,
      f"sample_range={hr1}, vaporizer_range={hr2}")

# -- 6. Lakeshore worker logfile advancing on the 5 s cadence
# (>= 2 mtime changes inside a 12 s watch = cadence <= ~6 s; a stale 30 s
#  worker shows 0-1. Threshold spans >= 2 write periods per the rig card.)
logfile = VTI.temp_logfile_candidates["T_sample"][0]
mtimes = {os.path.getmtime(logfile)}
for _ in range(12):
    interruptible_sleep(1)
    mtimes.add(os.path.getmtime(logfile))
n_writes = len(mtimes) - 1
check("logfile-cadence-5s", n_writes >= 2,
      f"{n_writes} distinct writes in 12 s (expect 2-3 at 5 s cadence)")

# -- 7. DC205 (Si gate): +/-100 V range (RNGE 2), output on, reading 0 V
rng, outp, vsi = dc205.voltage_range(), dc205.output(), dc205.voltage()
check("dc205-range-output-zero", rng == 2 and outp == 1 and abs(vsi) < 1e-3,
      f"range={rng} (need 2), output={outp}, V={vsi:.4f}")

# -- 8. Contacts hardwired per the device card (documentation cross-check)
CARD_WIRING = {"source": "T2", "drain": "B7", "sr1+": "T3", "sr1-": "T4",
               "sr2+": "B4", "sr2-": "B5", "sr3+": "T5", "sr3-": "B6"}
check("contact-config", WIRING == CARD_WIRING,
      f"WIRING matches card: {WIRING == CARD_WIRING}")

# -- 9. He level (AMI 1700 — closed-loop system, informational; pass = sane read)
try:
    from drivers.AMI_1700 import AMI_1700
    if qcodes.Instrument.exist("ami_he"):
        _ami = qcodes.Instrument.find_instrument("ami_he")
    else:
        _ami = AMI_1700("ami_he", "TCPIP0::192.168.0.100::7180::SOCKET")
    he_level = _ami.He_level()
    _ami.close()
    check("he-level", he_level > 0,
          f"{he_level:.1f} in (closed-loop He; not a session budget constraint)")
except Exception as e:
    check("he-level", False, f"read failed: {e!r}")

# -- Verdict (machine-readable; the E1 grant keys on this printed line)
fails = [nm for nm, ok, _ in checks if not ok]
print("VERIFY: ALL GREEN" if not fails else f"VERIFY: FAIL {fails[0]}")
