# VERIFY — session-start checks (brief: [VERIFY] at session start).
# Read-only by construction: getters and file stats only — no sets, no ramps,
# no heater/gate/field writes. Runtime ~20 s (worker-cadence poll dominates).
# The E1 grant keys on the printed verdict line at the end of this cell.
import os
import time

_fails = []

def _chk(name, ok, detail):
    if not ok:
        _fails.append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")

# --- 1. Magnet at 0 T (measured readback, both surfaces) ---
_B = magnet.field()
_B_stat = magnet._status()["field"]
_chk("magnet-zero", abs(_B) <= 0.02 and abs(float(_B_stat)) <= 0.02,
     f"field()={_B:+.4f} T, _status[field]={_B_stat}")
_chk("magnet-output",
     magnet.persistent_switch_on() and magnet.output_enabled(),
     f"PS heater on={magnet.persistent_switch_on()}, output={magnet.output_enabled()}")

# --- 2. SAFETIES committed == device card (independent re-statement of the
#        card numbers — compares the live validators, not the notebook vars) ---
def _vr(p):
    v = p.vals
    return (float(v._min_value), float(v._max_value))

_card = {
    "tg-validator":  (k_2400_tg.volt,        (-3.0, 3.0)),
    "bg-validator":  (k_2400_bg.volt,        (-4.5, 4.5)),
    "si-validator":  (dc205.smart_voltage,   (-50.0, 50.0)),
    "si-raw-validator": (dc205.voltage,      (-50.0, 50.0)),
    "field-cap":     (magnet.field,          (-8.0, 8.0)),
    "t-cap-sample":  (heater.sample_setpoint,    (0.0, 100.0)),
    "t-cap-vaporizer": (heater.vaporizer_setpoint, (0.0, 100.0)),
}
for _name, (_p, _exp) in _card.items():
    try:
        _got = _vr(_p)
        _chk(_name, _got == _exp, f"committed {_got}, card {_exp}")
    except Exception as _e:
        _chk(_name, False, f"validator unreadable: {_e!r}")

# --- 3. Base T holding ---
_Ts = T_sample()
_chk("base-T", 1.0 <= _Ts <= 1.5, f"T_sample = {_Ts:.3f} K (base ~= 1.2-1.3 K)")

# --- 4. Heaters off, vaporizer tracking base ---
_rs, _rv = heater.sample_range(), heater.vaporizer_range()
_chk("heaters-off", _rs == 0 and _rv == 0, f"sample_range={_rs}, vaporizer_range={_rv}")
_Tv = T_vaporizer()
_chk("vaporizer-base", _Tv < 2.0, f"T_vaporizer = {_Tv:.3f} K")

# --- 5. Lakeshore worker logfile: mtime advancing on the 5 s cadence.
#        Poll 16 s at 0.5 s; a 5 s worker shows >=2 mtime changes, the stale
#        30 s worker <=1 (rig card: threshold must allow >=2-3 write periods). ---
_cands = [p for p in VTI.temp_logfile_candidates["T_sample"] if os.path.exists(p)]
if not _cands:
    _chk("worker-cadence", False, "no T_sample logfile found")
else:
    _lf = _cands[0]
    _mt, _changes = os.path.getmtime(_lf), 0
    for _ in range(32):
        interruptible_sleep(0.5)
        _m = os.path.getmtime(_lf)
        if _m != _mt:
            _changes += 1
            _mt = _m
    _age = time.time() - _mt
    _chk("worker-cadence", _changes >= 2,
         f"{_changes} writes in 16 s, last write {_age:.1f} s ago ({_lf})")

# --- He level (AMI 1700, read-only query; closed-loop system per rig card,
#     so this is bath-presence/sensor-alive, not a consumption budget) ---
try:
    try:
        _ami = qcodes.Instrument.find_instrument("ami")
    except Exception:
        from drivers.AMI_1700 import AMI_1700
        _ami = AMI_1700("ami", "TCPIP0::192.168.0.100::7180::SOCKET")
    _he = _ami.He_level()
    _chk("he-level", _he > 0, f"{_he:.1f} in (closed-loop rig; operator judges margin)")
except Exception as _e:
    _chk("he-level", False, f"AMI 1700 read failed: {_e!r}")

# --- 6. Contacts hardwired per the device card's provided configuration ---
_exp_wiring = {"source": "T2", "drain": "B7", "sr1+": "T3", "sr1-": "T4",
               "sr2+": "B4", "sr2-": "B5", "sr3+": "T5", "sr3-": "B6"}
_chk("contact-config", WIRING == _exp_wiring, f"WIRING == card: {WIRING == _exp_wiring}")

# --- 7. DC205 on +/-100 V range, output on, reading 0 V ---
_rng, _out, _V = dc205.voltage_range(), dc205.output(), dc205.voltage()
_chk("dc205", int(_rng) == 2 and int(_out) == 1 and abs(_V) <= 0.05,
     f"range={_rng} (need 2), output={_out}, V={_V:+.4f}")

# --- Verdict (machine-read; last line of output) ---
if _fails:
    print(f"VERIFY: FAIL {_fails[0]}" + (f" (+{len(_fails)-1} more: {', '.join(_fails[1:])})" if len(_fails) > 1 else ""))
else:
    print("VERIFY: ALL GREEN")
