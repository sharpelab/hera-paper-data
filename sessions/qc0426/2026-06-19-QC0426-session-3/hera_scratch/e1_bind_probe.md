## HERA — E1 kernel-bind + VERIFY-completion probe (read-only)

**State: bring-up green, E0, awaiting the autonomy grant.** Gates A and B verified from disk:
all setup cells executed in one kernel (magnet status 0.003 T / PS on / output enabled;
sample_T 1.167 K; sr0-3 + QSwitch ser37 fw2.0 up); SAFETIES exec [11] commits exactly the
device-card limits - TG [-6, +7], BG [-4.5, +4.5], Si [-50, +50] V, B cap 8.0 T on
magnet.mag.vals. Within machine limits; no planned excursion enters the >10 T & >15 K zone.

This **read-only** cell is the brief's first-E1-execute kernel-bind probe. It (1) confirms this
kernel carries the operator's instruments, (2) finishes the VERIFY field/T reads with a fresh
magnet.mag() + sample_temperature(), (3) echoes the committed validators, and (4) records
lock-in tau/slope (rig card: operator-set, absent from run metadata - device card claims 0.3 s /
24 dB/oct -> 1.2 s/pt floor). No hardware writes, so it is safe to run in E0 now if you like.

**Next, on "go for autonomy":** Gate C - mux.select(...) to the provided contact config
(source T2 / drain B7 / sr1 T3-T4 / sr2 B4-B5 / sr3 T5-B6) + a cheap fixed-gate read to confirm
the contacts are live (first-session branch, no reference run) - then Step 1 of the
investigation: the 0 T TG-BG gate map for the CNP line and the (n, D) calibration.
