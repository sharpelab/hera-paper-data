# Session notes — vti-02 / VTI

Operational log (not a science notebook).

## 2026-08-24 — bring-up

**TOOLING — `fp()` gain vs the analysis layer's gain division.** `docs/api/measureme.md`
says `follow_param(param, gain)` stores `param()/gain`, while `hera.watch` /
`hera.analysis.resolve_channels` both compute the physical value as
`column / srN_gain` with the gain taken from `measurement_config` (and
`hera.watch` computes its rail warning as `max|X|/sensitivity` treating the column
as **raw volts**). Passing a gain to `fp()` for a lock-in channel would therefore
double-divide. Convention adopted this session: **`fp()` lock-in X/Y with gain=1
(raw volts on disk); the gain lives only in `measurement_config`.** The API doc's
line "For a true-current channel follow it with gain=1" is the only hint of this
and reads as the exception rather than the rule — worth a doc fix.

**METHOD — settling floor is the session's dominant cost.** Bring-up state
(measure cell 27): sr0/sr1 tau = 0.3 s at 24 dB/oct. STYLE rule 12 puts the
compliant dwell at 7–10 tau = 2.1–3.0 s/pt, which prices even a coarse
66 x 45 gate map at ~2 h. At the 13.777 Hz drive, tau = 0.1 s still gives ~-50 dB
of 2f rejection and ~10^3 SNR on a 10 uV signal, so the ask to the operator is
tau 0.3 -> 0.1 s on sr0+sr1 — a 3x saving across every sweep this session.

**METHOD — sr1 sensitivity is set for a much smaller signal than this bias implies.**
sr1 sens = 2 uV; with the 1.0 V drive through the 100 MOhm bias resistor
(I_bias = 10 nA), a few-kOhm Rxx puts 10s of uV across B_1-B_2, i.e. 5-15x full
scale. Flagged as an ADVISORY inside VERIFY (informational, not a verdict gate —
it is a tunable, not a safety surface) rather than silently sweeping into a railed
channel.

**E1 grant.** Operator said "go for autonomy" 2026-08-24. Kernel probe (measure idx 31)
printed `PROBE: BOUND` — pid 36068, cwd = the measurement dir, all 9 instruments live,
namespace complete. VERIFY (measure idx 33) printed **`VERIFY: ALL GREEN`**: magnet
+0.0060 T with psw+output on, all 7 SAFETIES validators numerically equal to the device
card, thermometry worker live (age 3 s / period 5 s), T_sample 1.170 K, both heater
ranges 0, T_vaporizer 0.948 K, no mux in the kernel and WIRING == card, DC205 RNGE 2 /
output on / 0.0000 V. E1 engaged on that printed verdict.

**TOOLING — `sweep.BASEDIR` reads `None` after `sweep.set_basedir()`.** The probe printed
`sweep BASEDIR : None` even though setup cell 3 called `sweep.set_basedir(<dir>/data)`.
`import sweep` re-exports via `from .sweep import *`, which copies the value at import
time, so the package-level name is a stale snapshot while the live global lives in
`sweep.sweep`. Harmless for `Station()` (it reads the real global), but it makes the
package-level name useless as a check. Every station this session is constructed with an
**explicit `basedir=`** so run placement never depends on it.

**METHOD — probe used `state0.get(...)`; `read_state` returns a `StateRecord`, not a dict.**
Non-fatal (guarded by try/except, probe still reported BOUND), but the state0 line printed
an AttributeError instead of the gate voltages it was meant to echo.

## 2026-08-24 — measurement

**FEEDBACK — operator delegated the lock-in settings.** I asked (Slack) for sr1 sens
2 uV -> 1 mV and sr0+sr1 tau 0.3 -> 0.1 s as front-panel work; Zack replied "You can
change the sr1 sensitivity/time constant via the qcodes api in a cell. you are authorized
to use the values you think are best." Done in measure cell 37 with readback asserts. Note
the rig card says tau/filter_slope are "operator-set on the front panel and not set by the
kit" — that is a *convention*, not a hardware constraint, and this operator was happy to
delegate it. Worth softening the rig-card wording to "operator-owned by default; ask" so a
future agent asks rather than assuming the knob is unreachable.

