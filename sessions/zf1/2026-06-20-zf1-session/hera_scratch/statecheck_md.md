## HERA — post-error state check (run 2 crashed at row 44/61)

The Step-1 gatemap (run 2) threw a **transient SR830 SNAP glitch** at BG row 44/61 (~74%): `ValueError: could not convert string to float: '154.764-\n'` — a malformed GPIB response on a batch lock-in read, not a device fault. 4529/6161 rows landed clean and are usable. The cell's `try/finally` should have parked both gates to 0 on the exception; this cell **confirms** that and that the GPIB bus recovered before I propose the re-run.

Reads T, B, gate setpoints + currents, and all four lock-ins (single reads — if one re-throws the glitch, just re-run the cell). If either gate is not at 0, it re-parks. No sweep, no field move. **~10 s.**
