## HERA — VERIFY (session-start checklist)

Gates A and B read green from the notebook: setup executed in this kernel
(magnet 0.003 T with PS on / output enabled; T_sample 1.171 K; sr0–sr3, both
2400s, DC205 on RNGE 2 connected), and the SAFETIES cell [exec 12] commits
exactly the device-card limits (TG ±3.0 V, BG ±4.5 V, Si ±50 V, |B| ≤ 8.0 T,
T ≤ 50 K). This cell is the brief's [VERIFY] checklist, **read-only by
construction** — magnet zero + PS/output, validator ranges vs the card's
numbers, base-T hold, heaters off, the 5 s worker-logfile cadence (12 s mtime
watch), DC205 range/output/zero, the hardwired contact map, and an AMI-1700 He
read. Last printed line is the verdict the grant keys on: `VERIFY: ALL GREEN`
or `VERIFY: FAIL <item>`. Runtime ≈ 15 s (dominated by the logfile watch).

Per the brief: on **"go for autonomy"** my first E1 acts are the read-only
kernel-binding probe, then executing this cell; E1 engages only on the printed
green verdict.