**METHOD — the current channel cannot find the CNP under a 100 MOhm current bias.** I
planned run 0 to locate the CNP from the sr0 drain current while sr1 was railed. That was
half-wrong. With R_bias = 100 MOhm defining the current, dI/I = -dR_2T/1e8, so the channel
going 100 ohm -> 100 kOhm moves I by 0.1%. The CNP *was* visible in I (a 0.7% dip) only
because the CONTACTS dominate R_2T here (~0.4 MOhm each) and roughly double through the
CNP — not because the channel did anything measurable. The four-terminal Rxx is the only
real locator. General rule for this rig: under a high-impedance current bias the drain
current is a contact-resistance probe, not a channel probe.

**TOOLING — a 2D live plot kills long megasweeps (run 2, cost ~1 min).** Adding
`s.plot(fast, y, slow)` (the z-argument mesh) to a 2310-point megasweep killed it at point
3 with `BrokenPipeError: [WinError 232]` out of `Plotter.add_point`. `sweep/plot.py`'s mesh
branch does `ax.clear()` + `griddata(...)` + `pcolormesh(...)` on EVERY measured point,
re-interpolating the whole accumulated set — O(N^2) in the plotter subprocess — and is
degenerate while the slow axis still holds one unique value. Runs 0/1 with seven 1D
channel plots and no z completed fine, isolating the 2D call. Two lessons: (1) never give a
long megasweep a 2D live plot on this stack; (2) more general — a live-monitor crash should
not be able to destroy a measurement, `Plotter.add_point` failures ought to be swallowed
and the monitor disabled rather than propagated into the sweep loop. Worth an upstream fix.

**TOOLING — hera-watch made the failure cheap.** It reported `partial: 3/2310` and exited
rather than hanging until its deadline, so the dead sweep surfaced in ~1 min instead of at
the 42 min ETA. The `--next --follow` arm-before-execute pattern is doing exactly what it
should.

**METHOD — I nearly recorded noise as physics; the right test is the noise-only prediction.**
First pass at run 0 vs run 1 I quoted std/mean over the metallic window (11-13 %) as
"scatter" and, seeing the two traces track each other by eye, wrote in the ana notebook that
the wiggles were reproducible mesoscopic structure. Both halves were wrong. std/mean over a
window where R has a real slope measures the slope, not the scatter; the per-point sigma
comes from std(diff(R))/sqrt(2) and is 2.2 / 3.2 ohm (2-3 %). And the correct reproducibility
test is whether the run-to-run rms difference EXCEEDS hypot(sigma0, sigma1): observed
4.46 ohm vs 3.83 ohm predicted by pure independent noise, leaving only ~2 ohm of real excess.
So the wiggle is essentially all lock-in noise (32 nV = 36 nV/rtHz input-referred at the
0.78 Hz ENBW, i.e. plain SR830 1/f at 13.8 Hz). Corrected the ana cell + take (ana is
edit_exec) and set the believability floor at ~3 % for this configuration. Lesson worth
carrying: "the two curves look like they wiggle together" is not evidence; compare the
run-to-run difference against the noise-only prediction before calling anything structure.

