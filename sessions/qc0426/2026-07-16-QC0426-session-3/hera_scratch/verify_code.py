# HERA — session-start VERIFY. Read-only: no instrument writes.
import os, time
from pathlib import Path

# --- magnet at zero, PS heater / output ---
B = magnet.field()
print(f"B (measured)     : {B:+.4f} T | status: {magnet._status()['field']}")
assert abs(B) < 0.02, f"magnet not at zero: {B} T"
ps, oe = magnet.persistent_switch_on(), magnet.output_enabled()
print(f"magnet PS/output : heater {ps}, output {oe}")
assert ps and oe, "PS heater / output not in operating state"

# --- base T + logfile freshness (frozen worker guard) ---
Ts, Tv = T_sample(), T_vaporizer()
p = next(Path(c) for c in VTI.temp_logfile_candidates["T_sample"] if Path(c).exists())
age = time.time() - p.stat().st_mtime
print(f"T_sample         : {Ts:.3f} K (log age {age:.0f} s) | T_vaporizer: {Tv:.3f} K")
assert 1.0 < Ts < 1.5, f"sample T out of base band: {Ts} K"
assert age < 15, f"T logfile stale ({age:.0f} s) — lakeshore worker dead?"

# --- DC205 (Si gate): range 2, output on, 0 V ---
v_si, rng, out = dc205.voltage(), dc205.voltage_range(), dc205.output()
print(f"DC205 (Si)       : {v_si:+.4f} V, range {rng} (need 2), output {out}")
assert int(rng) == 2, "DC205 not on ±100 V range"
assert int(out) == 1, "DC205 output not on"
assert abs(v_si) < 1e-3, f"DC205 not at 0 V: {v_si} V"

# --- gate readbacks (expected: all parked at 0) ---
print(f"gates            : TG {k_tg.volt():+.4f} V, BG {k_bg.volt():+.4f} V, Si {k_si():+.4f} V")

# --- committed validators vs device card ---
for name, par, lo, hi in [
    ("TG", k_2400_tg.volt, -3.0, 3.0),
    ("BG", k_2400_bg.volt, -4.5, 4.5),
    ("Si", dc205.smart_voltage, -50.0, 50.0),
    ("B",  magnet.field, -8.0, 8.0),
]:
    v = par.vals
    print(f"validator {name:2s}     : {v}")
    assert v._min_value == lo and v._max_value == hi, f"{name} validator != card [{lo}, {hi}]"

# --- lock-in settling record (operator-set; snapshots store None — this is the record) ---
for sr in (sr0, sr1, sr2, sr3):
    print(f"{sr.name}: tau {sr.time_constant()} s, slope {sr.filter_slope()} dB/oct, sens {sr.sensitivity()}")

print("\nVERIFY: all green — awaiting 'go for autonomy'")
