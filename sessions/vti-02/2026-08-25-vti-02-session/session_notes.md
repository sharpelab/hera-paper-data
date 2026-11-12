# Session notes — vti-02 / VTI

Operational log (not a science notebook).

**PROTOCOL — He budget is not machine-checkable from the measure kernel.**
The brief's `[VERIFY]` list includes "He budget for the session", but the AMI
1700 is not bound in the measure notebook's setup section and connecting it
from a VERIFY cell means opening a socket on a shared TCP instrument that the
influx logger may hold. Left it out of the machine verdict (measure cell 33,
item 8) and made it an explicit operator confirmation carried by the grant.
Either the session template should bind the AMI read-only at setup, or the
brief should stop listing He as a VERIFY item and name it an operator item.

**PROTOCOL — base T reads under the card's spec at bring-up.** Rig card and
device card both quote base ≈ 1.2–1.3 K; setup cell 8 read T_sample = 1.176 K.
Opened the VERIFY window to [1.0, 1.4] K rather than failing a colder-than-spec
fridge, and said so on the page (measure cell 32). If 1.176 K is normal for
this cooldown the cards' base range is a touch narrow.

**TOOLING — `nb cells` range syntax rejects `a:b`.** `nb cells <nb> 2:16` dies
with `ValueError: invalid literal for int() with base 10: '2:16'` out of
`parse_range`. `2-16` works. Worth either accepting the colon form or emitting
a usage hint instead of a traceback.

**RECIPE FIX — settling floor vs the rig card's per-point rule of thumb.**
`state0` (measure cell 27) records sr0 and sr1 at tau = 0.3 s, filter slope
24 dB/oct. STYLE rule 12's settling floor (k ≈ 7–10 at 24 dB/oct) puts a
settled point at ~2–3 s, ~10x the rig card's "standard fp set ≈ 0.2–0.25 s/pt
at NPLC=1". Whatever run calibrated that 0.2–0.25 s figure must have been at a
much shorter tau, but the rig card's Timing section does not say so, and run
metadata stores tau as `None` — so the number reads as universal when it is
not. Suggest the rig card's per-point figure carry the tau/slope it was
measured at. Measuring the actual cost at Gate C before pricing anything long.

**GRANT — E1 engaged 2026-08-24.** Operator: "go for autonomy, He is fine. Set
instrument values as you see fit." Kernel probe `PROBE: BOUND` (measure cell 31,
exec 16 — continues the operator's [1]-[15] sequence, all 9 instruments
registered). VERIFY `ALL GREEN` (cell 33, exec 17). Reading the extra grant as
covering lock-in sensitivity / time-constant / filter-slope / oscillator
amplitude only: the session-banned safety surfaces stay banned regardless, and
the specifically consent-gated knobs (`dc205.ramp_rate`, Keithley `volt.step`,
`set_both` ratio) still get a specific ask — a blanket phrase is not an
affirmative go on a specific proposal.

**PROTOCOL — my own cell 37 Part 2 was methodologically wrong; caught and
re-run as cell 39.** It sampled `sr1.X` 24 times back-to-back, ~0.7 s of wall
clock, and reported the std as per-point noise. At tau = 0.3 s those samples are
correlated (roughly two independent values), so the std was biased *low* for
large tau and the comparison was rigged toward the setting I already suspected
was right — it printed a fake 80x noise cliff between tau=0.3 and tau=0.1.
Sampling at the dwell interval instead gave 0.79% vs 1.73%, a factor of 2.2,
close to the sqrt(3) white-noise expectation. Generalisable lesson worth putting
somewhere agents will read it: **any lock-in noise measurement must sample at
>= the filter correlation time**, and the natural choice is the dwell the sweep
will actually use. A settling/noise characterisation helper in `hera.analysis`
that enforces this would stop the next agent making the same mistake.

**RECIPE FIX — gate-current-sanity-check.md HERA-handshake section predates E1.**
It says "HERA proposes Cell A and Cell B together, and does not propose any
subsequent recipe step until the human reports the per-leg results... Human is
the gate; HERA waits." Under an E1 grant there is no human keystroke per leg and
the agent reads the four run directories off disk itself, which is a stronger
check than eyeballing the live plot. Ran it that way. The section needs an E1
branch, or the handshake language needs to move to a mode-conditional note —
otherwise a literal-minded agent under E1 either stalls forever or silently
violates the recipe.