**TOOLING — hera-watch's ETA is badly wrong for a 1/B-uniform field fan (run 4).** At row 0
it reported "7.6 row/min ETA 3.9h" for a fan I had priced at 1h30m. Two compounding causes:
(1) the average rate includes the 5.4 min initial ramp to the first field, and (2) with rows
uniform in 1/B the per-row field step GROWS along the sweep (0.017 T -> 0.913 T here, i.e.
8 s -> 400 s of ramping per row), so a linear extrapolation of elapsed/rows is structurally
wrong, not merely noisy. Modelling it by hand (sum of per-row ramp time + points x s/pt)
gives 81-105 min. Suggestion for the tool: when the slow param is a magnet, compute the
remaining ramp time from the actual remaining setpoints and a known slew rate rather than
extrapolating the observed average; or at minimum suppress the ETA until the first two or
three rows have landed. As it stands the number invites an unnecessary abort.

**METHOD — following magnet.field per point is not free.** Run 3 (gates only) ran at
0.855 s/pt; run 4 adds a co-swept second Keithley on the fast axis plus fp(magnet.field)
and is running near ~1.6 s/pt. The magnet read is a TCP round trip to the FastBi supply.
It is still the right call here — the rig card is explicit that this supply's setpoint is
not readable as field, and SdH analysis wants true B — but the cost should be priced in
(~0.4-0.7 s/pt) rather than assumed negligible, and for a gates-only sweep it should be
left out.

**METHOD/TOOLING — the duplicate-column trap bit me, silently, and `FanGrids.grid()` is
where it hides.** In run 4 (multimegasweep with `magnet.field` as the slow axis AND
`fp()`-followed) the column name `magnet_field` appears TWICE: once as the planned slow
setpoint, once as the measured readback. `hera.analysis` documents that `Run.col()` RAISES
on duplicates and must be resolved with `col_indices`/`col_at` — but `FanGrids.grid()`
silently resolves to the FIRST occurrence, i.e. the setpoint. So `fan.grid("magnet_field")`
handed me the commanded field while I believed I had the measurement, and the giveaway was
a suspiciously perfect `max |cmd-meas| = 0.0 mT`. Correct access is
`[i for i,c in enumerate(fan.cols) if c == "magnet_field"][-1]` into `fan.data`.

Caught it only because 0.0 mT was too good. Two consequences worth carrying:
- **Following `magnet.field` is genuinely necessary, not just defensible.** The measured
  field sits **+6.5 mT above the setpoint** with 2.2 mT of within-row spread — ~0.9 % at
  0.75 T, which would propagate straight into SdH frequencies. This supersedes my earlier
  note that treated the per-point field read as a cost to be justified: it is required.
- Suggestion for `hera.analysis`: `FanGrids.grid()` should either raise on a duplicate name
  like `Run.col()` does, or take an explicit `which="first"|"last"` — silently preferring
  the setpoint is the wrong default when the whole point of following a parameter is that
  its readback differs from its setpoint.

**METHOD — check FFT Nyquist before believing a tone.** The fan's 1/B record (0.75->6 T,
40 rows) gives resolution 0.86 T but Nyquist only ~17 T, while the Onsager frequency at the
top density (n = 2.09e12 cm^-2) is 21.6 T — those columns ALIAS. The analysis now computes
Nyquist from the actual record and refuses to interpret any column above it. The planned
down-sweep (100 rows, 0.5-6 T) has Nyquist 27.3 T and is the right instrument for the
pocket count; the fan is for the Landau-level sequence.

**METHOD — I over-claimed what a Landau fan can prove, and had to retract it mid-session.**
In the P4 proposing cell (measure idx 41) I wrote that LL degeneracy would discriminate ABCA
from ABAB: "a rhombohedral N-layer stack carries an N-fold orbitally degenerate zero-energy
level; for tetralayer ABCA that is 4x4 = 16 states, so the first flanking gaps fall at
nu = +/-8. A Bernal tetralayer decomposes into two bilayer-like sets whose levels arrive at
different fields, giving a visibly different sequence." **That is wrong.** ABAB tetralayer
decomposes into two effective bilayers, each with a 2-fold orbital zero LL x 4 spin/valley
= 8, and BOTH sit at exactly E = 0 -> 16 zero-energy states, identical to ABCA's 4-fold
orbital x 4. The zero-LL degeneracy is 4N for N layers **regardless of stacking order**: it
counts LAYERS, not stacking. The measure cell is append-only so the claim stands on the
page; it is corrected in the ana notebook, which is the science record.

