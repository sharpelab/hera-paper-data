## HERA — reset rig state to session-start expectations (handoff to fresh session)

Undo this session's acquisition-state changes and put the lock-ins at the
device card's documented settings, so the next bring-up finds the rig where
its card says it should be:

- Keithley `nplci` 10 → **1** (the held Cell-B reset).
- Lock-ins → card values: **τ = 0.3 s, 24 dB/oct** on all four; sensitivities
  **sr1/sr2/sr3 = 2e-5** (CNP/gate-map scale), **sr0 = 1e-2** (card table).
  Caveat carried in the notes: at 1e-2 the drain channel still clips ≥ ~11 nA
  — the new session's bring-up may want 5e-2 until the bias chain is
  identified.
- Drive: sr1 amplitude **0.5 V** (card default), frequency untouched (~13 Hz).
- Verify gates/Si/field parked: prints expected vs actual, ends with a full
  state readback. ~15 s, no sweeps.
