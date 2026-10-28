"""Software servo wrapping an :class:`ANC350Axis` against a lock-in readback.

On the toploader, each rotator axis is driven by an ANC350 stepper module
but read out by an external SR830 lock-in (β on GPIB0::6, φ on GPIB0::7).
The lock-in's in-phase demodulated voltage (``X``) is monotonic in the
sensor's resistive position — so we can servo the rotator to a target
*lock-in voltage* by stepping the ANC350 and watching the lock-in.

Design choices (matching current toploader convention)
------------------------------------------------------
- **Stick-slip only.** DC-level fine-positioning is supported by the
  driver but not used in the lab; the servo is pure stepping.
- **Direction polarity is explicit.** The sign of "forward step on
  ANC350 axis i increases lock-in voltage" depends on cabling and
  cryostat orientation, so the operator passes it at construction.
- **Output enable is not managed.** The servo will not enable or
  disable HV piezo output. Operator owns that lifecycle so a servo
  failure can't leave the system in an unknown state.
- **Settle time is explicit.** Operator picks a value matching their
  lock-in time constant (typically ``~5×OFLT``).

Usage
-----
Construct one servo per axis, with the readback Parameter from the
corresponding lock-in (the lab uses ``qcodes.instrument_drivers.
stanford_research.SR830``).  ``v_min``/``v_max`` clamp the accepted
target range (safety bound).  ``direction_sign`` is empirically per-axis
on the toploader — β=+1, φ=-1 — or determined via
:func:`calibrate_direction_sign`::

    from qcodes.instrument_drivers.stanford_research import SR830
    sr830_beta = SR830("sr830_beta", "GPIB0::6::INSTR")

    servo_beta = LockinServoedAxis(
        "servo_beta",
        axis=anc.axes[0],
        readback=sr830_beta.X,
        direction_sign=+1,
        v_min=-50e-3, v_max=+50e-3,
    )
    anc.axes[0].frequency(100)         # bump from 1 Hz default for speed
    anc.axes[0].output_enabled(True)
    servo_beta.target_voltage(-7.5e-3) # blocks until converged
    print(servo_beta.last_iterations(), servo_beta.last_residual())

The ``target_voltage`` Parameter is sweepable — ``set`` blocks until the
servo converges or raises.  Compatible with measureme's
``Station.sweep`` (which just calls ``param(value)`` per setpoint) and
with QCoDeS ``do1d``/``do2d``.

See ``docs/rotator-servo.md`` for the full operator cookbook.
"""

from __future__ import annotations

import threading
import time
from typing import Any

from qcodes.instrument import Instrument
from qcodes.parameters import Parameter
from qcodes.validators import Ints, Numbers


class ServoTimeout(RuntimeError):
    """Raised when the servo loop exhausts ``max_iterations`` before convergence."""


class ServoAborted(RuntimeError):
    """Raised when :meth:`LockinServoedAxis.abort` interrupts a running servo."""


class CalibrationError(RuntimeError):
    """Raised when :func:`calibrate_direction_sign` cannot resolve polarity."""


