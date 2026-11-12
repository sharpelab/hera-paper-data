# HERA — bring-up read. READ-ONLY: parameter gets and status-register queries
# only. No sets, no ramps, no sweeps, no run directory.

# --- preconditions this cell assumes but does not set ---
_vtg, _vbg, _vsi = k_2400_tg.volt(), k_2400_bg.volt(), dc205.voltage()
_B, _Ts = magnet.field(), T_sample()
print(f"preconditions: V_tg={_vtg:+.4f} V  V_bg={_vbg:+.4f} V  V_si={_vsi:+.4f} V  "
      f"B={_B:+.4f} T  T_sample={_Ts:.3f} K")
assert abs(_vtg) < 1e-3 and abs(_vbg) < 1e-3 and abs(_vsi) < 0.01, "gates not parked at 0"
assert abs(_B) < 0.02, "field not at zero"
assert 1.0 <= _Ts <= 1.4, "sample not at base"

_amp, _frq = sr1.amplitude(), sr1.frequency()
_Rbias = meas_config["bias_resistor"]
_gain0 = meas_config["sr0_gain"]
print(f"drive: {_amp} V @ {_frq} Hz across {_Rbias:.3g} ohm -> I_bias(nominal) = {_amp/_Rbias:.4e} A")
print()

# --- per-lock-in read + overload flags ---
# SR830 LIAS? status byte: bit0 = input/reserve overload, bit1 = time-constant
# filter overload, bit2 = output overload. Reading it is a query (it latches,
# so this reports anything since the last read - fine for a bring-up snapshot).
_reads = {}
print(f"{'ch':<4} {'X (V)':>13} {'Y (V)':>13} {'R (V)':>13} {'theta':>8} {'sens':>10} "
      f"{'|X|/sens':>9}  overloads")
for _nm, _sr in [("sr0", sr0), ("sr1", sr1), ("sr2", sr2), ("sr3", sr3)]:
    _X, _Y, _R, _P = _sr.X(), _sr.Y(), _sr.R(), _sr.P()
    _sens = _sr.sensitivity()
    try:
        _lias = int(_sr.ask("LIAS?"))
        _ov = ",".join([n for b, n in ((0, "INPUT"), (1, "FILTER"), (2, "OUTPUT"))
                        if (_lias >> b) & 1]) or "none"
    except Exception as _e:
        _ov = f"(unread: {type(_e).__name__})"
    _reads[_nm] = (_X, _Y, _R, _P, _sens)
    print(f"{_nm:<4} {_X:>13.5e} {_Y:>13.5e} {_R:>13.5e} {_P:>8.2f} {_sens:>10.3e} "
          f"{abs(_X)/_sens:>9.3f}  {_ov}")

# --- transport numbers ---
print()
_I = _reads["sr0"][0] / _gain0          # A, true current through the device
_Vxx = _reads["sr1"][0]                 # V, sr1 gain is unity per the device card
print(f"I (from sr0)      = {_I:.5e} A   [nominal {_amp/_Rbias:.4e} A -> "
      f"{100*_I/(_amp/_Rbias):+.1f}% of nominal]")
print(f"V_xx (sr1, B1-B2) = {_Vxx:.5e} V")
if _I != 0:
    print(f"R_xx = V_xx / I   = {_Vxx/_I:.5e} ohm")
    # current-bias validity: R_device must be << R_bias
    print(f"implied series R (drive/I - R_bias) = {_amp/_I - _Rbias:.4e} ohm "
          f"(current bias holds while this is << {_Rbias:.3g})")
else:
    print("R_xx: undefined - sr0 X is zero (no current path?)")

print()
print(f"phase check: sr0 theta={_reads['sr0'][3]:+.2f} deg, sr1 theta={_reads['sr1'][3]:+.2f} deg "
      f"(near 0/180 = resistive; large |theta| = capacitive contamination or unsettled)")
print("BRINGUP-READ: done")
