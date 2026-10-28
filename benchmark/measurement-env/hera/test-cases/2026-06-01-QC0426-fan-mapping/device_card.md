# Device card — QC0426 (trilayer graphene)

*Per-device card for Qingrui's QC0426 trilayer-graphene device, 2026-06-01
cooldown on the **VTI** cryostat. Lives in the measurement directory; not
committed to the measurement-env repo.*

## Identity
- **Device id**: `QC0426`
- **Material**: **trilayer graphene** (`3LGr`), **stacking order unknown at the
  start of this cooldown — determining it was the whole point of the run.**
  ABA (Bernal) and ABC (rhombohedral) trilayer have qualitatively different
  Landau-fan / quantum-Hall signatures and displacement-field dependence, so the
  campaign loaded the sample into the VTI to **classify ABA vs ABC** from the
  fan-vs-D structure. Outcome (Qingrui, 2026-06-09): **the VTI did not get cold
  enough for a definitive classification**, but he **suspects ABA (Bernal)**.
  Treat the stacking as *unconfirmed, leaning ABA* — do not hard-assert it.
  (This supersedes the earlier ~70% ABC guess.)
- **Active user**: qingrui
- **Fridge**: **VTI (variable-temperature insert)** — *not* the dilution-fridge
  toploader. Base temperature this cooldown is **≈ 1.2-1.3 K**
  (`sample_temperature ≈ 1.246 K` at the latest sweep), not millikelvin.
- **Status**: single characterization cooldown; gate ranges established fresh this
  run. **D-series fans complete** — runs 80–84 = D = 0.25, 1, −1, −0.25, −0.5.
  Run 84 ended **2026-06-09 19:46 EDT** having swept B 8→0 T (magnet nominally
  at 0 T). Rig handed over for the **2026-06-10 HERA/IRIS live trial**.

## Gate stack (three gates, unusual drive wiring)
- **Top gate** (`k_tg`): hBN dielectric. **Driven by the SRS DC205, not a
  Keithley** — in the data it appears as the column **`DC_bias`** (the DC205
  voltage), and in sweep calls as `dc205_volt`. The sweep parameter is defined
  in measure cell 78:
  `dc205_volt = qcodes.Parameter('DC_bias', unit='V', set_cmd=dcbias)`, where
  `dcbias` calls `k_tg.ramp_voltage(vg)` and `k_tg` is the SRS_DC205 with
  `ramp_rate = 2`. Range this cooldown: **[−6.5, +7.5] V**.
- **Back gate** (`k_bg`): hBN dielectric, driven by a **Keithley 2400**. Range:
  **[−5, +4.8] V**. *(Cell 51: the back-gate Keithley was temporarily repatched to
  push the top gate during range-finding — read `measurement_config` per run, not
  the channel label, to know which Keithley drove what.)*
- **Si global back gate** (`k_si` / `k_2410`): doped-Si gate through **SiO₂**,
  driven by a second Keithley (`k_2410`). **The Si value is per-run — read
  `measurement_config`, don't assume a campaign-wide constant.** The 6 T gatemap
  and the D = 0.25 density cut (run 79) used **+95 V**, but the D = 0.25 fan
  (run 80, measure cell 183) ran at **+50 V** (`k_2410.volt(+50)`, comment
  "Si=50V"). Also stepped −50…+100 V in Si-dependence maps.
- **(n, D) convention** — **capacitance-based, including the SiO₂ Si-gate term**
  (analysis cell 24), *not* the toploader's `dtg/dbg` constant form:
  ```python
  kappa_hBN = 3 ; kappa_SiO2 = 3.9
  c_tg = eps0 * kappa_hBN / t_tg
  c_bg = eps0 / (t_bg/kappa_hBN + t_bgSiO2/kappa_SiO2)   # series hBN + SiO2
  n = (1/e)*(c_tg*V_tg + c_bg*V_bg) + n_offset           # → ×1e12 cm^-2 after rescale
  D = 0.5*(c_tg*V_tg - c_bg*V_bg)/eps0 + D_offset        # V/nm
  ```
  Constant-D lines are laid out as `vbg = vtg/1.3 + const` (the CNP slope
  `Vtg ≈ −1.3·Vbg + 0.06` from the 0 T map), then clipped to validators with the
  inline `sanitize_tg_bg()` helper. The D-line offset sets D
  (`const ≈ −8·D`: −2 → D = 0.25, −8 → D = 1, +8 → D = −1, …).