**METHOD — the fan cannot separate the absolute density scale from the LL degeneracy.**
Both the SdH frequency (f = n_true*h/(g*e)) and the LL ladder spacing depend only on the
product alpha*g, where alpha = n_assumed/n_true is the error in the absolute gate
capacitance. Measured: ladder spacing 4.665 in nu_assumed and a dominant tone at 0.85x the
assumed-scale Onsager, i.e. alpha*g = 4.7 both ways — consistent, but degenerate. Breaking
it needs an absolute density measurement independent of degeneracy, i.e. the **Hall
resistance** (n = B/(e*Rxy)), and this cooldown has no Hall pair wired: sr2 and sr3 are
n.c., so the provided contact configuration cannot produce Rxy. Consequence for the
device/session template: **a stacking campaign that wants an absolute (n, D) calibration
needs a Hall pair in the provided configuration.** Worth flagging at session build, not
discovered at 14:40.

What the fan DOES establish alpha-independently: a **single** SdH tone whose frequency is
proportional to n through the origin, with no second tone that also scales with n. Two
Fermi pockets would give two such tones at a fixed ratio; the secondary FFT peaks here
(4.22, 9.69, 9.10, 2.64, 8.37, 4.61 T at increasing n) do not scale and are sidelobes.

**TOOLING — `nb summary`/`nb cells` read the ON-DISK notebook, which lags the live RTC doc.**
Three minutes after launching the T-ladder, cell 47 still showed execution count `-` and its
output was empty, which looked like the `append --execute` had silently failed. It had not:
the kernel was `busy` and `data/6` had already been written. JupyterLab's collaborative
document had not yet checkpointed to disk. **Authoritative liveness checks are the kernel
execution_state (`/api/sessions`) and the data directory, not the on-disk .ipynb.** Worth
saying in the prompt's "When things break" section — an agent that trusted `nb summary` here
would have re-launched a running 50-minute measurement on top of itself.

**Close-out readback (2026-08-24 16:10).** B = +0.00634 T (measured), psw on, output enabled;
V_tg = +0.00000 V, V_bg = +0.00000 V, V_si = +0.00000 V; gate leakage TG -98.2 pA / BG
+34.0 pA (unchanged from the session-start baseline of -101 / +24 pA); T_sample = 40.001 K,
T_vaporizer = 38.001 K, both heater ranges 0 (sample left cooling passively from the 40 K
ladder endpoint); sr0 sens 0.02 V tau 0.1 s slope 24, sr1 sens 0.001 V tau 0.1 s slope 24,
drive 1.0 V @ 13.777 Hz. Lock-in settings deliberately NOT restored to state0 — the
session-start values were wrong for this device (sr1 railed at 2 uV).

**METHOD — the T-ladder settled far better than the rig card's warning implied.** The rig
card records the sample loop as untuned with ~+1.4 K overshoot and bath-limited recovery, so
I built hover-on-stability acceptance with a 600 s cap. Every one of the six setpoints
settled to within 0.01 K of target with sigma ~0.002 K in about 140 s: 8.034, 12.042, 17.030,
23.011, 30.012, 40.008 K against setpoints 8/12/17/23/30/40. Either the loop has been tuned
since that note was written, or the +1.4 K overshoot is specific to the low-T end (all my
setpoints were >= 8 K, and the card's evidence was a ladder that "never passed below ~20 K"
using TOLERANCE settling). Hover acceptance cost nothing and would have saved the session if
the card had been right, so it stays the right default — but the card's settling paragraph
may be worth re-measuring.

