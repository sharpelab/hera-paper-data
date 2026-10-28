## HERA — P5: temperature ladder — the activation gap Δ(D)

Plan step **P5**, and the last measurement of the session. Everything so far says the gap
is real and centred at D = 0, but says it in *resistance*. This says it in **meV**.

**Why this is the measurement that closes the argument.** Run 3's R_CNP(D) has one feature
that does not look like a cleanly growing single-particle gap: above D/ε₀ ≈ 0.23 V/nm it
**saturates** near 3 kΩ instead of continuing up exponentially. That is the signature of a
parallel conduction path or disorder-induced in-gap states putting a floor under the
resistance — and if that floor dominates, "R rose 10×" would be a weaker claim than it
looks. Thermal activation settles it: fitting R_CNP(T) ∝ exp(Δ/2k_BT) at each D returns a
gap in meV whose *D-dependence* is the physics. ABCA requires Δ(D) growing with |D| and
extrapolating to ≈ 0 at D = 0; ABCB requires a finite Δ at D = 0.

**It is also the one measurement immune to the unknown geometry.** The device card gives no
Hall-bar dimensions, so every resistance this session is in ohms, not ohms-per-square, and
the geometric prefactor is unknown. Activation is a *ratio* measurement — the prefactor
cancels exactly. So does the ~7–10 % probe-loading systematic, provided it does not itself
depend on temperature.

**Design.** At each temperature, one 245-point co-swept `multisweep` that walks the
session-measured CNP line (`V_bg = −1.2737·V_tg − 0.00764`) five times at perpendicular
V_bg offsets of 0, ±0.05, ±0.10 V, folded into a single path and reshaped to (5, 49) in
analysis. The offsets matter: they let R_CNP be taken as the **maximum over offsets** at
each point along the line, so a few-mV drift in the fitted line — or thermal drift of the
CNP itself as the sample warms — cannot masquerade as a change in gap. One sweep covers
D/ε₀ = −0.094 → +0.285 V/nm, so every temperature yields a complete R_CNP(D) curve in
under 4 minutes.

**Temperatures:** base, then 8, 12, 17, 23, 30, 40 K via `set_both(T, ratio=0.95)` — the
rig-card-sanctioned ratio; any deviation is consent-gated and is not used. Points are
accepted on **stability, not proximity**: the rig card records that the sample loop is
untuned, overshoots ~+1.4 K, and recovers only as fast as the bath allows, so waiting for
|T − setpoint| to close never converges below ~20 K. `T_sample` is followed per point, so
the Arrhenius fit uses the temperature actually measured, never the setpoint. The ladder
starts at 8 K deliberately — the rig's electron temperature is ~8 K, so nothing below that
carries independent information.

**Field to zero first.** Activation must be measured at B = 0 or a Landau gap contaminates
Δ. The down-sweep left the magnet at 0.5 T, so this cell owns the last leg down and
asserts |B| ≤ 0.05 T after the blocking ramp before any heater is touched.

**Ends warm, deliberately.** This is the last measurement, and cooling back to base from
40 K is passive and slow (τ ≈ 27 min). Close-out does not require base temperature — it
requires the field at zero, the gates at zero, and both heater ranges off.

**Cost** ~50 min: ~4 min of ramp to zero, then 7 × (settle ~3–4 min + sweep ~4 min).
**Checkpoints:** the printed settle line at each temperature (T and its σ), and each run id
as it lands — seven separate run directories, so a failure at any temperature costs one
point, not the ladder.
