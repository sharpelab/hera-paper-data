# `drivers` API Reference

Instrument drivers in `src/drivers/`, imported package-qualified
(`from drivers.FastBi1K5 import FastBi1K5`). QCoDeS `Instrument` /
`VisaInstrument` subclasses plus two house helpers (`ContactMux`,
`bring_up_qdac_gate`). `measurement-env` is the source of truth for these.

The `sharpelab_nb.drivers` package (`SRS_DC205`, `Yokogawa7651`, `ANC350`,
lock-in servo) is documented separately in
[`sharpelab-nb-drivers.md`](sharpelab-nb-drivers.md).

---

## `FastBi1K5` — magnet supply (CAEN ELS FAST-PS 1K5)

`FastBi1K5(name, host, **kwargs)`. Raw TCP ASCII (port 10001). Out-of-plane
field in Tesla via the coil constant `T_per_A = 1/7.3`.

| parameter | unit | R/W | notes |
|---|---|---|---|
| `field` | T | R/W | **get** = measured (averaged) current readback × `T_per_A`; **set** = blocking ramp (see below) |
| `is_ramping` | — | R | controller ramp flag (REG:STATUS bit 21) |

- **`field(target)` blocks**: issues the setpoint, polls `is_ramping` until
  clear, then a `settle_s` dwell (default 3 s). The set-point is **not**
  retrievable as a field — get always returns the measurement; never infer
  field from the last set call. Last commanded target is stashed at
  `commanded_field` (property).
- Non-blocking path: **`start_field_ramp(target)`** issues and returns
  immediately; pair with **`wait_for_ramp(timeout=None, tol=None)`** (poll the
  ramp flag, then settle — flat `settle_s` if `tol is None`, else poll the
  readback to within `tol` Tesla; `timeout=None` auto-bounds from `|ΔB|/slew`,
  `math.inf` waits forever). This enables measure-while-ramping.
- **Interrupt ≠ stop**: the ramp is commanded before the wait; a kernel
  interrupt leaves the supply ramping to its last target. Recovery is calling
  `field()`/`start_field_ramp()` again — there is no abort method.
- Limit: `max_field_T = 14.0`; targets beyond it (or beyond the `field`
  validator) raise before any setpoint is sent (checked on both the blocking
  and non-blocking paths).
- Switch / output: `heater_on()` / `heater_off()` (each blocks 10 s, no
  field-matching check), `output_enabled()`, `persistent_switch_on()` (reads);
  `status()` prints a summary. `start_field_ramp` raises if the persistent
  switch is off or the output is disabled.
- Tunables: `settle_s`, `poll_interval_s` (0.02), `slew_T_per_s` (= 1/7.3/60).

---

## `SRS_DC205` — DC voltage source (rate-based ramp)

`SRS_DC205(name, address, **kwargs)`. Serial `VisaInstrument` (115200 baud).

| parameter | unit | R/W | notes |
|---|---|---|---|
| `voltage` | V | R/W | raw setpoint |
| `smart_voltage` | V | R/W | set → `ramp_voltage` |
| `voltage_range` | — | R/W | 0: ±1 V, 1: ±10 V, 2: ±100 V |
| `output` | 0/1 | R/W | output enable |

- **`ramp_voltage(final_volt)`** — software ramp from the current reading at a
  **constant rate**: `ramp_rate` V/s (attribute, default 5) over
  `ramp_num_points` (default 50) steps. Rate-based ⇒ deterministic dV/dt at any
  move size (gate-safe). (The toploader's `sharpelab_nb.drivers.SRS_DC205` is a
  different driver with fixed-duration ramp semantics — not interchangeable.)

---

## `Lakeshore_335` — temperature controller

`Lakeshore_335(name, address, **kwargs)`. Serial `VisaInstrument`.

| parameter | unit | R/W | command |
|---|---|---|---|
| `sample_temperature` | K | R | `KRDG? A` |
| `vaporizer_temperature` | K | R | `KRDG? B` |
| `sample_setpoint` / `vaporizer_setpoint` | K | R/W | loop 1 / 2 setpoint |
| `sample_range` / `vaporizer_range` | — | R/W | heater range (int) |
| `sample_power` / `vaporizer_power` | % | R/W | manual heater output |

