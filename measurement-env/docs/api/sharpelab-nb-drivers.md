# `sharpelab_nb.drivers` API Reference

Instrument drivers in `src/sharpelab_nb/drivers/`, re-exported from the package:

```python
from sharpelab_nb.drivers import SRS_DC205, Yokogawa7651, ANC350
```

The `drivers` package (`src/drivers/`: `FastBi1K5`, `QSwitch`, `ContactMux`,
the VTI `SRS_DC205`, …) is documented separately in
[`drivers.md`](drivers.md).

---

## `SRS_DC205` — DC voltage source (fixed-duration ramp)

`SRS_DC205(name, address, *, ramp_num_points=100, ramp_wait_time=0.01, **kwargs)`.
Serial `VisaInstrument` (115200 baud).

| parameter | unit | R/W | notes |
|---|---|---|---|
| `voltage` | V | R/W | raw setpoint (7 dp) |
| `smart_voltage` | V | R/W | set → `ramp_voltage` |
| `voltage_range` | — | R/W | 0: ±1 V, 1: ±10 V, 2: ±100 V |
| `output` | 0/1 | R/W | output enable |

- **`ramp_voltage(volt)`** — software ramp from the current reading over
  `ramp_num_points` steps spaced `ramp_wait_time` apart (so the duration is
  roughly fixed regardless of ΔV), **plus a mandatory 10 s settle when
  `|Δvolt| > 0.1 V`**. (The VTI `drivers.SRS_DC205` of the same name uses
  rate-based (`ramp_rate` V/s) semantics and has no fixed settle — they are not
  interchangeable.)

---

## `Yokogawa7651` — programmable DC source (pre-SCPI, write-only cached)

`Yokogawa7651(name, address, *, coil_constant=None, **kwargs)`. The 7651 is
pre-SCPI (no `*IDN?`) and cannot report programmed values back over the bus, so
**all set parameters are write-only with a software cache**.

| parameter | unit | R/W | range / notes |
|---|---|---|---|
| `volt` | V | W | ±30 V |
| `current` | A | W | ±0.12 A |
| `field` | T | W | requires `coil_constant=`; range = ±0.12·|coil| |
| `mode` | — | W | `'VOLT'` (F1;) / `'CURR'` (F5;) |
| `output` | bool | W | output enable |

- After a kernel restart the cache is empty, so the ramp methods raise unless
  the cache is seeded first: **`set_voltage_cache(value)`** /
  **`set_current_cache(value)`**, or pass `start=` to the ramp call.
- **`ramp_voltage(target, step=0.01, delay=0.05, start=None)`** /
  **`ramp_current(target, step=0.001, delay=0.05, start=None)`** — software ramp
  from the cached (or `start=`) value; `step` must be `> 0`.
- When `coil_constant` is given, `field.step`/`field.inter_delay` are
  pre-configured for safe ramping (0.1 mT / 0.1 s ⇒ ~1 mT/s).
- `trigger()` sends `E;` (normally automatic after each set). `get_idn()`
  returns a static dict.

---

## `ANC350` — attocube piezo motion controller (rotator)

`ANC350(name, dll_dir, *, device_no=0, num_axes=3, **kwargs)`. Loads
`anc350v2.dll`/`libusb0.dll` from `dll_dir`; exposes `num_axes` axes as a
`ChannelTuple` at `.axes` (each an `ANC350Axis`).

### `ANC350Axis` (one stepper axis)
| parameter | unit | R/W | notes |
|---|---|---|---|
| `status` | — | R | raw status int (decode via `is_moving`/`is_at_eot`/`has_sensor_error`/`is_sensor_disconnected`) |
| `position` | counts | R | raw sensor int32 (INT32_MAX when sensor power is off — the toploader default) |
| `rotation_count` | — | R | full-rotation counter |
| `amplitude` | mV | R/W | step drive amplitude, 0–70 000 |
| `frequency` | Hz | R/W | step frequency, 1–2000 |
| `dc_level` | mV | R/W | constant DC for fine positioning (output must be enabled) |
| `output_enabled` | bool | W | HV output; reads a software tri-state cache (True/False/None) — `set_output_cache()` to seed after restart |

Methods: `step(direction, count=1, *, wait=True, timeout=60.0, poll_interval=0.05)`
(±1 = forward/backward), `step_continuous(direction)`, `stop()`,
`wait_until_idle(…)`. `step`/`step_continuous` refuse to run unless the output
cache is `True`.

---

## Lock-in servo (`lockin_servo`)

Closed-loop positioning of an `ANC350Axis` against a lock-in voltage readback.
Not re-exported from the package — import from
`sharpelab_nb.drivers.lockin_servo`.

### `bring_up_servo_axis(name, axis, readback, *, amplitude_mv=60_000, frequency_hz=100, direction_sign=None, settle_time=0.5, v_min=-50e-3, v_max=+50e-3, tolerance=25e-6, max_iterations=200, step_count=1)` → `LockinServoedAxis`
One-call bring-up: set amplitude/frequency, enable HV output, resolve
`direction_sign` (if `None`, **physically steps the rotator** via
`calibrate_direction_sign` and prints the result to cache), and construct the
servo. `amplitude_mv` is millivolts (60 000 = 60 V).

### `LockinServoedAxis(name, *, axis, readback, direction_sign, v_min, v_max, tolerance=25e-6, settle_time=0.5, max_iterations=200, step_count=1)`
| parameter | unit | R/W | notes |
|---|---|---|---|
| `voltage` | V | R | one-shot read of the underlying readback |
| `target_voltage` | V | R/W | **set runs the servo loop synchronously**; get = last target (or None) |
| `last_iterations` | — | R | iterations used by the last run |
| `last_residual` | V | R | `abs(target − final)` of the last run |

`set` of `target_voltage` raises `ServoTimeout` if `max_iterations` is exceeded.
`abort()` requests the in-progress loop to stop (does not call `axis.stop()`).
`direction_sign` and `axis` are properties.

### `thermalized_setpoint(servo, readback_lockin, *, name=None, full_amp=None, off_amp=0.004, wait_s=60.0)` → `Parameter`
Wrap a servo move + sensor-excitation cool-down into one settable-only
`Parameter` (use as a sweep's slow axis): restore excitation → servo to target
→ drop excitation to `off_amp` → wait `wait_s` for the stage to thermalize.
After each set the lock-in amplitude is left at `off_amp`, so the followed
readback is noise during the read window — the meaningful axis is the setpoint.

### `calibrate_direction_sign(axis, readback, *, settle_time, noise_samples=5, noise_threshold=None, max_test_steps=10)` → `(sign, n_steps)`
Resolve step polarity empirically: issue forward steps until `readback` moves
past the noise threshold, return `+1` if it rose else `-1` (with the step count
used). `settle_time` is required. Called automatically by `bring_up_servo_axis`
when `direction_sign=None`.