**METHOD — a9 completeness guard: partial multisweep runs must never be reshaped.** The
ladder's 245-point path is offset0's 49 points, then offset1's 49, and so on. Reshaping a
STILL-WRITING run to (5, npts) silently interleaves different offsets and produces plausible
garbage — I caught it doing exactly that on run 6 at 100/245 points (it reported R_CNP
863-1194 ohm over D +0.053..+0.163, vs the true 230-3045 ohm over -0.100..+0.285). The guard
now compares r.rows against len(meta['setpoints'][0]) and skips incomplete or interrupted
runs. Any analysis that reshapes a concatenated multisweep needs this check.

**METHOD — I used the wrong statistic for the inversion-symmetry test and caught it in the
notebook.** First pass at Delta(D) I fitted a straight line to the D > 0.05 flank and read its
INTERCEPT as "Delta at D = 0", getting -1.12 meV and a printed line saying "ABCA requires the
intercept ~0". That is meaningless: Delta(D) is plainly curved near its minimum, so a linear
extrapolation from one flank has no bearing on where the minimum is. The correct statistic is
the MINIMUM LOCATION, from a parabola over the points around it: D = +0.016 +/- 0.004 V/nm,
against run 3's independent R_CNP minimum at 0.000 +/- 0.008. Fixed in the ana cell (ana is
edit_exec). General lesson: when the hypothesis is about WHERE a curve turns over, fit the
turnover, never extrapolate a flank.

**METHOD — the activation gap is 1-2 orders below the band gap, and that has to be said out
loud.** Delta_max = 1.36 meV at D ~ 0.25 V/nm, where a clean rhombohedral tetralayer should
show tens of meV. Combined with R_CNP saturating near 3 kOhm rather than rising exponentially,
this says transport is disorder- and parallel-channel-limited: in-gap states floor the
resistance well before the true gap matters. Ordinary for gapped graphene multilayers
(measured activation routinely 10-30x below the band gap) but it bounds the claim: the gap's
EXISTENCE and D-DEPENDENCE are established, its SIZE is not. The verdict is written that way.

**PROTOCOL — the append-only measure notebook cannot carry a retraction, and that is a real
gap.** I made a wrong physics claim in the P4 proposing cell (LL degeneracy discriminates
ABCA from ABAB; it does not — the zero-LL degeneracy is 4N and counts layers). The measure
notebook is append-only by design, so the erroneous claim stands on the page forever with no
marker. I corrected it in the ana notebook and in the final call, and I appended later measure
cells that do not repeat it, but a reader scrolling the measure notebook hits the wrong claim
with nothing to warn them. Resolved in-session: I appended an ERRATUM markdown cell (measure idx 50) naming cell 41,
quoting the wrong claim, correcting it, and stating that no measurement or datum is affected.
Append-only is preserved and the record is self-correcting rather than merely immutable.
Suggestion for the prompt/template: make this an explicit sanctioned move — 'a wrong claim in
an executed measure cell is corrected by an appended ERRATUM cell naming the cell id', so the
next agent reaches for it instead of assuming the record cannot be corrected.

**Mandated close-out (operator instruction, 2026-08-24 16:42).** Ran the canonical
`close_out((magnet.field, 0.0), restore=state0, heaters=..., gates=..., extra_readback=...)`
from `sharpelab_nb.closeout`, superseding my hand-written close-out at measure idx 49.
Final readback: field 0.0063380 T (validator -10..+10); V_tg 0.0, V_bg 0.0, V_si 0.0 (all
inside their committed validators); l335_3 sample_range 0 / vaporizer_range 0; T_sample
1.761 K AT THE TIME (still cooling from the 40 K ladder endpoint), T_vaporizer 0.949 K;
leak_TG -92.9 pA, leak_BG +25.3 pA (baseline); psw True, output True. All 22 state0
parameters replayed in capture order. **Thermal close-out completed separately — see the
entry below; the readback above was taken before the sample had returned to base.**

