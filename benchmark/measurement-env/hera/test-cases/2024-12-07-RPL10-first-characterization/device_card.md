# Device card — RPL_10

*Per-device card for Aaron's RPL_10 rhombohedral-graphene device, first
cooldown. Lives in the measurement directory; not committed to the
measurement-env repo. Reconstructed from `241207_measure.ipynb` init/Configs
cells (0–20) + the RPL_10 notebook index.*

## Identity
- **Device id**: `RPL_10`
- **Material**: rhombohedral-stacked (ABC) multilayer graphene — Aaron's RPL
  series. [VERIFY: layer number (RPL = rhombohedral pentalayer?) — confirm with
  Aaron.]
- **Active user**: aaron
- **Status**: **first cooldown** of this device — device-init / early
  characterization. No prior science on RPL_10.
- **Cooldown identity**: the data on disk (`data/0…`) is from **this same
  cooldown / this notebook** — *not* a prior cooldown. (The generic replay
  preamble warns about device-card drift; for this fixture there is no drift —
  card and data are the same run.)

## Gate stack
- **Top hBN thickness** (top gate, `k_tg`): **26 nm**.
- **Bottom hBN thickness** (back gate, `k_bg`): **40 nm**.
- **Silicon back gate** (`k_si`): **YES** — this device has a doped-Si global
  back gate in addition to the local top/back hBN gates. `silicon-backgate-survey`
  **applies** (the operator uses V_Si as a third knob, e.g. +10/+20/−10/−20 V).
- The two hBN layers are **asymmetric** (26 vs 40 nm) — unlike a symmetric
  dual-hBN stack, the top gate couples more strongly per volt than the back
  gate. Typical of Aaron's RPL devices (one dielectric much thinner).
- `n` and `D` are derived from (Vtg, Vbg) [+ V_Si offset] via the standard
  rhombohedral-graphene gate-to-(n, D) relations; `calculate_gate_voltages` is
  defined inline later in the notebook (not yet present at the early cuts).

## Validators (this cooldown)
Validators are widened during the gate checks, then set for the working window
in the Configs block (cell 18). As established at the Configs block:

- `k_tg.volt`: **(−5.5, +2.5) V**  (top gate, 26 nm hBN — narrower window)
- `k_bg.volt`: **(−9, +5) V**      (back gate, 40 nm hBN)
- `k_si.volt`: **(−50, +50) V**    (Si global back gate)
- `heater.volt`: **(−6, +6) V**

During the gate-validation checks the top-gate validator is briefly opened to
±13 V and the back-gate validator to ±20 V to probe the hBN breakdown / leakage
onset (cells 27 / 33); these are wider than the working validators above.

## Gate-coupling notes
- Asymmetric stack ⇒ gate response is **not** symmetric in (top, back): expect
  the top gate to move density faster per volt than the back gate.
- The Si back gate shifts the operating point globally; the operator sweeps
  several V_Si values to find where the device behaves.

## Measurement setup (rig instruments wired this cooldown)
Physical setup state for this device/run — what knobs and readouts exist,
independent of what's been measured yet. (Cooldown-invariant for the toploader
rig; gate *ranges* are per the Validators above.)

- **Gates**: `k_tg` (top, 26 nm hBN), `k_bg` (back, 40 nm hBN), `k_si` (Si
  global back gate) — Keithley 2400 SMUs (`GPIB4::9/10/11`), each with a small
  voltage step for ramping; gate leakage current read back on `*.curr`.
- **DC bias**: an **SRS DC205** voltage source (`dc205_1`, instantiated in the
  init block) is wired as a DC-bias knob, applied through a bias resistor to set
  a current bias. [VERIFY bias-resistor value for this cooldown — not stated in
  the init cells.] Available for DC-bias / critical-current work.
- **Lock-ins**: 9× SR830 (`sr830_1..9`, GPIB0/1). In the working config (`mc_1`,
  cell 19): `sr830_4` is the **current channel** (gain **−1e6**, contact pair
  `I_{7-20}`); `sr830_1` = `9-11`, `sr830_2` = `11-13`, `sr830_3` = `13-14`,
  `sr830_5` = `14-15`, `sr830_6` = `15-17`, `sr830_7` = `17-19`, `sr830_8` =
  `24-22`, `sr830_9` = `25-24` (voltage probes, gain 100). `sr830_1.amplitude`
  is the AC excitation. An autorange helper (`autorange_sr830s`) is defined.
- **DMMs**: 2× Agilent 34401A (`a1`, `a2`, GPIB5) available as extra readouts.
- **Temperature / heater**: a `heater` (Keithley2400, `GPIB4::12`) drives the
  sample heater for T-dependence; base T read via `temperature()` from the
  fridge logfile (`Probe1_MixingCh_low.txt`). Magnet thermometry via
  `mag_temperature()`.
- **Magnet**: an **AMI430** superconducting magnet (`mag`, TCPIP) is wired and
  available as a measurement knob — **perpendicular field, set in Tesla**.
- **Rotator**: a `rotator_check.ipynb` exists in this device's directory, so an
  in-situ angle rotator may be present; **not exercised in this notebook** — do
  not assume an angle knob without confirming.

## Known operating points
None yet — first cooldown, no prior science. The operator is establishing the
gate window and locating features; the science targets (candidate
superconducting regions) emerge from the maps taken in this campaign.

## Recipe applicability for device-init
- `gate-current-sanity-check`: applies (the "can we even apply current" checks).
- `top-gate-sweep-check`: applies; respect the working validator.
- `back-gate-sweep-check`: applies; respect the working validator.
- `gate-leakage-survey`: applies (the ±13 V / ±20 V breakdown probes).
- `silicon-backgate-survey`: **applies** (this device HAS a Si back gate).

## Notes
- First notebook of the device's life; `mc_N` naming starts at `mc_1` here.
- `add_comment` discipline is present from the first gate-map cell onward.
- Contact numbering (`7-20`, `9-11`, …) is this chip's wiring; the current
  channel is on `sr830_4`.