## Validators (this cooldown)
- `k_tg` (DC205): **[−6.5, +7.5] V**
- `k_bg` (Keithley): **[−5, +4.8] V**
- `k_si` (`k_2410`): per-run — **+95 V** (6 T gatemap, density cut run 79),
  **+50 V** (D = 0.25 fan, run 80); stepped −50…+100 V in Si maps

## Measurement setup (rig instruments wired this cooldown)
- **Gates**: top via **DC205** (`DC_bias`), back via **k_bg** Keithley, Si via
  **k_2410** Keithley. `n`/`D` from (Vtg, Vbg) via the capacitance helper.
- **AC excitation / lock-ins**: SR830 family (`sr0…sr3` live). Current-bias drive:
  **0.5 V through a 100 MΩ bias resistor**, lock-in frequency **≈ 13 Hz**.
- **Current channel**: **`sr0`** = drain current, **`sr0_gain = −1E6`** (Ithaco
  preamp gain). **Current is `I = sr0_X / sr0_gain`** — the explicit gain division
  is mandatory (the per-rig convention difference from the toploader, which reads
  `sr4`/`sr830_4`). Per-channel sensitivities are recorded
  (`sr0_sens=1e-2`, `sr1_sens=sr2_sens=5e-4`, `sr3_sens=2e-4` at the density cut).
- **Voltage channels**: `sr1, sr2, sr3` carry four-terminal voltages; **contact
  pairs change between configs** and live in `measurement_config`, not a global
  `mc_N` block:
  - characterization block: `sr1=21-28, sr2=28-12, sr3=12-20` (`sr0` "on 03")
  - D-series / density cut: `sr1=09-01, sr2=12-20, sr3=09-12` (`sr0` "on 42")
  In the Landau-fan sections `sr3` is read as the Hall channel (`r_xy`).
- **Magnet**: **FastBi1K5** — a custom Ethernet-driven magnet controller from
  the dgglab/VTI-drivers repo, **not an AMI430**. Measure cell 4:
  `from FastBi1K5 import FastBi1K5; magnet = FastBi1K5('magnet', '192.168.0.10')`
  (driver source on the rig at `C:\Users\DGG\Documents\GitHub\vti_drivers\`).
  Out-of-plane (perpendicular) field in **Tesla** (`mag`/`magnet.mag`), used to
  **±13 T** (gate-vs-B maps) and 0↔8 T (fan ranges). The perpendicular null is
  the magnet's current set-point; treat "0 T" as the set value, not an absolute
  field.
- **Temperature / thermometry**: LakeShore controller; VTI base **≈ 1.2-1.3 K**.

## Active measurement config at the cut (`data/79`, the density cut)
`sr0` = drain current on 42 (gain −1E6); `sr1=09-01`, `sr2=12-20`, `sr3=09-12`;
`Si (k_2410) = +95 V`; other contacts floated. Comment:
*"n sweep at fixed D, DC205 for TG, K2400 for BG, Si=95V, float other contacts."*

## Known operating points / features (from this cooldown)
- **Charge-neutrality D-line**: `Vtg ≈ −1.3·Vbg + 0.06` (fit from the 0 T gate
  map), the line the fans co-sweep at fixed D.
- A **Landau fan at D = 0** (files 27/31) is established to 8 T / 13 T; the
  campaign's quantitative target is how the fan / Landau-level structure evolves
  with D.

## Notes / caveats
- **Stacking unconfirmed** (ABC vs ABA) — see Identity. Don't over-index.
- **Capacitance lever arms** (`t_tg`, `t_bg`, `t_bgSiO2`) are the device-specific
  inputs to `calc_nD`; for the accurate lever arm, cross-check against the
  quantum-Hall filling factors in the fans (`ν` from `n = ν·e·B/h`).
- **VTI base T ≈ 1.2 K**, not mK — sets what QHE features are resolvable.
- The active-config contact map is per-section; earlier `measurement_config`
  entries are stale wirings from the same cooldown's characterization phase.