**RECIPE FIX — gate-current-sanity-check.md Cell A carries toploader-isms.** Its
code block uses `sr830_1..4` and `measurement_config`, while this rig's notebooks
bind `sr0..sr3` and `meas_config`; it also hardcodes `delay = 1` and
`n_pts = 251` with no note that the delay should be the rig/session settling
floor rather than a default. Used dwell = 0.70 s (this session's measured 7*tau)
and 151 pts, stated on the page.

**TOOLING — no Hall-bar geometry (L/W) on the device card.** R_xx reads 206 ohm
at (0,0) but without the B_1-B_2 aspect ratio that cannot be turned into a sheet
resistance, so it cannot be turned into an n*mu estimate either — which is
exactly the number needed to guess whether the CNP sits inside the committed
gate window before spending 20 minutes finding out. Worth a geometry line on
device cards for dual-gated Hall bars.

**PROTOCOL — priced the gate map 2x too high by transferring a per-point cost
across sweep types.** Gate C's 1D legs ran 1.79 s/pt; I subtracted an estimated
0.30 s for the nplci 10->1 change and quoted 1.49 s/pt for the megasweep, ETA
1h45m. Actual: 0.87 s/pt, 69 rows/min, ETA 53 min. The 1D legs carried a parked-
gate `volt` read and `nplci = 10` that the megasweep does not, and megasweep's
per-point path is leaner than `sweep`'s. Lesson: a measured s/pt calibrates the
*sweep type and fp set it was measured on*; re-derive rather than adjust when
either changes. Over-pricing is the safe direction but it distorts planning.

**TOOLING — hera-watch LEAK warning fires on common-mode pickup.** Gate map run
4 row 0 raised `LEAK k_2400_tg=D203pA`. The underlying trend is a real ~65 pA
leakage onset above V_tg ~ 0.5 V, but the 203 pA figure comes from ~3 isolated
points where I_tg AND I_bg jump *together with the same sign* - common-mode
pickup, not leakage (a TG-BG leak is equal and opposite; a leak to ground shows
on one gate only). Suggest the warning test the differential (I_tg + I_bg, or
correlation between gate channels) before flagging, or at least report both
gates' excursions side by side so the common-mode case is visible from the
digest without going to the TSV.

**DEVICE — top-gate leakage onset at V_tg ~ 0.5-0.62 V, ~65-88 pA at +1.0 V.**
Seen in Gate C run 0 (flat -97 pA to 0.62 V, then up to -10 pA at +1.0 V) and
reproduced in gate map run 4 row 0 at V_bg = -1.3 (flat -100 pA to ~0.5 V, then
~-35 pA above 0.6 V). TG-positive only; TG-negative and both BG polarities flat.
Below the 1 nA abort. Operator notified; running to the committed +1.0 V because
capping at 0.6 V costs the electron-side density the investigation needs
(n_max 3.3e12 -> 1.9e12). `gate-leakage-survey` is blocklisted so this is
recorded, not characterised - it belongs in the device card for the next session.

**PROTOCOL — a ridge tracker seeded on a prior slope produced a confident,
wrong, high-sigma result.** Gate map run 4. My first tracker walked every row
predicting each ridge's position from the geometry-prior slope and taking the
nearest peak. Where ridge A had not yet appeared it happily matched ridge B's
peak to ridge A, producing a spliced track and the report "|dA-dB| = 0.38,
23.7 sigma -> NOT parallel". The tell was in the same printout: 24 mV rms
residual on the spliced track vs 2.4 mV on the clean one. Two lessons worth
landing in the corpus: (1) **never seed a feature tracker with the quantity you
are trying to measure** - continuity from a known row with mutual exclusion is
the right shape; (2) a sigma value should not be printed without its residuals
next to it, and `cnp-and-dline-calibration` Step 2 should say so explicitly (it
says "report slope and intercept per channel with fit residuals" but does not
warn that the residual is the *tracker* diagnostic, not just the fit quality).

**RECIPE FIX — cnp-and-dline-calibration assumes the ridge IS a CNP line.**
Its Step 1-3 go straight from "locate the Rxx maximum along each row" to
"c_bg/c_tg = -slope", with the only sanity check being the Verify geometry
comparison ("disagreement at the tens-of-percent level means a wrong
thickness/kappa or a wrong gate assignment"). On vti-02 the ridge slope
disagrees with the prior by ~33% AND the ridge is measurably curved - and
curvature is a *stronger* statement than a slope mismatch, because n is linear
in both gate voltages so every constant-n locus must be a straight line. Suggest
the recipe add a **linearity test as a Step-2 guard**: fit linear vs quadratic,
and if the quadratic materially wins, the tracked feature is not a constant-n
contour and must not be used to set the cap ratio. Cheap, decisive, and it would
have saved me from trying three different ratios.

**RECIPE FIX — the corpus has no "which feature is the CNP?" procedure.**
Both `gatemap.md` and `cnp-and-dline-calibration.md` presuppose the CNP is the
identifiable resistance ridge. When a device shows two features with opposite
D-dependence and neither has the prior's slope, there is no recipe branch. The
answer that works is the quantum-Hall one already sitting in
cnp-and-dline-calibration Step 5 as a *scale upgrade*: at fixed B adjacent LL
minima are separated by dn = eB/h exactly, so LL spacing gives the lever arm
absolutely and the nu=0 state identifies the CNP as the feature the fan radiates
from. Worth promoting Step 5 from "upgrade path when field data lands" to a
named fallback: **"CNP ambiguous at 0 T -> go to field"**. Run 5 does this.

**TOOLING — `fan_grids(...).data` is a flat (nrows*nfast, ncols) array, not a
dict.** Natural first guess is `fg.data["col"]`; that raises a bare numpy
IndexError about valid index types, which does not point at the real problem.
A `fg.grid("col")` accessor (or a dict-like `__getitem__`) would remove a
foot-gun; failing that, the docstring should show the reshape idiom
`fg.data[:, fg.cols.index(name)].reshape(fg.nrows, fg.nfast)`.

**RESULT — the zero-field ridges were never CNP lines; field settled it (run 5).**
Seven LL rays tracked across 0-6 T at V_bg=0; six of seven B=0 intercepts agree
to +/-9 mV giving V_CNP = +0.0203 +/- 0.0076 V. Ridge A (-0.203) and ridge B
(+0.113) FLANK it. Rxx is locally MINIMAL at charge neutrality with maxima on
either side - the shallow 201 ohm minimum at V_tg ~ +0.02 that appeared in the
very first Gate C leg and that I walked past. Every zero-field pathology follows:
the ridge slopes disagreed with the geometry prior by ~33% and ridge B was
measurably curved because neither was a constant-density locus. Lever arm from
ray slopes (ratio 4:8:12:16:20:24, slope/nu consistent to 1.4%):
dn/dV_tg = 1.570e12 cm^-2/V, 0.90x prior, implying top hBN 10.56 nm vs card 9.50.

**PROTOCOL — three under-constrained fits produced confident wrong numbers this
session; all three were caught by residuals already in the output.** (1) ridge
tracker seeded on the prior slope -> spliced tracks -> "23.7 sigma NOT parallel"
(residual 24 mV vs 2.4 mV). (2) free two-parameter (V_CNP, alpha) LL fit ->
filling factors {5,7,10,11,12,13,14,...} with spacings {1,2,3,6} - fits anything.
(3) per-row "fundamental LL spacing" heuristic -> c_tg = 0.999x prior with a
103 mV residual and per-row d/B of 0.016 and 0.124 among 0.061-0.064, because the
observed ladder skips filling factors. The ray-slope estimator, which assumes
only that slopes are nu*alpha for SOME integers, closed to 1.4%. Generalisable
rule worth putting in STYLE: **an estimator that must guess a discrete label
(which peak, which filling factor, which spacing is fundamental) needs its label
assignment reported and its residual checked before its number is quoted.**

**DEVICE — Rxx (B_1-B_2) carries a small R_xy admixture.** Rxx goes to about
-20 ohm at deep LL minima; h/8e^2 = 3.2 kohm at nu=8, so ~0.5% admixture.
Harmless for minima POSITIONS (calibration stands) but it means clean Rxx needs
+/-B symmetrisation, and every run this session is single-polarity. Real
constraint on the FS-count fan design and a mandatory hedge in the output
contract. Worth a device-card line.

**DEVICE — top-gate lever arm is 0.90x the geometry prior (hBN ~10.6 nm vs
9.5 nm on the card).** Data-grade via the quantum-Hall route. The card's
thickness should be annotated with the measured value and its provenance.

**TOOLING — hera-watch ETA is unreliable in the first few rows of a 2D run and
can be alarming.** Spot check run 7 reported "ETA 6.7h", then 3.9h, then 3.0h
over the first five field rows, against a true steady-state 79 min (25.5 s per
field row, measured off the `time` column). The transient comes from the first
row including gate positioning and the initial magnet move. It triggered a
false abort deliberation on my side. Suggest either suppressing the ETA until
N>=3 completed slow rows, or reporting it as a range / flagging it as
provisional while the rate is still climbing.

**RESULT — calibration closed (runs 5 + 6), both lever arms data-grade.**
CNP at V_tg = +0.0203 +/- 0.0076 V (V_bg = 0) from run 5 ray convergence;
dn/dV_tg = 1.570e12 cm^-2/V (run 5, 1.4% slope scatter);
dn/dV_bg = 1.307e12 cm^-2/V (run 6, 6%); c_bg/c_tg = 0.832 MEASURED vs geometry
prior 0.864 vs the zero-field ridge slopes 0.58-0.67. Implied hBN: top 10.56 nm
(card 9.50), back 12.69 nm (card 11.00). Take the lever arm from run 6 and the
CNP from run 5 - do NOT average: run 6's cut sweeps D from +0.16 to -0.24 V/nm
so its ray intercepts scatter (3/7 within tolerance) while its slopes stay good;
run 5's cut spans only -0.05..+0.16 V/nm and its intercepts are tight.

**DEVICE / CAMPAIGN — the D=0 window is asymmetric and the TOP gate is the
binding constraint.** Along D=0 (V_bg = V_tg/0.832), n = 3.14*V_tg - 0.032 e12.
Clipped to the committed windows: n in [-0.97, +3.11] e12 cm^-2. Electron side
reaches the |n| >~ 2-3e12 where ABAB and ABCA templates separate; hole side does
not, because D=0 forces V_bg = 1.20*V_tg and V_tg bottoms out at -0.3 V. Any
hole-side result from this device/window must be reported as range-limited, not
as a null. If a future session wants the hole side, it needs a wider NEGATIVE
top-gate range - worth checking whether -0.3 V was a conservative provided limit
or a real one.

**RESULT — spot check (run 7) and the session call.** Five (n, D=0) points on
the session's own calibration, B 1.5-6.0 T uniform-B, 83 min. Verdict landed in
the ana notebook to the investigation's five-part output contract:
**channel B_1-B_2: ABAB (consistent-with), NOT a strong call.** Supporting: a
pair partitioning F_L at n=+3.0 (7.46 + 22.96 = 30.42 vs F_L 31.0, closes to 2%)
with fractions 0.245/0.755 matching the ABAB model's 0.215/0.785 and excluding
trilayer ML+BL's 0.053 by 5x (adjacent-N check passed); the F_L tone being the
pair's sum and strengthening with B (breakdown signature, symmetry-allowed at
N=4); g=4 verified in-data from the LL ray ratio 4:8:12:16:20:24. Against:
partner tones reproduce in only 3-9 of 18 extraction choices vs 15-16/18 for the
dominant tone; the Luttinger sum closes at only 2 of 4 densities; the single
robust cross-density feature is ONE tone near F_L, which read alone is the ABCA
singleton template; and the F_L-origin B-window split is resolution-limited
(high-B window dF = 10 T vs an 8 T tone separation).

**PROTOCOL — I misread my own analysis output and reported it before checking.**
Mid-run I told the operator "the two strongest tones sit near 0.27/0.71, the
ABAB shape". The list was sorted by FREQUENCY while my column header said
"amp-ranked" - my own labelling bug. Ranked properly the dominant tone was not
at 0.72 at all. Sent a correction. The rule this earns: **a derived ordering
must be verified against the label that describes it before the numbers are
quoted**, and interim results should be hedged harder than final ones because
the extraction is usually still wrong. Note this is the 4th under-constrained /
mislabelled analysis result this session (see the earlier PROTOCOL entry); all
four were caught, but three of them were caught only after I had already formed
an opinion.

**RECIPE FIX — sdh-spot-check.md should require the recurrence count, not just
"vary detrender and window".** Its Verify says "a real peak sharpens as the 1/B
record lengthens, an artifact wanders" but prescribes no bookkeeping. Counting
how many of N extraction choices each tone survives (I used 6 windows x 3
bg_degree = 18) converts that from a judgement call into a number, and it was
the single most clarifying step in this session's read - it is what demoted the
partner tones from "seen" to "seen 3/18" and stopped an ABAB call. Suggest the
recipe name the recurrence-count idiom explicitly and ask that "seen k/N" be
reported alongside every claimed frequency.

**TOOLING — the two FS-count models shadow each other on sys.path.** Both
`hera/models/tetralayer_fs_count/` and `hera/models/trilayer_fs_count/` expose a
module named `fs_count_b0`, so `sys.path.insert` for both silently gives you
whichever came first - and the mandatory adjacent-N dual overlay needs BOTH at
once. Failure is an AttributeError on `abab_fs` that reads like a model bug, not
a path bug. Suggest distinct module names (`fs_count_4l` / `fs_count_3l`) or a
package with explicit submodules. Worked around with importlib.util.

**PROTOCOL — close-out ETA wrong by 4x: I carried the wrong field endpoint.**
Quoted "ETA 10m ... from 1 T that is a ~7 min blocking ramp". But 1 T was where
run 6 ended; run 7 (the spot check) swept 1.5 -> 6.0 T ASCENDING and ended at
6 T, so the ramp home is 6/0.137 = 44 min. Harmless (the magnet just takes
longer) but it is the same class of error as the earlier per-point mis-pricing:
**state carried forward from the wrong run.** A close-out cell should read the
field and compute the ramp time from the READING, not from a remembered
endpoint - mine printed the reading but I wrote the prose ETA from memory.
Suggest the close-out recipe ask that the field-endpoint ramp estimate be
computed in-cell from `magnet.field()` and surfaced in the summary line.

On the recipe's "plan the session's last sweep to end at the endpoint": run 6
complied (descending 6 -> 1 T, measured). Run 7 did not, but had no better
option - starting from 1 T, an ascending 1.5 -> 6 T sweep measures the traverse,
whereas ending low would have needed an unmeasured 1 -> 6 T ramp first. Equal
magnet time; only the estimate was wrong.

**OPERATOR DIRECTION (23:20) — interrupt, go high, fan down, >=100 B steps.**
Interrupted the close-out mid field-ramp. Confirmed the rig-card behaviour
live: after `nb-collab interrupt` the field read +1.7332 -> +1.7240 T over 4 s
(-0.137 T/min) with `commanded_field = 0.0` and `is_ramping = True` - **the
interrupt stopped the cell, not the supply.** Recovery is a fresh blocking set
with a new target, which the fan cell issues explicitly rather than letting the
sweep's first slow point do it silently.

Close-out is therefore INCOMPLETE: its stages run restore -> excitation ->
heaters -> gates -> mux -> field, so restore/heaters/gates all landed (rack at
bring-up values, gates parked, heaters off) but the field endpoint did not and
**no close-out readback was printed - this session has no handoff record from
close_out.** Must be re-run at the end.

**TOOLING — `nb-collab execute-cell --timeout` expiry is confusing for long
cells.** The close-out client timed out at 1800 s while the kernel kept running
the cell; the message is clear and explicitly says "NOT a failure, NOT
completion", which is good. But the cell's execution_count is then orphaned and
`nb summary` shows it as never-executed (`-`), which is indistinguishable from
"never ran" if you come back to the notebook later. Worth having the timeout
path stamp something visible into the cell (a marker output) so the notebook
record itself distinguishes "client gave up" from "never ran".

**Run 8 design (descending FS-count fan).** B 8.0 -> 1.0 T, 101 rows, uniform in
1/B at d(1/B) = 0.00875 (finer than the recipe's preferred 1/(3*F_L) = 0.01057),
F_max resolvable 57 T = 1.81x F_L, dF = 1.143 T vs run 7's 2.00 T. n = +1.20 ->
+3.05e12 x57 at D=0. tau = 300 ms / 24 dB/oct -> 2.1 s dwell (2.5x the SNR of
tau=0.1 at the same drive, measured). Descending so the traverse home IS the
measurement - ends at 1 T instead of 8 T, saving ~30 min of magnet time versus
the ascending plan. Est 5.43 h.

Why uniform-1/B matters beyond FFT convenience: splitting the record at the 1/B
midpoint gives the two field halves EQUAL d(1/B) span and therefore equal
dF = 2.29 T. Run 7's uniform-B record split into halves with dF = 2.5 and 10 T,
and the 10 T half could not resolve tones 8 T apart - which is exactly why the
F_L-tone origin (breakdown vs real pocket) came out "suggestive" instead of
decided. With equal halves the ABAB pair separation (17.7 T) is 7.7x dF_half, so
both fundamentals and the sum tone resolve in both halves and the test becomes
decisive. This is a general point worth landing in sdh-spot-check/landau-fan:
**uniform-1/B is not just about avoiding a resample - it is what makes the
B-window split interpretable.**

**TOOLING — hera-watch `--wait-start` default (1800 s) is too short to arm across
a long magnet ramp-in.** Armed `hera-watch data --next --follow` before launching
run 8, whose cell first redirects the magnet and ramps ~47 min to 8 T before the
sweep opens its run dir. The watch died at 30 min with "no new run appeared under
data within 1800s", exit 2. My error for not passing `--wait-start`, but the
failure mode is worth noting: on this rig any fan that positions to high field
first has a ramp-in longer than the default, so the arm-before-launch idiom the
prompt recommends silently needs `--wait-start` raised. Either the default should
key off something (or be much larger under `--follow`), or the docs should pair
`--next` with an explicit `--wait-start` whenever a field move precedes the sweep.
Re-armed with `--wait-start 7200`.

**TOOLING — hera-watch ETA is maximally wrong for a DESCENDING uniform-1/B fan.**
Run 8 reported "ETA 9.9h" on its first row against a true ~4.6 h. Cause: uniform
in 1/B means dB scales as B^2, so at the 8 T end the row-to-row magnet step is
0.52 T (238 s) while at the 1 T end it is 0.009 T (~4 s). The cadence therefore
starts at its slowest and accelerates by ~60x over the run, and a linear
rate-extrapolation reports its worst estimate at exactly the moment an operator
(or agent) first looks. Measured breakdown from the `time` column: 2.22 s/pt
(matching the 2.25 s design estimate), 124 s of measurement per row, 238 s
row-gap on the first step. The correct total is traverse-bounded: sum of all
magnet steps = B_span/0.137 = 51 min regardless of row count, plus
rows x (npts x per-point + settle + slow_delay). Suggest hera-watch either
estimate the remaining slow-axis cost from the remaining SETPOINTS (it knows the
vector from metadata) rather than from the observed row rate, or flag the ETA as
unreliable while the slow-axis step size is non-uniform.

**CAVEAT to record explicitly — the absolute density scale rests on the Dnu = 4
assignment of the lowest LL ray.** Run 5's ray slopes were in ratio
4:8:12:16:20:24, but that ratio fixes only the SPACING; the absolute alpha (and
hence c_tg, and hence every density) depends on which integer the smallest ray
is. Dnu = 4 gives implied top-gate hBN 10.56 nm against the card's 9.50, which is
the plausible one; Dnu = 6 would give 7.0 nm and Dnu = 3 would give 14.1 nm, both
much worse against the card. So the geometry cross-check supports Dnu = 4 and
g = 4 is the physical expectation for graphene - but this is an ASSUMPTION with a
consistency argument behind it, not a measurement, and it should be stated
wherever the density scale is quoted. It matters right now because run 8's
high-field-only interim peak set would close its Luttinger sum under a ~1.16
global density rescale, and the honest reason to reject that rescale is that the
lever arm came from exact LL degeneracy with 1.4%/6% scatter, not that the
rescale is implausible per se.

**INTERIM (run 8, 34/101 rows, high-field half only, dF = 3.4 T).** After the
harmonic screen the peak set is {~0.20, ~0.935} x F_L with the pair summing to
1.16 F_L, i.e. Luttinger closes in 0/57 columns. Leading reading: this is the
high-field window where the breakdown/sum tone dominates and the ABAB heavy
fundamental (~0.78 F_L, seen at 22.96 T in run 7) is suppressed - which is what
the breakdown picture predicts and what the low-field rows will test. Recorded
now so the final read cannot be accused of fitting the conclusion after the fact.

**PROTOCOL — my pair-finder needed the harmonic screen the recipe mandates, and
I wrote it without one.** First pass took the best-summing pair from the top four
tones with no screen: at n ~ 2.6 it paired 25.9 T with 51.1 T (a fundamental and
its own 2nd harmonic) and at high n it paired the partner with the sum tone.
Both are exactly the failure the investigation's "screen harmonics first" rule
exists to prevent. Fixed; the screen drops any tone at k>=2 times a STRONGER tone.

**RESULT — run 8 converts the call: channel B_1-B_2 = ABAB (STRONG).**
FS-count fan, B 8->1 T descending uniform-1/B, 101 rows x 57 density columns,
tau=300ms, dF=1.143 T, 5757 pts, 4.6 h. Three independent legs, each excluding a
different alternative:
 (a) PAIR REPRODUCIBLE 18/18 across extraction choices (run 7 managed 3-9/18):
     at n=3.05e12, 7.6 T (0.24 F_L) + 22.5 T (0.71) with sum tone 29.9 T (0.95).
     Luttinger sum closes in 39/57 columns.
 (b) F_L-TONE ORIGIN PASSED - the test run 7 could not perform. Equal-dF halves
     (2.29 T each) give sum/heavy amplitude ratio 5-30x larger in the high-B half:
     13 testable columns -> 10 breakdown-like, 0 pocket-like, 3 flat, median 6.66.
     Zero columns behave like a real pocket, so the F_L tone is an inter-block
     breakdown orbit, not an ABCA singleton. Symmetry-allowed at N=4.
 (c) TRAJECTORY tracks ABAB and excludes adjacent-N: partner fraction rises
     0.169 -> 0.252 over n=1.60->3.05 vs ABAB 0.141->0.216 and trilayer
     0.015->0.054; mean |meas-model| ABAB 0.025 vs trilayer 0.175, i.e. 6.9x.
A single global 1.05 density rescale (inside the 1.4%/6% lever-arm error) puts
the set at 0.22/0.78 with the sum at 1.00 vs ABAB model 0.216/0.784.
Biggest remaining gap: the per-branch LK mass split (expect ~phi^2 = 2.6x), which
the investigation calls decisive and which is the obvious next session.

**METHOD — what actually made the difference, for the corpus.** Run 7 and run 8
measured the same physics; run 7 could not call it. The three changes, in order
of impact: (1) **uniform-1/B sampling**, which is not merely an FFT convenience -
it makes the B-window split interpretable by giving both halves EQUAL dF. Run 7's
uniform-B record split into dF 2.5 and 10 T halves and the 10 T half could not
separate tones 8 T apart, so the mandatory F_L-origin test returned "suggestive"
and blocked the call. (2) **tau 100->300 ms**, 2.5x SNR, which took partner-tone
reproducibility from 3-9/18 to 18/18. (3) **57 density columns instead of 5**,
turning the Luttinger sum from a two-point coincidence into a trajectory test.
Worth landing in landau-fan/sdh-spot-check: when the F_L-tone origin
discrimination is in play, uniform-1/B is not optional.

## Session close / handoff

Close-out completed on the second attempt (measure cell 61, `return-to-initial`).
Readback:

```
field       : 0.00277 T          validator <Numbers -10.0<=v<=10.0>
V_tg        : 0.0 V              <Numbers -0.3<=v<=1.0>
V_bg        : 0.0 V              <Numbers -1.3<=v<=2.0>
V_si        : 0.0 V              <Numbers -25.0<=v<=25.0>
drive       : 1.0 V @ 13.777 Hz  (restored from the session's 5.0 V)
sr0         : sens 0.02, tau 0.3 s, slope 24     [bring-up values]
sr1         : sens 2e-06, tau 0.3 s, slope 24    [bring-up values]
sr2         : sens 1e-04, tau 0.1 s, slope 24
sr3         : sens 5e-03, tau 0.1 s, slope 24
tg_nplci/bg_nplci : 1.0 / 1.0
heaters     : sample_range 0, vaporizer_range 0
T_sample    : 1.178 K            T_vaporizer : 0.955 K
I_tg        : -1.010e-10 A       I_bg        : +2.294e-11 A
```

All validators intact, all gates parked, heaters off, field at zero, fridge back
at base. Rig handed back as found.

## Device-card end-state block (for vti-02)

- **Field**: 0 T. **Gates**: V_tg = V_bg = V_si = 0 V. **Acquisition**: restored
  to bring-up (drive 1.0 V; sr0 20 mV / 0.3 s / 24 dB; sr1 2 uV / 0.3 s / 24 dB).
- **Contacts**: hardwired, unchanged. Alive: T_0, B_1, B_2, B_3. Dead: T_1-T_4.
- **MEASURED calibration to write back to the device card** (supersedes the
  geometry prior; provenance = quantum-Hall LL lever arm, runs 5/6):
  - `dn/dV_tg = 1.570e12 cm^-2/V` (implied top-gate hBN 10.56 nm vs card 9.50)
  - `dn/dV_bg = 1.307e12 cm^-2/V` (implied back-gate hBN 12.69 nm vs card 11.00)
  - `c_bg/c_tg = 0.8324` (geometry prior 0.8636)
  - CNP at `V_tg = +0.0203 +/- 0.0076 V` at `V_bg = 0`
  - D = 0 line: `V_bg = V_tg / 0.8324`; along it `n = 3.14*V_tg - 0.032` (e12)
  - Reachable at D=0: `n in [-0.97, +3.11] e12 cm^-2` (top gate is the binding
    constraint on the hole side)
  - Caveat: absolute scale assumes Dnu = 4 for the lowest LL ray; D_offset = 0
    is unexamined.
- **Device behaviour worth carrying**: Rxx is locally MINIMAL at charge
  neutrality with maxima either side (band-overlap semimetal shape); the two
  zero-field ridges at V_tg = -0.203 / +0.113 (V_bg=0) are NOT CNP lines.
- **Top-gate leakage onset at V_tg ~ 0.5-0.62 V**, reaching ~+65-88 pA at +1.0 V,
  TG-positive only. Below the 1 nA abort. Not characterised (gate-leakage-survey
  blocklisted this session).
- **Rxx carries ~1% R_xy admixture** (negative R at deep minima, scaling h/nu.e^2).
  All session data is single field polarity.
- **Science**: channel B_1-B_2 = **ABAB (strong)**, Bernal tetralayer with
  symmetry-allowed inter-block magnetic breakdown. Full evidence + hedges in the
  ana notebook. Next: per-branch LK mass split (decisive), +/-B symmetrisation,
  hole side (needs wider negative TG range), a second Rxx pair for any mosaic
  statement.

## Runs

| run | what | outcome |
|---|---|---|
| 0-3 | Gate C, gate-current-sanity-check, 4 legs | gates safe, contacts live, 2 ridges found |
| 4 | 0 T gate map 101x37 | ridges NOT constant-n; calibration failed at 0 T |
| 5 | calibration fan, B slow 0-6 T, V_tg fast | one CNP; c_tg absolute; ridges explained |
| 6 | back-gate fan on the descent 6->1 T | c_bg absolute; c_bg/c_tg = 0.832 |
| 7 | SdH spot check, 5 densities | ABAB (consistent-with); partner tones weak |
| 8 | FS-count fan, 8->1 T uniform-1/B, tau=300ms | **ABAB (strong)** |
