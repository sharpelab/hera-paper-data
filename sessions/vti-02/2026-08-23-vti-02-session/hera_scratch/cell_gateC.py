# HERA — gate C: liveness on the provided pair (plan step 0).
# Preconditions (assumed, not set) -> lock-in ranging -> 0D read -> TG sweep at V_bg=0.

# --- preconditions: state this cell inherits
_T, _B, _Vbg, _Vsi = T_sample(), magnet.field(), k_bg.volt(), dc205.voltage()
print(f"precheck: T_sample={_T:.3f} K (want 1.0-1.4) | B={_B:.4f} T (want |B|<0.02) | "
      f"V_bg={_Vbg:.4f} V (want 0) | V_si={_Vsi:.3f} V (want 0)")
assert 1.0 <= _T <= 1.4, "T_sample out of base window"
assert abs(_B) < 0.02, "magnet not at zero"
assert abs(_Vbg) < 1e-3 and abs(_Vsi) < 0.01, "BG/Si not at 0 V"

# --- lock-in ranging (flagged in the VERIFY markdown; state0 holds the originals for close-out)
for _s in (sr0, sr1):
    _s.time_constant(0.03)
    _s.filter_slope(24)
sr0.sensitivity(0.02)    # 10 nA x 1e6 V/A = 10 mV
sr1.sensitivity(1e-3)    # 100 kOhm full scale at 10 nA; autorange hook below keeps it in band
time.sleep(0.5)

# --- 0D liveness read (printed, not a run)
_I = sr0.X() / meas_config["sr0_gain"]
_P0, _X1, _Y1 = sr0.P(), sr1.X(), sr1.Y()
print(f"liveness: I_drain={_I*1e9:.3f} nA (expect ~10) phase(sr0)={_P0:.1f} deg | "
      f"sr1 X={_X1*1e6:.2f} uV Y={_Y1*1e6:.2f} uV -> Rxx~{(_X1/_I if _I else float('nan')):.1f} Ohm")


class SrAutoRange:
    """run_after hook: keep max(|X|,|Y|) of one SR830 inside [8%, 80%] of its
    sensitivity. Reads the sweep's own row (no extra instrument reads) and only
    talks to the lock-in when a range step is needed."""
    def __init__(self, sr, cols, gain=1.0, lo=1e-6, hi=1.0):
        self.sr, self.cols, self.gain, self.lo, self.hi = sr, cols, gain, lo, hi
        self.sens = sr.sensitivity()
        self.log = []
    def __call__(self, data):
        r = max(abs(float(data[i]) * self.gain) for i in self.cols)
        if r > 0.8 * self.sens and self.sens < self.hi:
            if self.sr.increment_sensitivity():
                self.sens = self.sr.sensitivity(); self.log.append(("up", self.sens))
        elif r < 0.08 * self.sens and self.sens > self.lo:
            if self.sr.decrement_sensitivity():
                self.sens = self.sr.sensitivity(); self.log.append(("down", self.sens))


# --- station: row = [time, V_tg, sr0_X(->A), sr0_P, sr1_X, sr1_Y, k_tg_curr, k_bg_curr, T_sample]
meas_config["sample_temperature:"] = T_sample()
meas_config["Si (V)"] = dc205.voltage()
meas_config["comments"] = "gate-c-liveness: TG 0->-0.3->1.0->-0.3->0 V @5 mV, BG=0, Si=0, B=0, base T"
s = sweep.AsyncStation(meas_config)
s.fp(sr0.X, meas_config["sr0_gain"]).fp(sr0.P).fp(sr1.X).fp(sr1.Y).fp(k_tg.curr).fp(k_bg.curr).fp(T_sample)
s.add_comment("gate-c-liveness")
s.add_comment("TG 0->-0.3->1.0->-0.3->0 V @5mV, delay 0.2 s, tau 30 ms; V_bg=0, V_si=0, B=0; I_bias 10 nA")
ar1 = SrAutoRange(sr1, cols=(4, 5), gain=1.0, lo=1e-6, hi=0.5)
s.register_run_after(ar1, args=())
for _p in (sr1.X, sr0.X, sr1.Y, sr0.P, k_tg.curr, k_bg.curr, T_sample):
    s.plot(k_tg.volt, _p)

_up = spoints(-0.3, 1.0, 261)
_vt = np.concatenate([spoints(0.0, -0.3, 61), _up[1:], _up[::-1][1:], spoints(-0.3, 0.0, 61)[1:]])
print(f"sweep: {len(_vt)} pts, V_tg in [{_vt.min():.2f}, {_vt.max():.2f}] V, ends at {_vt[-1]:.2f} V")
_t0 = time.time()
res = s.sweep(k_tg.volt, _vt, delay=0.2)
_dt = time.time() - _t0
print(f"run {res.id}: {_dt/60:.1f} min, {_dt/len(_vt):.3f} s/pt; sr1 autorange log: {ar1.log}")
print(f"end state: V_tg={k_tg.volt():.4f} V, V_bg={k_bg.volt():.4f} V, T_sample={T_sample():.3f} K, sr1 sens={sr1.sensitivity()} V")
