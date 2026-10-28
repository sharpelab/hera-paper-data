# Session notes — QC0426 / VTI — 20260619.2

Operational log per the HERA agent prompt (RECIPE FIX / TOOLING / PROTOCOL /
FEEDBACK). Points at data; does not duplicate it.

## Bring-up record (2026-06-19)

- **Mode at start:** E0 (collaborative). **Grant: operator zack said "go for autonomy"
  2026-06-19 → E1 engaged** (after gates A/B green; bring-up VERIFY reported & accepted).
- **Gate A — instruments alive:** GREEN. Setup section ran in current kernel
  (exec [2]–[15]). `magnet.status()` cell 6: Field 0.003 T, output enabled, PS heater on,
  CC mode. LS335 cell 8: `sample_temperature` 1.168 K, `vaporizer_temperature` 0.0 K.
  4× SR830 connected (s/n 45620/83412/41639/93552). k_2400 + k_2410 (Si, s/n 1293333)
  connected; k_2410 paced (volt.step 0.005 V, inter_delay 0.01 s). DC205 (s/n 20500514,
  ramp_rate 2 V/s) connected. QSwitch (serial 37, fw 2.0 — matches expected IDN) connected.
- **Gate B — SAFETIES committed:** GREEN. Cell 18 ran (exec [11]); validators match the
  device card exactly — TG [−6.0,+7.0], BG [−4.5,+4.5], Si [−50,+50], B cap 8.0 T on
  `magnet.mag.vals`. Instrument-level TG fence also on `dc205.voltage.vals`. 8 T < 14 T
  driver backstop; planned base-T fan stays out of the >10 T/>15 K consideration zone.
- **Open observations (non-blocking):**
  - Base sample T 1.168 K — just under the 1.2–1.3 K band (colder, fine).
  - `vaporizer_temperature` (LS335 input B) reads 0.0 K. Input B is control-only and the
    rig card flags a curve-assignment anomaly on input B; we run no T ladder
    (temperature-dependence blocklisted), so non-blocking. Watch if vaporizer state ever matters.
- **Kernel-bind probe (E1, cell 32):** PASS. Bound to operator's instrument-carrying kernel.
  Magnet field ~0.0026 T, output enabled, `persistent_switch_on` True, mag.vals −8..8.
  Gates all at 0 V with validators matching card. mux (ContactMux) bound.

## FEEDBACK — lock-in τ: live 0.1 s vs device card 0.3 s (2026-06-19)
Kernel-bind probe (cell 32) read `tau=0.1 s, slope=24 dB/oct, freq≈13 Hz` on all four
SR830s. **Device card §"Lock-in time constant" documents 0.3 s** (and derives "min dwell
4·τ = 1.2 s/pt" from it). Rig card is explicit that τ/slope are operator-set on the front
panel and NOT set by the kit → the live 0.1 s is truth; the card's 0.3 s is stale or an
intent mismatch. **Using live τ = 0.1 s for dwell pricing.** At 24 dB/oct the settling
floor is ~7–10·τ ≈ 0.7–1.0 s; the gatemap's fast_delay=1 s = 10·τ is well-settled, so this
does not block the gate-plane work — but it matters for fast-B SdH sweeps later; revisit
τ before the spot checks. Sensitivities (sr1/sr2=2e-5, sr3=1e-4, sr0=5e-2) match the
card's CNP/gate-map regime. Asked operator to confirm intended τ.

## TOOLING — status-dict / mux attr names (2026-06-19)
`magnet._status()` key is `persistent_switch_on` (not `persistent_switch`); `ContactMux`
settle attr is private `_settle_s` (no public `settle_s`). Two harmless probe-cell errors
(cells 30, 32) corrected on append-only record; no instrument writes occurred.

## TOOLING — stateful instrument footguns: silent state changes readback/measurement semantics (2026-06-19)
*(note written under operator override of the earlier no-notes call — it's a reusable, cross-session driver finding.)*

**The class.** Instrument settings that are (a) operator/front-panel/NVRAM-set, not set by the
kit, (b) absent or null where you'd naively look (device card, run `metadata.json`, or a plain
parameter get), and (c) silently change what a readback or measurement *means*. They mimic a
device fault. Two hit us this session; both cost debugging time on a healthy device.

**Case 1 — Keithley 2400 averaging filter → `.volt()` "gate at 1.1 V" false alarm.**
Stock qcodes `Keithley2400`: `volt.get_cmd = _get_read_output_protected` → issues **`:READ?`**
(a fresh source-measure trigger; *errors if output off*) and `_volt_parser` returns the
**measured** VOLT field — NOT `:SOUR:VOLT:LEV?`. With the instrument's averaging filter on
(`:SENS:AVER:STAT 1`, `:COUN 2`), each `.volt()` read mixes a stale buffer sample 50/50 with the
fresh one → **exact-halving** readback (1.1125 → 0.556 → 0.278 → … → 0) relaxing from the
sweep's +4.5 V endpoint. Source was at 0 the whole time (`:SOUR:VOLT:LEV?`=0, output on, no
compliance trip; run-0 data clean: CNP at Vbg≈+0.3 V, |I_bg|<135 pA). FIX: `:SENS:AVER:COUN 1`
on k_2400 (cell 47) → `:READ?` now exact 0.0, immediate. **k_2410 (Si), same driver, audited
(cell 50): its filter was OFF (`AVER:STAT`=0, with a stale `COUN`=10) → no halving, `.volt()`
already immediate; no fix applied.** The two identical-model sources sitting in *different*
NVRAM filter states (k_2400 on / k_2410 off) is the sharpest illustration of this class and the
case for normalize-don't-inherit. **NORMALIZED (cell 53):** both gate Keithleys set to
`AVER:STAT OFF, COUN 1` → identical explicit state, immediate single-sample `:READ?` (verified
volt = exact 0.0 on both, gates at 0 V, output on). Authoritative gate-state read = `:SOUR:VOLT:LEV?` or
`.volt.cache` after a set; never a fresh `.volt()` get (it's a filtered measurement that lags any
ramp). Recorded sweep `k_2400_volt` column = setpoints, so run data is unaffected.

