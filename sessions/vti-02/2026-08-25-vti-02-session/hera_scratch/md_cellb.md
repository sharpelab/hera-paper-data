## HERA — gate-current-sanity-check Cell B: reset nplci

All four Gate C legs completed clean — no gross turn-up off the charging slope on
either gate, no cross-gate tracking, both lock-ins live the whole way, and
`sr1` never above 3% of full scale. The recipe's condition for running Cell B is
met.

Resetting the gate-current `nplci` from 10 back to 1: the pA floor existed for the
leakage check, and at ~0.30 s/pt of extra readback it would add ~19 minutes to the
gate map. Validators are re-printed as a check that nothing has moved them.

One caveat carried forward rather than resolved: the TG leakage onset at
V_tg ≈ 0.62 V (+88 pA excess at +1.0 V, run 0). At `nplci = 1` the gate-current
readback coarsens, but 88 pA stays comfortably resolvable — the map will still
show it if it grows.
