# Device card — RPL_10

*Per-device card for Aaron's RPL_10 rhombohedral-graphene device, captured for
the `2024-12-30` cooldown (`241230_measure.ipynb`). Describes device physical
properties + the measurement setup wired this run. Lives in the measurement
directory; not committed to the measurement-env repo.*

## Identity
- **Device id**: `RPL_10`
- **Material**: rhombohedral (ABC-stacked) **tetralayer (4-layer)** graphene,
  hBN-encapsulated, dual-gated with a metallic top gate, a bottom gate, and a
  silicon back gate (`k_si`). *(Layer count confirmed by Aaron, 2026-06-06 —
  "RPL" was an incorrect name from when the stack was thought to be 5 layers.)*
  This notebook hosts the SC1/SC1' superconducting domes Aaron tracks across the
  device's life.
- **Active user**: aaron
- **Status**: mature cooldown — this is a science run (Phase 2 exploration), not
  device-init. The device already has known operating points (SC1 / SC1' domes,
  a "bubble" feature) from prior cooldowns / notebooks.

## Gate stack
- **Top hBN thickness** (`dtg`): **26 nm** *(from `calculate_gate_voltages`
  default `dtg=26`, cell 31)*
- **Bottom hBN thickness** (`dbg`): **40.5 nm** *(from
  `calculate_gate_voltages` default `dbg=40.5`, cell 31)*
- **Si back gate**: YES — `k_si` (Keithley2400, `GPIB4::11`) is wired and held at
  `V_si = -20 V` for essentially all sweeps this run. Asymmetric gate stack (thin
  top hBN, thick bottom hBN) — unlike the roughly symmetric b1c2.
- **hBN dielectric constant** (`ep`): 3 *(cell 31)*
- **(n, D) convention**: `calculate_gate_voltages(n, D, dtg=26, dbg=40.5)` maps a
  target carrier density `n` (units ~10¹² cm⁻², per the linspace ranges) and
  displacement field `D` (V/nm) to `(Vtg, Vbg)`. `conversion_factor = 5.52634936`.

## Validators (this cooldown)
*Set at cell 10 via `add_validator(validators.Numbers(...))`.*

- `k_tg.volt`: **(-5.5, +2.5) V**
- `k_bg.volt`: **(-9, +5) V**
- `k_si.volt`: **(-50, +50) V**
- `heater.volt`: **(-6, +6) V**

All gate Keithleys run `compliancei = 1e-6 A`, `volt.step = 0.005 V`.

## Measurement setup (rig instruments wired this cooldown)
Physical setup state for this device/run — what knobs and readouts exist,
independent of what's been measured yet. (Largely cooldown-invariant for the
toploader rig; gate *ranges* and contact wiring drift between cooldowns.)

- **Gates**: `k_tg`, `k_bg` (top + bottom, Keithley2400 `GPIB4::9` / `GPIB4::10`),
  plus `k_si` silicon back gate (`GPIB4::11`, held −20 V). `n`/`D` computed via
  `calculate_gate_voltages` (cell 31). Ranges per Validators above.
- **DC bias**: `dc205_1` (SRS DC205, `ASRL25`) is wired and available as a
  current-bias source. Aaron's typical bias network is a **100 MΩ resistor →
  1 V = 10 nA** (i.e. I_dc[nA] = V_dc205 × 10), but this is wiring-dependent and
  not stated in this notebook — confirm against the run's cabling *(Aaron,
  2026-06-06)*. Used for the I_dc-vs-gate "perusing Idc" work earlier this run;
  parked at 0 V during the field/quantum-oscillation sweeps.
- **Lock-ins**: 8× SR830 (`sr830_1..7`, `sr830_9`) + **1× SR860** (`sr830_8`,
  the higher-bandwidth lock-in, new this cooldown, `TCPIP::192.168.0.7`).
  Channel → contact-pair wiring per `mc_4` (cell 20):
  `sr830_1: 28-25`, `sr830_2: 11-13`, `sr830_3: 13-14`,
  **`sr830_4: I_{7-20}` — the current channel (gain −1E6 per cell 8)**,
  `sr830_5: 14-15`, `sr830_6: 15-17`, `sr830_7: 29-13`, `sr830_8: 28-14`,
  `sr830_9: 29-28`; Agilents `a1: 13-14`, `a2: 15-17`. Voltage-channel gains 100.
- **Temperature / heater**: `heater` (Keithley2400, `GPIB4::12`) drives the
  sample heater for T-dependence; base T read via `temperature()` / the fridge
  logfile (recorded as the `T` column / `s.fp(temperature)` in every sweep). The
  heater is *wired and available* but has not been driven up to this point in the
  run — all sweeps so far are at base temperature.
- **Magnet**: AMI430 superconducting magnet (`mag`, `TCPIP0::192.168.0.101`) —
  **perpendicular field, set in Tesla** — is wired and is the active slow axis
  for the field gatemaps and quantum-oscillation fans in this run (swept ±1 T).
- **Rotator**: not referenced in this notebook (a `rotator_check.ipynb` exists in
  the device directory but is out of scope for this run). Treat field as purely
  perpendicular here.

## Known operating points (this device, from this run and priors)
- **SC1 / SC1'**: two superconducting domes Aaron tracks on RPL_10 (named
  features; characterized in detail later in this and subsequent notebooks).
- **"bubble"**: a feature studied for hysteresis / multiferroism in the prior
  (241207) notebook; a Hall-based multiferroism check around it opens this run.
- The quantum-oscillation work here sits near **D = 0.31 V/nm, n ≈ −2.9 to −2.1**
  (×10¹² cm⁻²), at `V_si = −20 V`.

## Contact map
Active config this run is **`mc_4`** (cell 20). The current channel is
**`sr830_4`** wired across contacts **7-20** (`I_{7-20}`, gain −1E6); the
remaining SR830s/SR860 + Agilents read voltage pairs across the device (see
Measurement setup). An alternate `mc_5` (cell 20) swaps a couple of voltage
contacts (`sr830_5: 25-24`, `sr830_8: 25-15`) and is introduced later for
heater-inclusive configs.

## Notes
- `calculate_gate_voltages` is redefined inline at cell 31 (after a first
  appearance in the prior notebook); the `dtg=26, dbg=40.5` defaults are the
  authoritative RPL_10 values for this cooldown — do not propagate the stale
  `dtg=16, dbg=25.5` that appear in some unrelated RPL_19 ana notebooks.
- `add_comment` discipline is good throughout this run — every sweep carries a
  descriptive comment (config, V_si, D/n, field). Use those comments to read
  intent off each `data/<id>/metadata.json`.
- The SR860 (`sr830_8`) is new hardware this cooldown vs. the 241207 notebook.