Methods: `set_sample_closed_loop()`, `set_vaporizer_closed_loop()`,
`off(heater='both'|'sample'|'vaporizer')`, `set_both(temperature, ratio=1)`
(picks a heater range from the target T), `warmup()` (300 K / 100 K).

## `Lakeshore_218` — temperature monitor

`Lakeshore_218(name, address, **kwargs)`. Read-only:
`magnet_temperature` (`KRDG? 1`, K), `gm_temperature` (`KRDG? 5`, K).

---

## `AMI_420` — magnet controller

`AMI_420(name, address, **kwargs)`. Serial `VisaInstrument`. Function-style
(no qcodes parameters):

- `mag(v, retries=3)` — set field setpoint, ramp, block until `STATE? != RAMPING`
  (retrying on error). `set_setpoint(v)` + `ramp()` are the lower-level pair.
- `state()` → decoded state string (`RAMPING`/`HOLDING`/`TO ZERO`/…).
- `heater_on()` / `heater_off()` — persistent-switch heater.
- `get_setpoint()`, `get_field()`, `get_ramp_rate()`, `get_ramp_segs()`.

## `AMI_1700` — He level meter

`AMI_1700(name, address, **kwargs)`. Read-only `He_level` (inches, `MEAS:HE:LEV?`).

## `Terranova_906A` — vacuum gauge

`Terranova_906A(name, address, **kwargs)`. Serial (9600 baud). Read-only
`pressure` (float), `version`, `units`.

---

## `QSwitch` — relay contact switch (QDevil)

`QSwitch(name, address, **kwargs)`. `VisaInstrument` fork (v0.5.0 lineage).
A *line* (1–24) is a device contact; a *tap* (relay 1–9) selects ground (0),
a breakout BNC (1–8), or through-connect (9). Most callers go through
`ContactMux` rather than these directly.

Parameters: `state` (R/W, the full relay channel-list string),
`closed_relays` (delegate: `(line, tap)` list), `overview` (decoded
name→state map), `auto_save` (`'on'`/`'off'` — persist relay config to NVM),
`error_indicator`.

Relay control: `close_relays(state)` / `open_relays(state)` (and singular
`close_relay(line, tap)` / `open_relay`), where `state` is a list of
`(line, tap)` tuples (additive/subtractive against the current state). Named:
`ground(lines)`, `unground(lines)`, `connect(lines)`, `breakout(line, tap)`,
`arrange(breakouts=, lines=)` (register name→number maps). Housekeeping:
`reset()` (**`*rst` — opens ALL relays**), `state_force_update()`, `errors()`,
`error()`, `abort()`.

## `contact_mux.ContactMux` — named-contact switching + truthful metadata

`ContactMux(qswitch, lines, breakouts, settle_s=10.0)`. Wraps a connected
`QSwitch` with the lab wiring model and emits a `measurement_config` fragment
so each run's contact routing is recorded.

- `lines`: contact name → QSwitch line (1–24). `breakouts`: port name →
  breakout tap (1–8). Contacts not in `lines` are invisible to the mux; taps 0
  (ground) and 9 (through) are reserved. Constructor validates ranges and
  rejects duplicate line/tap numbers.
- **`select(routing, settle_s=None)`** — switch to `routing` (port →
  contact(s)). Make-before-break against ground: grounds every managed line and
  opens its taps, closes the target `(line, tap)` relays, then opens the
  grounds (routed lines go live, unused lines float), then settles. **It grounds
  every managed line mid-transition** — ramp any DC source wired through the mux
  to 0 first.
- **`park(settle_s=None)`** — ground every managed line (idle/safe), clear
  routing.
- **`mc_fragment()`** → dict — `qswitch_routing` (intent) + `qswitch_state`
  (relay list read back from hardware), plus the corpus' `"srN": "<+>-<->"`
  pair keys and `"sr0": "drain current on …"` when ports follow the
  `source`/`drain`/`srN±` naming convention.
- Properties: `settle_s`, `routing` (last selected). Operates only on managed
  lines and never calls `qsw.reset()`.

Module helper `target_state(lines, breakouts, routing)` → sorted `(line, tap)`
closures (pure; for tests/review).
