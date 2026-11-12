# Gate C — contact liveness on the provided configuration (first-session branch,
# no reference run). Routes the device-card config through the QSwitch, then reads
# the lock-ins at the resting gate point to confirm source-drain carries current
# and each four-terminal pair reads a sane resistance. No sweep -> no run dir.
import time

# --- preconditions this cell assumes but does not set ---
_T = heater.sample_temperature()
_B = magnet.mag()
_vtg = dc205.voltage(); _vbg = k_2400.volt(); _vsi = k_2410.volt()
print(f"[precond] sample_T={_T:.3f} K  B={_B:+.4f} T  TG={_vtg:+.3f} BG={_vbg:+.3f} Si={_vsi:+.3f} V")
assert _T < 5.0, f"sample_T {_T} K unexpectedly high"
assert abs(_B) < 0.05, f"|B|={_B} T not at zero"
assert -6.0 <= _vtg <= 7.0 and -4.5 <= _vbg <= 4.5 and -50 <= _vsi <= 50, "a gate sits outside its validator"

# --- route the provided contact configuration (Auto: ContactMux, in-envelope) ---
# Si standing closures (lines 16/11) are excluded from the managed set; select()
# never touches them and never calls qsw.reset().
mux.select({"source": "T2", "drain": "B7",
            "sr1+": "T3", "sr1-": "T4",
            "sr2+": "B4", "sr2-": "B5",
            "sr3+": "T5", "sr3-": "B6"})
print(f"[mux] selected provided config; settle_s={mux.settle_s}")
time.sleep(1.0)  # extra lock-in settle on top of mux settle (tau=0.3, 24 dB/oct)

# --- liveness read ---
I_bias_nom = sr1.amplitude() / 100e6                 # nominal drive current
I_meas = sr0.X() / abs(meas_config["sr0_gain"])      # measured AC current via Ithaco
print(f"[drive] V_ac={sr1.amplitude():.4f} V  f={sr1.frequency():.2f} Hz  I_bias_nom={I_bias_nom*1e9:.3f} nA")
print(f"[current] sr0.X={sr0.X():.4e} V_preamp -> I_meas={I_meas*1e9:.4f} nA  (P={sr0.P():.1f} deg)")
for nm, s in (("sr1 T3-T4", sr1), ("sr2 B4-B5", sr2), ("sr3 T5-B6 (Rxy)", sr3)):
    V = s.X()
    R = V / I_meas if I_meas != 0 else float('nan')
    print(f"[{nm:16s}] X={V:+.4e} V  P={s.P():+6.1f} deg  R=V/I_meas={R:10.1f} ohm")
