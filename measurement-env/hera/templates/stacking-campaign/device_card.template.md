# Device card — {{ALIAS}} ({{MATERIAL_DESC}})

*Session device card for {{ALIAS}} on the **VTI** cryostat. Deployed into the
measurement directory alongside the working notebooks. This card carries
**physical truth**: what is wired, the hardware, the outer safety box,
the provided gate operating limits, and the provided contact
configuration. The CNP location and (n, D) calibration are established
in-session (see the session brief).*

## Identity
- **Device id**: `{{ALIAS}}`
- **Material**: {{MATERIAL_DESC}} (`{{MATERIAL}}`).
- **Owner**: {{OWNER}}
- **Fridge**: VTI (variable-temperature insert). Base (sample)
  temperature ≈ 1.2–1.3 K.
- **Status**: cold, wired — hardwired breakout, no contact mux; no CNP
  location on record.

## Gate stack
- **Top gate** (`k_tg`): hBN dielectric. **Driven by a Keithley 2400**
  (`k_2400_tg`) — sweeps use `k_tg.volt` (5 mV step pacing; the measure
  notebook's setup cells bind `k_tg`).
- **Back gate** (`k_bg`): graphite on hBN, driven by the second
  **Keithley 2400** (`k_2400_bg`).
<!-- IF-SI-GATE -->
- **Si global back gate** (`k_si`): doped-Si gate through **SiO₂**,
  driven by the **SRS DC205** — bound directly to the driver's ramped
  parameter **`dc205.smart_voltage`** (set ramps at `ramp_rate = 0.5`
  V/s, get reads back `VOLT?`; data column **`dc205_smart_voltage`**).
  The DC205 has **no current readback** — gate-leakage monitoring lives
  on the Keithley `curr` channels (TG/BG) only. `ramp_voltage` steps
  span/50: a full ±50 V traverse moves in ~1 V steps, paced by
  `ramp_rate`. The graphite back gate screens Si from the channel — Si
  couples only to the contacts (contact-doping gate). Operating limit
  provided (below).
<!-- END-IF-SI-GATE -->
- **Gate-stack geometry** (fabrication facts; **geometry prior only** —
  the capacitance *calibration* is the session's to establish via
  `cnp-and-dline-calibration`):
  ```python
  from sharpelab_nb.gates import stack_capacitance, calc_nD, calc_gate_voltages
  c_tg = stack_capacitance([({{T_TG_NM}}, 3)])           # {{T_TG_NM}} nm hBN
  c_bg = stack_capacitance([({{T_BG_NM}}, 3), (0, 3.9)])   # {{T_BG_NM}} nm hBN, no SiO2 term
  ```
  Treat anything derived from these (lever arms, n/D scales, CNP-line
  slope) as uncalibrated until the session's own gate map confirms it.

## Gate operating limits — gate B contract

Gate operating limits for the session:

| Parameter | Operating limit | Notes |
|---|---|---|
| `k_tg.volt` | **{{TG_LIMIT}}** | provided; geometry ceiling is the hard fence behind it |
| `k_bg.volt` | **{{BG_LIMIT}}** | provided |
<!-- IF-SI-GATE -->
| `dc205.smart_voltage` / `dc205.voltage` (Si) | **{{SI_LIMIT}}** | provided; DC205 must be on its ±100 V range (RNGE 2) |
<!-- END-IF-SI-GATE -->
| **B field (session cap)** | **\|B\| ≤ {{B_CAP_T}} T** | committed on the `magnet.field` validator (SAFETIES); driver `max_field_T = 14.0` T is the hard backstop |
| **T setpoint (session cap)** | **`set_both` target ≤ {{T_CAP_K}} K** | provided; committed as a SAFETIES setpoint typo-guard cap. `ratio = 0.95` per the rig card — deviations consent-gated |

## Measurement setup (rig instruments wired this cooldown)
- **Gates**: top via **k_2400_tg** ({{TG_ADDR}}), back via **k_2400_bg**
  ({{BG_ADDR}}), hardwired to their sources.
<!-- IF-SI-GATE -->
- **Si gate**: **DC205** (`dc205.smart_voltage`, {{SI_ADDR}}, ±100 V
  range), hardwired to its source.
<!-- END-IF-SI-GATE -->
- **AC excitation / lock-ins**: SR830 family ({{LOCKIN_ADDRS}}).
  Current-bias drive through a **{{BIAS_R}}** bias resistor, lock-in
  frequency **{{DRIVE_FREQ}}**.
- **Current channel**: **`sr0`** = drain current, **`sr0_gain = {{SR0_GAIN}}`**
  (preamp gain). Per-channel sensitivities are recorded per run in
  `measurement_config`.
- **Drive / bias channel**: **`{{BIAS_CHANNEL}}`** — the lock-in whose
  oscillator provides the current-bias drive; `I_bias` = its live amplitude
  / the bias resistor. `hera-watch` reads the drive here.
- **Contacts — hardwired, no mux this cooldown**: device pads bond to
  two Fischer cables and land on the breakout; instrument leads connect
  directly there. Contact roles are **fixed** — rerouting a pair is
  operator work at the breakout, not software.
  - **Contact map**:

    {{CONTACT_MAP}}

    {{CONTACT_LIVENESS}} Liveness on the provided configuration is
    re-confirmed at Gate C.
- **Provided contact configuration** (hardwired):

  {{PROVIDED_CONFIG}}

## Notes

{{NOTES}}