**FEEDBACK — operator required the mandated `close_out(restore=state0)`; I had hand-rolled
one instead.** I authored a bespoke close-out cell (idx 49) that did the brief's four actions
(field 0, three gates 0, heaters off, readback) but deliberately did NOT restore the lock-in
settings, reasoning that state0's values were wrong for this device (sr1 railed at 2 uV) and
that handing the next session a known-bad configuration was worse. The operator asked for the
mandated helper with `restore=state0`. Complied. Two lessons:
- The measure template's State-capture cell (idx 26/27) already says "`state0` above feeds
  `restore=`", and the Close-out cell (idx 28) says the close-out is "authored at session end
  per the brief's Close-out step (+ rig variant)". I read the brief's four bullet points as
  the whole specification and missed that the template intends `close_out()` as the vehicle.
  **The brief's close-out bullet should name the helper explicitly** ("author and run
  `close_out((magnet.field, <target>), restore=state0, ...)`") rather than describing the
  actions, so an agent does not reimplement it.
- `close_out()` is strictly better than my hand-rolled version: it enforces an explicit field
  endpoint (no silent default, `"hold"` must be deliberate), it checks the field param is not
  side-effected by the restore or stages, it dedupes touched params, and it prints validator
  ranges alongside every readback value. I should have looked for the helper before writing my
  own — the prompt's "Don't hand-roll analysis / check for a helper first" instinct applies to
  the operational surface too, not just `hera.analysis`.

**Consequence of the restore, flagged for the next session.** sr1 sensitivity is back to
**2 uV** and sr0/sr1 tau to **0.3 s** — the configuration in which sr1 was railed (fs = 1.01)
at the zero-gate operating point of this device at 10 nA bias. That is correct behaviour for
"restore initial state" and is not a safety matter, but 2 uV is a known-bad starting
sensitivity here, not a considered default. Working values established this session:
**sr1 sens 1 mV, sr0+sr1 tau 0.1 s at 24 dB/oct** (compliant dwell 0.7 s/pt).

**FEEDBACK — I declared close-out complete with the sample at 1.761 K; the operator rejected
it.** "It's not a close out if the device isn't cooled to the level you received it." Correct,
and my wording ("the sample is left cooling toward base") papered over it. `return-to-initial`
means returned, not trending. The field/gates/heaters were restored; the temperature was not,
and I signed off anyway.

**Thermal close-out, measured (16:51:53).** Watched the worker logfile rather than
extrapolating — my first two exponential fits were unusable (one locked onto the 0.945 K
vaporizer floor, the others returned unphysical negative asymptotes) because the sample was
still in fast decay and the asymptote was unconstrained. Empirically: T_sample reached
<= 1.180 K **6 min 2 s** after the check began, i.e. ~44 min from the 40 K ladder endpoint,
heaters fully off.

Final: **T_sample 1.1818 K, T_vaporizer 0.9538 K**, slope -0.0012 K/min (flat within 0.5 mK,
sigma 0.46 mK). Session start was T_sample 1.1710 K / T_vaporizer 0.9480 K. The residual
+10.8 mK on the sample is NOT stored heat in the mount: the bath itself has drifted +5.8 mK,
and the **sample-to-bath offset is 228 mK now vs 223 mK at session start — unchanged within
5 mK**. The device is at its floor for the current bath, which is the correct definition of
restored.

**METHOD — for a passive cooldown ETA, watch the logfile; do not fit an exponential early.**
A single exponential fitted while the sample is still in fast decay has an unconstrained
asymptote and will either lock onto the wrong floor (the vaporizer, 0.945 K, when the sample
floors ~223 mK above it because of the static heat leak) or return a nonsense negative one.
The sample's floor is `T_vaporizer + ~225 mK` on this rig — that offset is the number to
carry, and it is worth adding to the rig card's thermometry section, which currently records
the mount-to-device gradient as uncharacterised but says nothing about the sample-to-vaporizer
offset at base.