def calibrate_direction_sign(
    axis: Any,
    readback: Parameter,
    *,
    settle_time: float,
    noise_samples: int = 5,
    noise_threshold: float | None = None,
    max_test_steps: int = 10,
) -> tuple[int, int]:
    """Determine ``direction_sign`` for a :class:`LockinServoedAxis` empirically.

    Issues forward (``+1``) single steps until the readback changes by more
    than the noise threshold, then returns ``+1`` if the readback *rose*
    or ``-1`` if it *fell*.

    The axis must have ``output_enabled`` already True.  The rotator will
    be slightly displaced from its starting position when this returns —
    by ``steps_taken`` forward steps' worth (typically tiny, but not
    reversible due to stick-slip hysteresis).

    Parameters
    ----------
    axis : ANC350Axis
        Axis to calibrate.  Must have output enabled.
    readback : qcodes.parameters.Parameter
        Lock-in readback parameter (typ. ``sr830.X``).
    settle_time : float
        Seconds to wait after each step before re-reading (``~5 × OFLT``).
    noise_samples : int
        Number of baseline samples to estimate readback noise.
    noise_threshold : float | None
        Minimum absolute readback change to consider real motion (volts).
        If ``None``, estimated as ``3 × (max − min)`` of the baseline
        samples, with a tiny floor to avoid zero.
    max_test_steps : int
        Cap on test steps before giving up.

    Returns
    -------
    direction_sign : int
        ``+1`` or ``-1``.
    steps_taken : int
        Number of forward steps it took to resolve polarity.

    Raises
    ------
    CalibrationError
        If no readback change above threshold is seen within
        ``max_test_steps``.
    """
    if noise_samples < 2:
        raise ValueError(f"noise_samples must be >= 2, got {noise_samples}")
    if max_test_steps < 1:
        raise ValueError(f"max_test_steps must be >= 1, got {max_test_steps}")

    baseline = [readback() for _ in range(noise_samples)]
    if noise_threshold is None:
        noise_threshold = 3 * (max(baseline) - min(baseline)) + 1e-9
    v0 = sum(baseline) / len(baseline)

    for n in range(1, max_test_steps + 1):
        axis.step(+1, count=1)
        time.sleep(settle_time)
        v1 = readback()
        delta = v1 - v0
        if abs(delta) > noise_threshold:
            return (+1 if delta > 0 else -1), n

    raise CalibrationError(
        f"no clear motion after {max_test_steps} forward step(s); "
        f"|Δ| stayed below threshold {noise_threshold:.3e} V "
        f"(last reading {v1:+.4e} V, baseline {v0:+.4e} V)"
    )


