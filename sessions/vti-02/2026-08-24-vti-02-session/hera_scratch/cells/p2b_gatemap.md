## HERA — P2 re-run: gate map without the 2D live plot (run 2 post-mortem)

**Run 2 died at point 3 of 2310** with `BrokenPipeError: [WinError 232]` raised from
`Plotter.add_point` — the live-plot subprocess fell over and took the sweep down with it.
Preconditions had all passed (T 1.170 K, B +0.0063 T, V_si 0, both Keithley outputs on,
τ 0.1 s, sr1 1 mV) and the station had already printed its 27m 21s estimate, so nothing
about the device, the gates or the measurement is implicated.

**Cause.** The extra `s.plot(k_tg.volt, sr1.X, k_bg.volt)` I added for a live map. In
`sweep/plot.py` the mesh branch runs `ax.clear()` → `griddata(...)` → `pcolormesh(...)`
**on every measured point**, re-interpolating the entire accumulated dataset each time —
O(N²) work in the child process — and it is degenerate early on, when the slow axis still
holds a single unique value. Runs 0 and 1 plotted seven 1D channels with no `z` and both
completed cleanly, which isolates the 2D call as the difference.

**Fix: drop the 2D live plot, change nothing else.** This is no loss. The rig card already
warns that `plot.png` is the live monitor and *not* the measurement for rastered or
co-swept maps — the map has to be re-formed from the TSV with `fan_grids` /
`resistance_grids` regardless, which is what the analysis does. The seven per-channel 1D
plots stay, so the operator still sees every followed value live; that is the exact
configuration already proven over two runs.

**No measurement parameter changed** — same window, same steps, same delays, same
channels. Run 2's 3-point stub stays on disk as the record of the failure.

**Lesson recorded** in `session_notes.md`: never give a long `megasweep` a 2D live plot on
this stack; a monitor crash must not be able to destroy a 34-minute measurement. The cheap
insurance is that `hera-watch` caught it within a minute — it reported `partial: 3/2310`
and exited instead of hanging, so the cost of the failure was ~1 min, not 34.
