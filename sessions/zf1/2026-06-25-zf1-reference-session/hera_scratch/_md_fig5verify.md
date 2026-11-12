## HERA — Fig 5 verify: cheap 1D dV/dI vs I_dc at base (Ic check before the 2D)

Fig 4 done (ξ ≈ 0.30 μm). **Fig 5 = dV/dI vs (I_dc, T)** at the optimum, B=B_eff0 — the brief gates it on a cheap base dV/dI confirming the supercurrent is clean first. **This is that verify.**

Ramps the field **back to B_eff0** (from the +0.75 mT Fig-4 field — a positioning ramp that crosses controller 0; read back), waits for base + R-settle, then a **round-trip dV/dI vs I_dc, ±80 nA** (±8 V on dc205, I_dc=V_dc/1e8). **AC 0.5 nA**, 4T sens 0.1 mV. Round-trip (fwd+bwd) doubles as a hysteresis check. Expect: dV/dI≈0 for |I_dc|<Ic, switching to normal (~50 Ω) at **Ic≈28 nA** with peaks near **±36 nA** (matching run 9 / the handoff).

~5 min (302 pts × ~1 s). Preconditions asserted (gates at optimum, heater off, field on B_eff0). dc205 returns to 0 at the end. **Proceed to the 2D only if this is clean.** If Ic≈28 nA and symmetric, I’ll propose Fig 5 (dV/dI vs I_dc × the settled T-ladder). Run when ready.
