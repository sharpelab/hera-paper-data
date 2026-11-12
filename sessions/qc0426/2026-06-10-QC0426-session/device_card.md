# Device card — QC0426 (trilayer graphene)

*Session device card for QC0426 on the **VTI** cryostat — 2026-06-10 HERA
live session. Deployed into the measurement directory alongside the working
notebooks. Cell/run references below point into the **reference campaign
directory** `~/VTI_local_data/qingrui/20260601-QC0426-3LGr/` (read-only;
this session's own data ids restart at 0 in `./data/`).*

## Identity
- **Device id**: `QC0426`
- **Material**: **trilayer graphene** (`3LGr`), **stacking order under
  investigation** — ABA (Bernal) and ABC (rhombohedral) trilayer have
  qualitatively different Landau-fan / quantum-Hall signatures and
  displacement-field dependence, and classifying the stacking from the
  fan-vs-D structure is this device's campaign goal. Form reads from the
  data; do not assert a stacking this card does not state.
- **Operator**: qingrui
- **Fridge**: **VTI (variable-temperature insert)** — *not* the dilution-fridge
  toploader. Base temperature this cooldown is **≈ 1.2–1.3 K**
  (`sample_temperature ≈ 1.246 K` at the latest reference sweep), not millikelvin.
- **Status**: same cooldown as the reference campaign (loaded 2026-06-01;
  gate ranges established then). Prior campaign measurements ended
  2026-06-09 with the magnet swept to 0 T
  `[VERIFY: magnet actually at 0 T before bring-up]`. This session is a
  fresh measurement directory on the same loaded device.

## Gate stack (three gates, unusual drive wiring)
- **Top gate** (`k_tg`): hBN dielectric. **Driven by the SRS DC205, not a
  Keithley** — in the data it appears as the column **`DC_bias`** (the DC205
  voltage), and in sweep calls as `dc205_volt`. The sweep parameter (reference
  measure cell 78):
  `dc205_volt = qcodes.Parameter('DC_bias', unit='V', set_cmd=dcbias)`, where
  `dcbias` calls `k_tg.ramp_voltage(vg)` and `k_tg` is the SRS_DC205 with
  `ramp_rate = 2`.
- **Back gate** (`k_bg`): hBN dielectric, driven by a **Keithley 2400**.
  *(Reference cell 51: the back-gate Keithley was temporarily repatched to
  push the top gate during range-finding — read `measurement_config` per run,
  not the channel label, to know which Keithley drove what.)*
- **Si global back gate** (`k_si` / `k_2410`): doped-Si gate through **SiO₂**,
  driven by a second Keithley (`k_2410`). **The Si value is per-run — read
  `measurement_config`, don't assume a campaign-wide constant.** Reference
  campaign used +95 V (gatemaps, density cut) and +50 V (fan, run 80), and
  stepped −50…+100 V in Si-dependence maps.
  `[VERIFY: Si voltage for this session's measurements — +50 V or +95 V?]`
- **(n, D) convention** — **capacitance-based** (reference analysis cell 24),
  *not* the toploader's `dtg/dbg` constant form:
  ```python
  kappa_hBN = 3 ; kappa_SiO2 = 3.9
  c_tg = eps0 * kappa_hBN / t_tg                           # t_tg = 15.6 nm
  c_bg = eps0 / (t_bg/kappa_hBN + t_bgSiO2/kappa_SiO2)     # t_bg = 12 nm, t_bgSiO2 = 0
  n = (1/e)*(c_tg*V_tg + c_bg*V_bg) + n_offset             # → ×1e12 cm^-2 after rescale
  D = 0.5*(c_tg*V_tg - c_bg*V_bg)/eps0 + D_offset          # V/nm
  ```
  Constant-D lines are laid out as `vbg = vtg/1.3 + const` (the CNP slope
  `Vtg ≈ −1.3·Vbg + 0.06` from the reference 0 T gate map), then clipped to
  validators with the `sanitize_tg_bg()` helper. The D-line offset sets D
  (`const ≈ −8·D`: −2 → D = 0.25, −8 → D = 1, +8 → D = −1, …).

## Validators — gate B contract

The SAFETIES cell in the measure notebook must commit **exactly these
numbers**; compare values, don't eyeball:

| Parameter | Range | Notes |
|---|---|---|
| `dc205_volt` / `k_tg` | **[−6.5, +7.5] V** | established by reference-campaign range-finding |
| `k_bg.volt` | **[−5.0, +4.8] V** | ditto |
| `k_2410.volt` (Si) | **[−50, +100] V** | resolved live by operator 2026-06-10: Si optimization needs negative values — at least −50 V as the safety (Qingrui) |
| **B field (session cap)** | **\|B\| ≤ 8.0 T** | protocol-enforced (driver has no soft-limit hook); reference fans used 0↔8 T |
| **B field (amended 2026-06-11)** | **\|B\| ≤ 14.0 T** | operator approval (Qingrui/Aaron): 14 T is a cap, not an endpoint; SAFETIES re-committed in the measure notebook (cell before the E3 segment) |

## Re-entry baselines — gate C designated references

**This is a fresh run: do not read the prior campaign directory.** The
designated reference material is the curated pack at `./reference/`
(README + two B = 0 density-cut baselines at D = ±0.25 V/nm on the
session wiring). Before the campaign's main measurement, reproduce a
density cut along the same D-line and compare per the pack README's four
checks (resistance scale, CNP position, shape, drain current);
disagreement is stop-and-report. A 1D `k_bg` sweep remains a useful
qualitative gate-response/leakage check but has no designated reference
trace — judge it on smoothness, leakage floor, and CNP visibility.

*(Correction over earlier drafts: the previously designated reference
runs were bad picks — runs 20–23 are the cable-swapped TG-push sweeps,
and run 79 was taken at 6 T. The pack baselines supersede them.)*

Need more reference material? Ask the operator for it by name.

`[VERIFY: contact wiring unchanged since the reference campaign's last run]`

## Measurement setup (rig instruments wired this cooldown)
- **Gates**: top via **DC205** (`DC_bias`), back via **k_bg** Keithley, Si via
  **k_2410** Keithley. `n`/`D` from (Vtg, Vbg) via the capacitance helper.
- **AC excitation / lock-ins**: SR830 family (`sr0…sr3` live). Current-bias drive:
  **0.5 V through a 100 MΩ bias resistor**, lock-in frequency **≈ 13 Hz**.
- **Current channel**: **`sr0`** = drain current, **`sr0_gain = −1E6`** (Ithaco
  preamp gain). **Current is `I = sr0_X / sr0_gain`** — the explicit gain
  division is mandatory. Per-channel sensitivities are recorded in
  `measurement_config` (`sr0_sens=1e-2`, `sr1_sens=sr2_sens=5e-4`,
  `sr3_sens=2e-4` at the reference density cut).
- **Voltage channels**: `sr1, sr2, sr3` carry four-terminal voltages; **contact
  pairs change between configs** and live in `measurement_config`, not a global
  `mc_N` block. Wiring as of the reference campaign's end (expected unchanged —
  see `[VERIFY]` above): `sr1=09-01, sr2=12-20, sr3=09-12`, `sr0` "on 42".
  In fan measurements `sr3` is read as the Hall channel (`r_xy`).