class LockinServoedAxis(Instrument):
    """Closed-loop axis: ANC350 stepper actuator + lock-in voltage readback.

    Parameters
    ----------
    name : str
        QCoDeS instrument name.
    axis : object
        An :class:`~sharpelab_nb.drivers.anc350.ANC350Axis` providing
        ``step(direction, count)``.  Must have output enabled before
        servoing — this class does not manage output state.
    readback : qcodes.parameters.Parameter
        Parameter returning the lock-in position metric in volts (typ.
        ``sr830.X``).  Sign must be monotonic vs. position.
    direction_sign : int
        ``+1`` if ``axis.step(+1)`` increases ``readback()``, ``-1`` if
        it decreases it.  Per-rig, per-axis.
    v_min, v_max : float
        Safety clamp on accepted target values (volts).
    tolerance : float
        ``|target − readback|`` threshold below which the servo stops
        (volts).
    settle_time : float
        Seconds to wait after each step before reading the lock-in.
        Choose ``~5 × OFLT`` (lock-in time constant) for accurate reads.
    max_iterations : int
        Hard cap on servo loop iterations.  Raises :class:`ServoTimeout`
        if exceeded.
    step_count : int
        Steps issued per iteration.  Larger → faster but coarser.
    **kwargs
        Forwarded to :class:`qcodes.instrument.Instrument`.
    """

    def __init__(
        self,
        name: str,
        *,
        axis: Any,
        readback: Parameter,
        direction_sign: int,
        v_min: float,
        v_max: float,
        tolerance: float = 25e-6,
        settle_time: float = 0.5,
        max_iterations: int = 200,
        step_count: int = 1,
        **kwargs: Any,
    ) -> None:
        if direction_sign not in (-1, +1):
            raise ValueError(f"direction_sign must be +1 or -1, got {direction_sign!r}")
        if v_min >= v_max:
            raise ValueError(f"v_min ({v_min}) must be < v_max ({v_max})")
        if tolerance <= 0:
            raise ValueError(f"tolerance must be > 0, got {tolerance}")
        if settle_time < 0:
            raise ValueError(f"settle_time must be >= 0, got {settle_time}")
        if step_count < 1:
            raise ValueError(f"step_count must be >= 1, got {step_count}")

        super().__init__(name, **kwargs)

        self._axis = axis
        self._readback = readback
        self._direction_sign: int = int(direction_sign)
        self._v_min: float = float(v_min)
        self._v_max: float = float(v_max)
        self._tolerance: float = float(tolerance)
        self._settle_time: float = float(settle_time)
        self._max_iterations: int = int(max_iterations)
        self._step_count: int = int(step_count)

        self._abort_flag = threading.Event()
        self._target_cache: float | None = None
        self._last_iterations: int = 0
        self._last_residual: float = float("nan")

        self.add_parameter(
            "voltage",
            label="Lock-in voltage",
            unit="V",
            get_cmd=self._readback,
            docstring="One-shot read of the underlying lock-in readback parameter.",
        )
        self.add_parameter(
            "target_voltage",
            label="Target voltage",
            unit="V",
            vals=Numbers(self._v_min, self._v_max),
            get_cmd=lambda: self._target_cache,
            set_cmd=self._servo_to,
            docstring=(
                "Target lock-in voltage. Setting this runs the servo loop "
                "synchronously; get returns the last commanded target (or "
                "None if never set)."
            ),
        )
        self.add_parameter(
            "last_iterations",
            label="Servo iterations (last run)",
            vals=Ints(0),
            get_cmd=lambda: self._last_iterations,
        )
        self.add_parameter(
            "last_residual",
            label="Residual error (last run)",
            unit="V",
            get_cmd=lambda: self._last_residual,
            docstring="abs(target − final_voltage) from the last servo run.",
        )

    # --- public API --------------------------------------------------------

    def abort(self) -> None:
        """Request the in-progress servo loop to stop.

        Sets a flag checked on each iteration.  Does NOT call
        ``axis.stop()`` — the operator can do that separately if needed.
        """
        self._abort_flag.set()

    # --- servo loop --------------------------------------------------------

    def _servo_to(self, target: float) -> None:
        self._abort_flag.clear()
        v = self._readback()
        err = target - v
        iterations = 0

        for iterations in range(1, self._max_iterations + 1):
            if abs(err) <= self._tolerance:
                iterations -= 1  # didn't actually need to step
                break

            if self._abort_flag.is_set():
                self._last_iterations = iterations - 1
                self._last_residual = abs(err)
                raise ServoAborted(
                    f"aborted after {iterations - 1} iterations, "
                    f"residual={err:+.4e} V"
                )

            err_sign = 1 if err > 0 else -1
            self._axis.step(self._direction_sign * err_sign, count=self._step_count)
            if self._settle_time:
                time.sleep(self._settle_time)
            v = self._readback()
            err = target - v
        else:
            self._last_iterations = self._max_iterations
            self._last_residual = abs(err)
            raise ServoTimeout(
                f"did not converge within {self._max_iterations} iterations; "
                f"residual={err:+.4e} V, last reading={v:+.4e} V"
            )

        self._target_cache = target
        self._last_iterations = iterations
        self._last_residual = abs(err)

    @property
    def direction_sign(self) -> int:
        """The configured ``+1``/``-1`` step polarity (read-only)."""
        return self._direction_sign

    @property
    def axis(self) -> Any:
        """The underlying ANC350 axis.

        Use it for live actuator config the servo deliberately doesn't own
        — e.g. ``servo.axis.frequency(1000)`` to speed up stepping mid-session,
        ``servo.axis.amplitude(...)``, or ``servo.axis.output_enabled(False)``.
        """
        return self._axis


