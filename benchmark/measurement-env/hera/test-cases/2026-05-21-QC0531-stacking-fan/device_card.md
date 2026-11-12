# Device card — QC0531 (tetralayer graphene)

*Session device card for QC0531 on the **toploader** cryostat. Deployed into the
measurement directory alongside the working notebooks. Carries physical truth:
what is wired, the hardware, the gate operating limits, and the contact
configuration. The CNP location and (n, D) calibration were established in the
device-init session and are committed below.*

## Identity
- **Device id**: `QC0531`
- **Material**: tetralayer graphene (`4LGr`), dual-gated. Layer count from
  optical contrast + Raman on the exfoliated flake; **stacking order not
  assigned** (the question this campaign answers).
- **Owner**: aaron
- **Fridge**: toploader. Base (sample) temperature ≈ 1.3–1.5 K.
- **Status**: cold, wired; device-init complete (CNP + (n, D) line on record).

## Gate stack (two graphite gates)
- **Top gate** (`k_tg`): hBN dielectric, graphite gate; driven through the gate
  DAC, appears in sweeps as `k_tg_volt`.
- **Back gate** (`k_bg`): hBN dielectric, graphite gate; `k_bg_volt`. No Si
  back gate on this device (`t_bgSiO2 = 0`).
- **Acquisition lever lengths** (used throughout data acquisition, committed
  device-init): `dtg = 19.2 nm`, `dbg = 22.6 nm`, `ep = 3`. Gate → (n, D) via
  `sharpelab_nb.gates.calculate_n_D(vtg, vbg, dtg=19.2, dbg=22.6, ep=3)`;
  target (n, D) → gate volts via `calculate_gate_voltages(...)`.

## (n, D) calibration — ESTABLISHED (device-init, committed)

Source: 0 T TG–BG gate map, ridge by high-R-plateau centroid, per
`device-init/cnp-and-dline-calibration.md`. Ratio DATA-calibrated; absolute
n/D **scale is geometry-prior (~10–15%)** until a quantum-Hall lever-arm check
(dn/dB = ν e/h) upgrades it — do not quote absolute n at ratio precision.

- **Lever arms**: `dtg = 19.2 nm`, `dbg = 22.6 nm`, `ep = 3` (above).
- **CNP / offsets**: CNP centred at (V_tg, V_bg) ≈ (0, 0) after the device-init
  offset was folded into the acquisition constants; the D = 0 line is
  `V_tg / dtg = V_bg / dbg`. `n`, `D` computed directly from `calculate_n_D`.
- **Realized D ≈ 0 n-window in the gate box**: |n| ≲ 7 × 10¹² cm⁻² both signs.
- **Metallic survey (D ≈ 0)**: sr830_2 and sr830_3 both metallic
  (~200–600 Ω) across the n-window — no insulating arms; both usable for
  fan / spot-check Rxx. sr830_1 = Rxy (~0 at B = 0).

## Gate operating limits

| Parameter | Operating limit | Notes |
|---|---|---|
| `k_tg_volt` | **[−6.0, +6.0] V** | provided; geometry ceiling behind it |
| `k_bg_volt` | **[−6.5, +6.5] V** | provided |
| **B field (session cap)** | **\|B\| ≤ 5.0 T** | committed on the `magnet.mag` validator (SAFETIES) |

## Measurement setup (rig instruments wired this cooldown)
- **Gates**: top `k_tg`, back `k_bg`, driven through the gate DACs; ranges per
  the operating limits. `n` / `D` computed from (V_tg, V_bg) via
  `calculate_n_D` with the lever arms above.
- **AC excitation / lock-ins**: SR830 family. Current-bias drive through a
  100 MΩ bias resistor, lock-in frequency ≈ 13 Hz; time constant 0.3 s,
  24 dB/oct (minimum dwell 4·τ = 1.2 s/pt).
- **Current channel**: **`sr830_4`** carries the AC current (`I_{a-b}`); Rxx
  per voltage pair is `sr830_{pair}_X / sr830_4_X`.
- **Voltage channels**: `sr830_2`, `sr830_3` are four-terminal longitudinal
  (Rxx) pairs; `sr830_1` is the Hall channel (Rxy).
- **Magnet**: superconducting solenoid — **perpendicular field, set in Tesla** —
  wired and available as a measurement knob (session cap |B| ≤ 5 T).
- **Thermometry**: sample temperature from the fridge logfile (`T_probe`,
  `T_fridge` columns), ≈ 1.3–1.5 K at base this cooldown.

## Contact map (provided configuration this run)

| role | channel | contacts |
|---|---|---|
| current (source→drain) | `sr830_4` | `I_{a-b}` |
| Rxx pair A | `sr830_2` | 12–9 |
| Rxx pair B | `sr830_3` | 9–7 |
| Rxy (Hall) | `sr830_1` | 13–12 |

Read each Rxx pair separately — a mosaic flake can present different stacking
per region.

## Recipe applicability
- `investigations/tetralayer-stacking-fs-count.md` governs (material line =
  `4LGr`). Dual-gated, D = 0 accessible — the recipe's operating point is
  reachable.
