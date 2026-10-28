## HERA — Step 1 gatemap remainder (BG +2.0→+4.2), stitches onto run 2

Run 2 crashed on a transient SR830 SNAP glitch at BG row 44/61 (one-off; state-check confirmed gates parked at 0, bus recovered). 44 clean rows (BG −4→+1.88) are in hand: CNP slope −1.19 (= geometry prior), no SC candidate in that range. This completes the box: **BG +2.013→+4.2 (17 rows), TG fast −7→+6 (101)** — `np.linspace(-4,4.2,61)[44:]`, so it lands on exactly the same grid and concatenates onto run 2 rows 0–43 in analysis (run 2's partial row 44 is re-done here and discarded).

**Robustness tweak:** drop `sr830_4` from the read set (it's unusable — shares the drive contact, ±24 kΩ scatter) — fewer GPIB SNAP reads, less glitch surface. sr1/sr2/sr3 retained. If the transient recurs, I'll just re-run the still-missing tail.

**Price:** 1717 pts × ~0.75 s/pt (run-2 measured) ≈ **~25 min** (incl. settles). Under the 30-min checkpoint threshold — `hera-watch --follow` will wake me at completion (or another crash). Magnet still untouched (pristine field asserted). Drive 0.5 nA. Gates park to 0 at end.

**Preconditions** (asserted): T base; |B|<5 mT (pristine); drive 0.5 nA; gates printed. Watch the live leakage plots.
