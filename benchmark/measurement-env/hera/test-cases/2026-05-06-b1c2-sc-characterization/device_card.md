# Device card — b1c2

*Per-device card for the b1c2 dual-device chip. Lives in the measurement
directory; not committed to the measurement-env repo.*

## Identity
- **Device id**: `b1c2`
- **Material**: Bernal bilayer graphene + WSe₂ layer (Isaac's device).
  *(Confirmed by Aaron, 2026-06-06 — corrects an earlier "twisted trilayer +
  TMD" guess. Layer order not yet specified.)*
- **Active user**: isaac
- **Status**: freshly inserted, new cooldown — device-init only
- **Dual-device chip**: yes — "top device" and "bottom device" with
  separately-gated halves. [VERIFY: gate stack identical across both? are
  we exercising one or both tonight?]

## Gate stack
- **Top hBN thickness** (`t_tg`): ~23.6 nm *(from `_measure.ipynb` cells
  127/129; earlier cells used 24.5 nm. [VERIFY which is correct] — Aaron
  could not confirm the thicknesses, 2026-06-06.)*
- **Bottom hBN thickness** (`t_bg`): 20 nm *(from `_measure.ipynb` cells
  116/117/127/129)*
- **Si back gate**: NO. `t_bgSiO2 = 0` per `_measure.ipynb` cell 2 — no SiO2
  layer. **Dual graphite gates** (top + back), not a metal back gate
  *(confirmed by Aaron, 2026-06-06)*. **`silicon-backgate-survey` does not
  apply** to this device.
- **hBN dielectric constant** (`ep` / `cst_kappa_hBN`): 3
- **Single device or dual**: dual (top + bottom)

## Validators (current cooldown — fresh)
*Ranges established 2026-05-05 by manual range-finding after grounding fix
(see "Known issues" / `hera_scratch/session_notes.md`). Asymmetric on TG —
typical hBN leakage onset asymmetry.*

- `k_tg.volt`: **(-7, +6) V**
- `k_bg.volt`: **(-4, +4.4) V**

Live-instrument tightening applied via:
```python
k_tg.volt.vals = validators.Numbers(-7, 6)
k_bg.volt.vals = validators.Numbers(-4, 4.4)
```
Cell 1 `GATES["k_*"]["limit"]` should be updated to match so a kernel
restart preserves the validators.

## Gate-coupling notes
- Both hBN layers similar thickness — gate response should be roughly
  symmetric in (top, back), unlike Aaron's RPL devices where one is much
  thinner.
- Approximate `n ∝ Vtg/dtg + Vbg/dbg`; `D ∝ Vtg/dtg − Vbg/dbg`.
- See `_measure.ipynb` cell 2 for `calc_nD` / `calc_tb` / `sanitize_tg_bg`
  helpers — Isaac's idiom uses these instead of `sharpelab_nb`'s
  `calculate_gate_voltages`.

## Measurement setup (rig instruments wired this cooldown)
Physical setup state for this device/run — what knobs and readouts exist,
independent of what's been measured yet. (Cooldown-invariant for the toploader
rig; gate *ranges* drift between cooldowns — see Validators.)

- **Gates**: `k_tg`, `k_bg` (top + back), driven through the gate DACs; ranges
  per Validators above. `n`/`D` computed from (Vtg, Vbg) via the cell-2 helpers.
- **DC bias**: `dc205_1` (SRS DC205) applied through `bias_resistor = 1e8 Ω`,
  so a ±15 V DC205 setting is a current bias of ≈ ±150 nA.
- **Lock-ins**: 4× SR830 (`sr830_1..4`); channel → contact-pair wiring and gains
  per the Contact map section below.
- **Temperature / heater**: `heater` (Keithley2400, `GPIB4::12`) drives the
  sample heater for T-dependence; base T read via `temperature()` from the
  fridge logfile (~29 mK at base).
- **Magnet**: AMI430 superconducting magnet — **perpendicular field, set in
  Tesla** — is wired and available as a measurement knob.
- **Rotator**: in-situ sample-angle rotator is present and wired (sets the
  field's in/out-of-plane projection; "Beff = 0" labels denote the
  perpendicular component nulled at the rotator's calibrated setpoint).

## Known operating points
None yet — this is a fresh insertion / new cooldown / no prior science on
this device.

## Contact map
[VERIFY: what's the active source-drain pair for tonight? RPL_19's `mc_1`
convention won't apply. Isaac's prior session used contact pairs labeled
`28-4`, `6-4`, `7-4`, `7-31`.

Last-known-good wiring from `20260415_measure.ipynb` cell 416 (final
`meas_config` of that run, comment `'bottom device'`, Landau fan with
sd = 6-4):

- `sr830_1: "6-4"` — current channel (gain `-1e6` per cell 1's
  `SR830_GAINS[1]`)
- `sr830_2: "28-30"` — long
- `sr830_3: "30-31"` — long
- `sr830_4: "5-30"` — long
- No halls defined in that config.

Note the cell 1 `SR830_GAINS` mismatch: the b1c2 template ships with
`1: 100, 4: -1E6` (sr830_4 as current, top-device convention). Adopting
the April 15 bottom-device wiring above requires flipping to
`1: -1E6, 4: 100`. Alternatively, re-cable so the current preamp lives on
sr830_4 and shift the `mc` accordingly. Confirm with Isaac which path
applies tonight.]

## Recipe applicability for device-init
- `gate-current-sanity-check`: applies.
- `top-gate-sweep-check`: applies; respect the [VERIFY] validator.
- `back-gate-sweep-check`: applies; respect the [VERIFY] validator.
- `gate-leakage-survey`: applies if simpler checks hint at trouble.
- `silicon-backgate-survey`: **does NOT apply** (no Si BG).

## Notes
- Stale `dtg=16, dbg=25.5` in Isaac's prior `_ana.ipynb` cell 2 are
  RPL_19 values that were never updated for b1c2 — don't propagate them.
- Rotator (in-situ sample angle) is present and wired — see "Measurement
  setup" above. (Out of scope for HERA's *device-init recipes*, but it is a
  real measurement knob, not unavailable.)
- No `add_comment` discipline in source notebook — recipe asks for it
  going forward; coordinate with Isaac.
