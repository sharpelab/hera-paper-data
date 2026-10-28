## HERA — E1 kernel-binding probe (read-only)

Brief [VERIFY] item: *"the first E1 execute is a read-only namespace probe that
confirms it is bound to the operator's instrument-carrying kernel."* This is that
probe and nothing more — it reads `os`/`globals()`/the qcodes instrument registry
and writes to no instrument. It must print `PROBE: BOUND` before the VERIFY cell
below is executed.
