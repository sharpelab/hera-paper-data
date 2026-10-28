## HERA — VERIFY (session-start checks, read-only)

Gate A and gate B verified from disk: setup cells [1]–[9] executed this kernel with sane readbacks (magnet 0.006 T, output on, PS heater on; T_sample 1.166 K, T_vaporizer 0.945 K, logfiles live at 5 s cadence; both Keithleys verified at 0 V; DC205 RNGE 2, output on), and SAFETIES [10] commits exactly the card's limits — TG [−0.3, +1.0] V, BG [−1.3, +2.0] V, Si ±25 V, |B| ≤ 10 T, T ≤ 100 K — inside the rig's 14 T / 100 K machine limits.

Two cells below, both read-only (gets only, nothing set). **Cell 1** is the kernel-binding probe; **Cell 2** is VERIFY, ending in the verdict line `VERIFY: ALL GREEN` / `VERIFY: FAIL <items>`. Per the brief, Zack says **"go for autonomy"** without running them; I execute probe → VERIFY as my first E1 acts and engage only on the printed green line. One item VERIFY cannot read from this kernel: **He level** (AMI 1700 not connected in this notebook) — please state the He level / session budget with the grant.

Noted for the first measurement, not a blocker: `sr1` sits at 2 µV sensitivity (= 200 Ω full scale at the 10 nA bias) and both lock-ins at τ = 0.3 s / 24 dB/oct (settling floor ≈ 2–3 s/pt). The liveness cell will size sensitivity for an unknown Rxx; τ I will leave as set unless it prices a sweep out.
