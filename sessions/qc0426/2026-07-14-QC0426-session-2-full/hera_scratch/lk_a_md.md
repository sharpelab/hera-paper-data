## HERA — REVISED plan (supersedes the previous cell, which should NOT be run — its cooldown phase is replaced by the LK ladder)

**Cell A (this one): prove the machinery up — base → 3 K → 10 K → 50 K, ending HOLDING at 50 K.**
Same validation as before (both range bands, logfile-freshness guard per poll, vaporizer-runaway assert, interruptible, heaters-off on any exception via `finally` — but on *success* it holds at 50 K and hands off to the ladder cell). Gates parked, B stays at 8 T. ~45–55 min.

**Cell B (next): LK-mass ladder DOWN — 8 rungs, 25 → 1.5 K, one field sweep per rung.**
Runs only after A's plateau numbers look right.