- **Magnet**: **FastBi1K5** — custom Ethernet-driven magnet controller from
  the dgglab/VTI-drivers repo, **not an AMI430**. Reference cell 4:
  `magnet = FastBi1K5('magnet', '192.168.0.10')`. Out-of-plane (perpendicular)
  field in **Tesla** (`magnet.mag`). The perpendicular null is the magnet's
  set-point; treat "0 T" as the set value, not an absolute field. Ramp and
  blocking behavior are rig-level facts — see the agent prompt's magnet
  discipline section.
- **Temperature / thermometry**: LakeShore controller; VTI base **≈ 1.2–1.3 K**.

## Known operating points / features
- **Charge-neutrality D-line**: `Vtg ≈ −1.3·Vbg + 0.06` (fit from the
  reference 0 T gate map) — the line constant-D sweeps co-follow.
- **Capacitance lever arms** (`t_tg = 15.6 nm`, `t_bg = 12 nm`,
  `t_bgSiO2 = 0`) are the device-specific inputs to `calc_nD`; for an
  accurate lever arm, cross-check against quantum-Hall filling factors
  (`ν` from `n = ν·e·B/h`).

## Notes / caveats
- **VTI base T ≈ 1.2 K**, not mK — sets which QHE features are resolvable;
  factor it into any claim about features that are *absent*.
- The contact map is per-run; older `measurement_config` entries in the
  reference data are stale wirings from the characterization phase.
- This session's `data/` ids restart at 0 — "run 79" etc. always means the
  reference campaign directory, never this session's tree.