def bring_up_servo_axis(
    name: str,
    axis: Any,
    readback: Parameter,
    *,
    amplitude_mv: int = 60_000,
    frequency_hz: int = 100,
    direction_sign: int | None = None,
    settle_time: float = 0.5,
    v_min: float = -50e-3,
    v_max: float = +50e-3,
    tolerance: float = 25e-6,
    max_iterations: int = 200,
    step_count: int = 1,
) -> LockinServoedAxis:
    """Pre-flight an ANC350 rotator axis and return a ready :class:`LockinServoedAxis`.

    Collapses the standard bring-up — set amplitude/frequency, enable HV
    output, resolve ``direction_sign``, construct the servo — into one call,
    so each rotator axis (β/θ on one chassis axis, φ on the next) is a
    single line at the top of a notebook.  See ``docs/rotator-servo.md``.

    Parameters
    ----------
    name : str
        QCoDeS instrument name for the servo (e.g. ``"servo_phi"``).
    axis : ANC350Axis
        The chassis axis to drive (e.g. ``anc.axes[1]`` for φ).
    readback : qcodes.parameters.Parameter
        Lock-in position readback (e.g. ``sr830_phi.X``).
    amplitude_mv : int
        Piezo step amplitude in **millivolts** (param is mV; 60_000 = 60 V,
        the toploader chassis default).  Not volts — ``60`` here is ~no motion.
    frequency_hz : int
        Step frequency.  100 Hz is ~2-3× faster than the 1 Hz safety idle.
    direction_sign : int | None
        ``+1``/``-1`` step polarity.  If ``None``, this calls
        :func:`calibrate_direction_sign`, which **physically steps the
        rotator** a few times to resolve polarity and prints the result so
        you can cache it (pass it explicitly next time to skip the steps).
    settle_time, v_min, v_max, tolerance, max_iterations, step_count
        Forwarded to :class:`LockinServoedAxis` (see its docstring).

    Returns
    -------
    LockinServoedAxis
        Output-enabled, ready to ``target_voltage(...)``.  The resolved
        polarity is available as ``servo.direction_sign`` (read it to cache
        the calibrated value and skip re-stepping next session), and the
        underlying axis as ``servo.axis``.
    """
    axis.amplitude(amplitude_mv)
    axis.frequency(frequency_hz)
    axis.output_enabled(True)

    if direction_sign is None:
        direction_sign, n_cal = calibrate_direction_sign(
            axis, readback, settle_time=settle_time
        )
        print(
            f"{name}: calibrated direction_sign = {direction_sign:+d} "
            f"({n_cal} steps used) — cache this to skip recalibration"
        )

    return LockinServoedAxis(
        name,
        axis=axis,
        readback=readback,
        direction_sign=direction_sign,
        v_min=v_min,
        v_max=v_max,
        tolerance=tolerance,
        settle_time=settle_time,
        max_iterations=max_iterations,
        step_count=step_count,
    )


def thermalized_setpoint(
    servo: LockinServoedAxis,
    readback_lockin: Any,
    *,
    name: str | None = None,
    full_amp: float | None = None,
    off_amp: float = 0.004,
    wait_s: float = 60.0,
) -> Parameter:
    """Wrap a servo move + sensor-excitation cool-down into one settable Parameter.

    Stick-slip stepping **and** the readout lock-in's excitation both
    dissipate heat into the sample — enough to suppress the SC state at base
    temperature.  This wraps the per-setpoint protocol so the existing
    sweep/dataset/plot machinery drives it unchanged: restore excitation →
    servo to target → drop excitation → wait for the stage to thermalize.

    Returns a settable-only :class:`~qcodes.parameters.Parameter`; use it as
    the slow axis of a sweep (``s.sweep(theta_thermalized, setpoints, ...)``).

    Note
    ----
    After each set the lock-in amplitude is left at ``off_amp``, so
    ``readback_lockin.X`` is noise during the read window — the meaningful
    axis is the *setpoint*, not the followed readback.  Wrap your sweep in
    ``try/finally`` restoring ``readback_lockin.amplitude(full)`` so an
    aborted sweep doesn't leave the sensor un-excited.

    Parameters
    ----------
    servo : LockinServoedAxis
        The axis to drive (e.g. ``servo_phi``).
    readback_lockin : SR830
        The lock-in whose ``amplitude`` powers this axis's position sensor.
        Each axis has its own — drop the right one, or two axes thermalize
        against each other.
    name : str | None
        Parameter name.  Defaults to ``"<servo>_thermalized"``.
    full_amp : float | None
        Excitation (V) needed for servo readback.  Defaults to the lock-in's
        current ``amplitude()`` at call time.
    off_amp : float
        Excitation (V) during the cool-down/read window.  0.004 V is the
        SR830 sine-amplitude floor (~no signal).
    wait_s : float
        Seconds to wait after dropping excitation, per setpoint (60–600 s
        on the toploader; raise if R doesn't recover between points).
    """
    full = full_amp if full_amp is not None else float(readback_lockin.amplitude())

    def _set(v: float) -> None:
        readback_lockin.amplitude(full)   # ensure full for servo readback
        servo.target_voltage(v)           # blocks until convergence
        readback_lockin.amplitude(off_amp)  # kill the steady-state heat source
        time.sleep(wait_s)                # let the stage thermalize

    return Parameter(
        name or f"{servo.name}_thermalized",
        label=f"{servo.name} target (thermalize protocol)",
        unit="V",
        set_cmd=_set,
    )
