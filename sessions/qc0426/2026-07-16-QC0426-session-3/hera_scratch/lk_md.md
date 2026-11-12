## HERA — LK mass ladder at (n = −6e12, D = 0) — `temperature-dependence-vti` (operator-unbanned)

Blocklist exception: **operator explicitly unbanned `temperature-dependence` for this session and requested the ladder** (recorded in session_notes). This is the call's named firming step: per-branch LK mass at the ABA pair — two distinct masses confirm two genuine bands; independently, a coexisting component *lighter* than the main branch cannot be a beat (decisive exclusion).

**Flavor B**: 6 rungs — base, then `set_both(T, ratio=0.95)` → 6, 10, 14, 19, 25 K (all under the 50 K cap; ratio per rig card). Per rung: **hover acceptance** (stable < 0.1 K over 90 s within [nom−0.5, +3]; fp'd per-point T is the fit axis, labels stay nominal), logfile-freshness guard on every poll (≥ 2–3 write periods), **runaway guard** (fault only on T_vap rising above both rung-start and target). Then the *same* field sweep, **direction alternated from the live field** (VTI mandatory): 3 ↔ 8 T, 251 pts (ΔB 20 mT = ×2.4 Nyquist on the 66 T sum tone at B_lo; δF = 4.8 T separates f_ML = 11 from f_BL = 55; the high-B window is where warm-rung oscillations survive). One file per rung, station rebuilt per rung (comments are station-lifetime).

**LK caveat, stated**: base electron temperature ≈ 8 K (rig card) — the base/6 K rungs sit in the T_e-flattened regime and effectively *measure* T_e; the mass slope comes from rungs ≥ 10 K. Mount→device gradient uncharacterized at heater power — absolute-T error inherited linearly by the fit (rig card Offsets); masses reported with that hedge. No automated LK fit exists in the corpus — the fit lands flagged for expert review.

**Wall-clock**: rung 0 includes 0→3 T positioning (~22 min); each sweep ≈ 43 min (5 T traverse-dominated + 251 × 1.5 s); up-leg catches 2.5–4 min (rig card) ≈ **5.3–5.6 h total**. Ends: heaters off, gates parked, B → 0 (blocking, in the finally).

**Checkpoints**: per-rung completion (armed watch, re-armed each rung): T accepted vs nominal, tones present, amplitude trend monotonic-down. Abort: runaway guard, hover timeout (40 min), or top-rung amplitude NOT suppressed → extend ladder up instead of burning rungs (recipe Verify).
