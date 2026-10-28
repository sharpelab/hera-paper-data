# === Settle test — measure the true per-step equilibration time (sets the settled-ladder dwell) ===
# Fig 3 (run 4) showed a ~50 mK sample-probe lag at 90 s dwell. Park the heater at
# the transition midpoint from base and watch R (the sample-T proxy) equilibrate
# -> the time for R to plateau is the dwell the settled re-do needs.
import time

B_EFF0 = -0.366e-3
# --- preconditions: at base, B_eff0, gates at optimum, heater off ---
T0 = temperature(); B_now = magnet.field(); Vtg = k_tg.volt(); Vbg = k_bg.volt(); Hv = heater.volt()
print(f"T={T0*1e3:.1f} mK (expect ~34) B={B_now*1e3:.4f} mT V_tg={Vtg:.3f} V_bg={Vbg:.3f} heater={Hv:.3f} V")
assert T0 < 0.060, f"not at base: {T0*1e3:.1f} mK"
assert abs(B_now-B_EFF0) < 0.0015, "B off B_eff0"
assert abs(Vtg-(-5.365))<0.010 and abs(Vbg-(+3.987))<0.010, "gates off optimum"
assert Hv < 0.01, "heater not off"

dc205_1.volt(0.0); sr830_1.amplitude(0.1); sr830_2.sensitivity(0.005); sr830_3.sensitivity(1e-4)
I_bias = 0.1/1e8
def Rnow(): return (sr830_3.X()/100)/I_bias

def watch(Vset, minutes):
    print(f"\n--- park heater {Vset} V, watch {minutes} min ---")
    t0 = time.monotonic(); heater.volt(Vset); time.sleep(1.0)
    assert abs(heater.curr()) > 1e-9, f"heater not drawing at {Vset} V"
    rec = []
    print(" t(s)   T(mK)   R(ohm)   dR (last)")
    Rprev = None
    while time.monotonic()-t0 < minutes*60:
        interruptable_sleep(15)
        T = temperature(); R = Rnow(); el = time.monotonic()-t0
        dR = (R-Rprev) if Rprev is not None else 0.0
        print(f" {el:5.0f}  {T*1e3:6.1f}  {R:7.2f}   {dR:+6.2f}")
        rec.append((el, T*1e3, R)); Rprev = R
    rec = np.array(rec)
    Rfinal = np.median(rec[-4:,2])
    # settle time = first t where R within 2% of final and stays
    tol = max(0.02*abs(Rfinal), 0.5)
    settled = None
    for el, T, R in rec:
        if abs(R-Rfinal) <= tol:
            settled = el; break
    print(f"  -> {Vset} V: T_final={np.median(rec[-4:,1]):.1f} mK, R_final={Rfinal:.2f} ohm, "
          f"R within 2% by t~{settled:.0f} s")
    return rec

# transition midpoint (most lag-sensitive); ~262 mK at 4.5 V per warm-up
watch(4.5, 14)
heater.volt(0.0)
print(f"\nheater back to 0; cooling to base. T={temperature()*1e3:.1f} mK. "
      f"Settled re-do dwell = the R-plateau time above (with margin).")