**Case 2 — SR830 τ = 0.1 s live vs 0.3 s on the device card** (FEEDBACK note above). Same class:
front-panel-set, kit doesn't set it, run metadata stores `None`. Operator set all four to 0.3 s
(cell 39) this session.

**Proposed fixes (the operator's framing — preflight and/or template):**
1. **Preflight / kernel-bind probe → a real STATE AUDIT.** Extend the probe to read AND compare
   against card-expected, surfacing mismatches loudly: SR830 τ / filter_slope / sensitivity;
   Keithley `:SENS:AVER:STAT`/`:COUN`/`:TCON`, nplc, autozero, output state, source vs sense func;
   DC205 ramp_rate; magnet status. The probe already reads τ — add the Keithley filter + the
   `.volt`-is-a-measurement note.
2. **Measure-notebook template → normalize, don't inherit.** Setup-time cell that explicitly SETS
   known-good state instead of inheriting NVRAM/front-panel: `k_2400`/`k_2410` `:SENS:AVER:COUN 1`,
   SR830 τ to the intended value. Inline-document the `.volt` setpoint-vs-measurement gotcha
   (read `:SOUR:VOLT:LEV?` for state; `.volt()` errors with output off).
3. **Broader audit candidates (same class, not yet bitten):** Keithley autozero / sense autorange;
   DC205 output/range/ramp_rate; magnet measured-current moving-average readback lag and
   "setpoint not readable as field" (already in rig card); LS335 input-B curve anomaly /
   `vaporizer_temperature`=0.0; QSwitch standing closures 16/11 (`qsw.reset()` forbidden).

## Session closeout (2026-06-19)

**Outcome: campaign aborted; one reusable TOOLING finding + device confirmed healthy.**
The stacking-ID campaign (ABA vs ABC by FS counting) was **not pursued** — the operator aborted
during Gate C when a back-gate readback anomaly surfaced, and we ran a debug detour instead.

**What happened (arc):**
- Bring-up gates A/B verified green from disk; E1 grant given; kernel-bind probe passed.
- Gate C contact routing (provided config) selected cleanly; **1D BG liveness sweep = run 0**
  (`data/0`) — clean: CNP at Vbg ≈ +0.3 V (TG=0), Rxx peak ~2 kΩ, metallic flanks, drain ~5 nA,
  |I_bg| < 135 pA. Contacts on the provided config are **alive**; device is healthy.
- `k_2400.volt()` post-park halving (1.1125→0.556→…) triggered an abort + E0 drop to debug.
  Root cause = 2400 averaging filter (see TOOLING note), **not** a device/gate/leakage fault.
- Fixed (k_2400 AVER→off/COUN 1), audited k_2410 (was off, normalized too), SR830 τ→0.3 s.

**Data produced:** `data/0` — Gate C BG liveness sweep, complete, usable (slug `reentry-baseline`).

**Final instrument state (parked, clean):** TG / BG / Si all at 0 V (output on); both gate
Keithleys `AVER:STAT OFF, COUN 1`; magnet ~0.003 T, output enabled, PS heater on; no runs in
progress; QSwitch routed to provided config, standing closures 16/11 intact. Measure notebook
record runs through cell 53.

**Handoffs for post-session (chiron / recipe + template maintenance):**
1. The stateful-footgun TOOLING note above → fold into preflight (state audit) + measure-notebook
   template (normalize-don't-inherit; inline `.volt`-is-a-measurement caveat).
2. Reconcile device card §"Lock-in time constant" (says 0.3 s) vs live front-panel state — and
   decide whether the template should *set* τ explicitly at bring-up.
3. k_2410 carried a stale `AVER:COUN`=10 (filter off, so dormant) — example of NVRAM drift between
   identical instruments; the template normalization closes this class.
