"""QCoDeS driver for the attocube ANC350 (v2 USB protocol) piezo controller.

Wraps the v2 DLL (``anc350v2.dll``) via ctypes.  Targets the modular ANC350
platform — one USB-attached chassis with up to three single-axis Stepper
Driver modules.  Each axis is exposed as an :class:`ANC350Axis`
``InstrumentChannel`` of the top-level :class:`ANC350` ``Instrument``.

Sensor readback design choice
-----------------------------
On the toploader, the internal position sensors are intentionally
*unpowered* (sensor bias dissipates heat at base temperature).  Position
readback comes from external SR830 lock-ins on a separate parameter.  Most
position-related fields here will therefore report stale or sentinel
values (``INT32_MAX``) — this is expected and not an error.

DLL discovery
-------------
The DLL ships with the DAISY install.  Pass ``dll_dir`` pointing at the
folder containing ``anc350v2.dll`` and ``libusb0.dll`` (typically
``Software_ANC350v3/ANC350_DLL/Win_64Bit`` for 64-bit Python).
"""

from __future__ import annotations

import ctypes
import os
import sys
import time
from typing import Any

from qcodes.instrument import ChannelTuple, Instrument, InstrumentChannel
from qcodes.validators import Bool, Ints


# --- DLL surface --------------------------------------------------------

_NCB_OK = 0
_NCB_ERRORS = {
    0: "Ok",
    -1: "Error",
    1: "Timeout",
    2: "NotConnected",
    3: "DriverError",
    4: "BootIgnored",
    5: "FileNotFound",
    6: "InvalidParam",
    7: "DeviceLocked",
    8: "NotSpecifiedParam",
}

# Status bits returned by PositionerGetStatus.
_STATUS_MOVING = 0b0001
_STATUS_EOT = 0b0010
_STATUS_SENSOR_ERROR = 0b0100
_STATUS_SENSOR_DISCONNECTED = 0b1000

# DLL convention for step direction.
_DIR_FORWARD = 0
_DIR_BACKWARD = 1

# Sentinel returned when sensor power is off.
INT32_MAX = 0x7FFFFFFF


class _PositionerInfo(ctypes.Structure):
    _fields_ = [("id", ctypes.c_int), ("locked", ctypes.c_bool)]


class ANC350Error(RuntimeError):
    """Non-zero return code from an anc350v2.dll call."""

    def __init__(self, fn: str, code: int) -> None:
        super().__init__(f"{fn} failed: {code} ({_NCB_ERRORS.get(code, '?')})")
        self.code = code
        self.fn = fn


def _load_dll(dll_dir: str) -> ctypes.CDLL:
    if sys.platform != "win32":
        raise RuntimeError("ANC350 driver requires Windows (anc350v2.dll).")
    if not os.path.isdir(dll_dir):
        raise FileNotFoundError(f"dll_dir not found: {dll_dir}")
    os.add_dll_directory(dll_dir)
    dll = ctypes.WinDLL("anc350v2")

    handle = ctypes.c_int32
    axis = ctypes.c_int32
    int_out = ctypes.POINTER(ctypes.c_int32)
    bool_out = ctypes.POINTER(ctypes.c_bool)

    dll.PositionerCheck.restype = ctypes.c_int32
    dll.PositionerCheck.argtypes = [ctypes.POINTER(ctypes.POINTER(_PositionerInfo))]
    dll.PositionerConnect.restype = ctypes.c_int32
    dll.PositionerConnect.argtypes = [ctypes.c_int32, int_out]
    dll.PositionerClose.restype = ctypes.c_int32
    dll.PositionerClose.argtypes = [handle]

    # (handle, axis, *int) getters
    for name in (
        "PositionerGetStatus",
        "PositionerGetPosition",
        "PositionerGetRotCount",
        "PositionerGetAmplitude",
        "PositionerGetFrequency",
        "PositionerGetDcLevel",
    ):
        f = getattr(dll, name)
        f.restype = ctypes.c_int32
        f.argtypes = [handle, axis, int_out]

    # (handle, axis, value) setters
    # NOTE: setter for DC level is PositionerDCLevel (DC uppercase),
    # while the getter is PositionerGetDcLevel (Dc mixed) — attocube
    # naming inconsistency.
    for name in (
        "PositionerAmplitude",
        "PositionerFrequency",
        "PositionerDCLevel",
        "PositionerStepCount",
    ):
        f = getattr(dll, name)
        f.restype = ctypes.c_int32
        f.argtypes = [handle, axis, ctypes.c_int32]

    # output enable: write-only on the DLL side
    dll.PositionerSetOutput.restype = ctypes.c_int32
    dll.PositionerSetOutput.argtypes = [handle, axis, ctypes.c_bool]

    # step / stop primitives
    dll.PositionerMoveSingleStep.restype = ctypes.c_int32
    dll.PositionerMoveSingleStep.argtypes = [handle, axis, ctypes.c_int32]
    dll.PositionerMoveContinuous.restype = ctypes.c_int32
    dll.PositionerMoveContinuous.argtypes = [handle, axis, ctypes.c_int32]
    dll.PositionerStopMoving.restype = ctypes.c_int32
    dll.PositionerStopMoving.argtypes = [handle, axis]

    # cap measure — see ANC350Axis.capacitance stub below
    # dll.PositionerCapMeasure.restype = ctypes.c_int32
    # dll.PositionerCapMeasure.argtypes = [handle, axis, int_out]

    return dll


def _check(rc: int, fn: str) -> None:
    if rc != _NCB_OK:
        raise ANC350Error(fn, rc)


# --- Axis channel -------------------------------------------------------


class ANC350Axis(InstrumentChannel):
    """One axis (stepper drive module) of an ANC350 chassis.

    Parameters
    ----------
    parent : ANC350
        The owning chassis instrument (provides DLL handle).
    name : str
        Channel name.
    axis_no : int
        Hardware axis index (0-based).
    """

    def __init__(self, parent: "ANC350", name: str, axis_no: int) -> None:
        super().__init__(parent, name)
        self.axis_no: int = axis_no

        # Tri-state software cache for output enable: True / False / None
        # (unknown). Initialises to None — the DLL has no GetOutput, so we
        # genuinely don't know the device state at construction.
        # ``step`` and ``step_continuous`` refuse to run unless the cache
        # is True. Use ``output_enabled(True/False)`` or
        # ``set_output_cache()`` to set it.
        self._output_cache: bool | None = None

        # --- read-only -----------------------------------------------------

        self.add_parameter(
            "status",
            label="Status bits",
            get_cmd=self._get_status,
            docstring=(
                "Raw status int from PositionerGetStatus. "
                f"bit0={_STATUS_MOVING:#06b} moving, "
                f"bit1={_STATUS_EOT:#06b} end-of-travel, "
                f"bit2={_STATUS_SENSOR_ERROR:#06b} sensor error, "
                f"bit3={_STATUS_SENSOR_DISCONNECTED:#06b} sensor disconnected. "
                "Use is_moving/is_at_eot/has_sensor_error for decoded flags."
            ),
        )
        self.add_parameter(
            "position",
            label="Position (raw)",
            unit="counts",
            get_cmd=self._get_position,
            docstring=(
                "Internal sensor position as a raw int32. Returns INT32_MAX "
                "when sensor power is off (the toploader default — see module "
                "docstring). Real units come from the actor profile loaded "
                "into the controller; we currently do not load one because "
                "lock-in readback is used instead."
            ),
        )
        self.add_parameter(
            "rotation_count",
            label="Rotation count",
            get_cmd=self._get_rot_count,
            docstring="Full-rotation counter (rotators only).",
        )

        # --- read/write ----------------------------------------------------

        self.add_parameter(
            "amplitude",
            label="Step amplitude",
            unit="mV",
            vals=Ints(0, 70_000),  # ANC350 stepper drive: 0..70 V
            get_cmd=self._get_amplitude,
            set_cmd=self._set_amplitude,
            docstring="Stepping drive amplitude in millivolts (0..70 V).",
        )
        self.add_parameter(
            "frequency",
            label="Step frequency",
            unit="Hz",
            vals=Ints(1, 2000),
            get_cmd=self._get_frequency,
            set_cmd=self._set_frequency,
            docstring="Stepping frequency in Hz (1..2000).",
        )
        self.add_parameter(
            "dc_level",
            label="DC level (fine positioning)",
            unit="mV",
            vals=Ints(0, 70_000),
            get_cmd=self._get_dc_level,
            set_cmd=self._set_dc_level,
            docstring=(
                "Constant DC voltage applied to the piezo for fine "
                "(sub-step) positioning, in millivolts (0..70 V). "
                "Only takes effect while output is enabled. Available "
                "for manual fine-positioning; not currently used by "
                "LockinServoedAxis (toploader convention is stick-slip "
                "only)."
            ),
        )

        # --- write-only, cached -------------------------------------------

        self.add_parameter(
            "output_enabled",
            label="Output enable",
            vals=Bool(),
            get_cmd=lambda: self._output_cache,
            set_cmd=self._set_output,
            docstring=(
                "Enable HV piezo output. The DLL exposes no GetOutput, so "
                "this reads a software tri-state cache: True / False / None "
                "(unknown). Sets accept True or False only. "
                "Use set_output_cache() to seed/clear after a kernel restart."
            ),
        )

        # --- not exposed in v1: capacitance -------------------------------
        # PositionerCapMeasure briefly excites the piezo to measure
        # capacitance. Side effect makes it unsafe to call while a
        # measurement is in progress on a coupled mechanical system.
        # Stub left here so it's easy to enable later.
        #
        # self.add_parameter(
        #     "capacitance",
        #     label="Piezo capacitance",
        #     unit="nF",
        #     get_cmd=self._get_capacitance,
        # )

    # --- helpers (low-level DLL calls) -------------------------------------

    @property
    def _dll(self) -> ctypes.CDLL:
        return self.parent._dll

    @property
    def _handle(self) -> int:
        return self.parent._handle

    def _read_int(self, fn_name: str) -> int:
        out = ctypes.c_int32(0)
        rc = getattr(self._dll, fn_name)(self._handle, self.axis_no, ctypes.byref(out))
        _check(rc, fn_name)
        return out.value

    def _write_int(self, fn_name: str, value: int) -> None:
        rc = getattr(self._dll, fn_name)(self._handle, self.axis_no, value)
        _check(rc, fn_name)

    # --- parameter implementations ----------------------------------------

    def _get_status(self) -> int:
        return self._read_int("PositionerGetStatus")

    def _get_position(self) -> int:
        return self._read_int("PositionerGetPosition")

    def _get_rot_count(self) -> int:
        return self._read_int("PositionerGetRotCount")

    def _get_amplitude(self) -> int:
        return self._read_int("PositionerGetAmplitude")

    def _set_amplitude(self, value: int) -> None:
        self._write_int("PositionerAmplitude", value)

    def _get_frequency(self) -> int:
        return self._read_int("PositionerGetFrequency")

    def _set_frequency(self, value: int) -> None:
        self._write_int("PositionerFrequency", value)

    def _get_dc_level(self) -> int:
        return self._read_int("PositionerGetDcLevel")

    def _set_dc_level(self, value: int) -> None:
        self._write_int("PositionerDCLevel", value)

    def _set_output(self, enabled: bool) -> None:
        rc = self._dll.PositionerSetOutput(self._handle, self.axis_no, bool(enabled))
        _check(rc, "PositionerSetOutput")
        self._output_cache = bool(enabled)

    # def _get_capacitance(self) -> int:
    #     return self._read_int("PositionerCapMeasure")

    # --- convenience: decoded status flags --------------------------------

    def is_moving(self) -> bool:
        return bool(self.status() & _STATUS_MOVING)

    def is_at_eot(self) -> bool:
        return bool(self.status() & _STATUS_EOT)

    def has_sensor_error(self) -> bool:
        return bool(self.status() & _STATUS_SENSOR_ERROR)

    def is_sensor_disconnected(self) -> bool:
        return bool(self.status() & _STATUS_SENSOR_DISCONNECTED)

    # --- motion primitives -------------------------------------------------

    @staticmethod
    def _encode_direction(direction: int) -> int:
        if direction == +1:
            return _DIR_FORWARD
        if direction == -1:
            return _DIR_BACKWARD
        raise ValueError(f"direction must be +1 or -1, got {direction!r}")

    def _require_output_on(self, action: str) -> None:
        if self._output_cache is True:
            return
        if self._output_cache is False:
            raise RuntimeError(
                f"cannot {action}: output is disabled on axis {self.axis_no}. "
                f"Call output_enabled(True) first."
            )
        raise RuntimeError(
            f"cannot {action}: output state on axis {self.axis_no} is unknown. "
            f"Call output_enabled(True) (or False), or set_output_cache(True) "
            f"if you know it's already enabled, before issuing motion."
        )

    def wait_until_idle(
        self, timeout: float = 30.0, poll_interval: float = 0.05
    ) -> None:
        """Block until status bit 0 ("moving") clears.

        Verified reliable when motion was initiated by either:

        * :meth:`step` — sets ``PositionerStepCount`` then issues one
          ``MoveSingleStep``; bit rises ~250 ms after the DLL call and
          falls when the configured step count completes.
        * :meth:`step_continuous` + :meth:`stop` — bit falls ~225 ms after
          the stop call (firmware finishes the in-progress step cycle).

        The misuse case where bit 0 can stick: calling
        ``PositionerMoveSingleStep`` directly without first setting
        ``PositionerStepCount`` — the firmware never gets a completion
        criterion and the bit stays high indefinitely.  This wrapper
        always sets the step count, so you only hit this if you bypass
        the driver.

        Parameters
        ----------
        timeout : float
            Seconds to wait before raising ``TimeoutError``.
        poll_interval : float
            Seconds between status polls.
        """
        deadline = time.monotonic() + timeout
        while self.is_moving():
            if time.monotonic() > deadline:
                raise TimeoutError(
                    f"axis {self.axis_no} status bit 0 still high after {timeout}s"
                )
            time.sleep(poll_interval)

    def step(
        self,
        direction: int,
        count: int = 1,
        *,
        wait: bool = True,
        timeout: float = 60.0,
        poll_interval: float = 0.05,
    ) -> None:
        """Take ``count`` single steps in ``direction`` (+1 forward, -1 backward).

        Sets ``PositionerStepCount`` to ``count`` and issues ONE
        ``PositionerMoveSingleStep``.  The firmware then performs
        ``count`` step cycles and drops the status moving bit cleanly when
        done.  With ``wait=True`` (default), polls :meth:`wait_until_idle`
        until the firmware reports completion — total wall time is
        ~``count / frequency`` seconds plus a ~200 ms motion-start lag.

        With ``wait=False`` the call returns ~immediately after issuing
        the move; the rotator continues stepping in the background.
        Caller is responsible for any subsequent draining or coordination.

        Requires ``output_enabled`` cache to be ``True``.

        Parameters
        ----------
        direction : int
            ``+1`` (forward) or ``-1`` (backward).
        count : int
            Number of single steps to issue.
        wait : bool
            If True, block until ``wait_until_idle`` confirms motion has
            ended.
        timeout : float
            Forwarded to ``wait_until_idle``.  Generous default since
            slow frequencies + large counts can legitimately take a long
            time (e.g., 60 steps at 1 Hz = 60 s).
        poll_interval : float
            Forwarded to ``wait_until_idle``.
        """
        if count < 1:
            raise ValueError(f"count must be >= 1, got {count}")
        self._require_output_on("step")
        d = self._encode_direction(direction)
        rc = self._dll.PositionerStepCount(self._handle, self.axis_no, count)
        _check(rc, "PositionerStepCount")
        rc = self._dll.PositionerMoveSingleStep(self._handle, self.axis_no, d)
        _check(rc, "PositionerMoveSingleStep")
        if wait:
            # The firmware lags the DLL call — give it a poll_interval head
            # start so the moving bit has a chance to rise before we drain.
            time.sleep(poll_interval)
            self.wait_until_idle(timeout=timeout, poll_interval=poll_interval)

    def step_continuous(self, direction: int) -> None:
        """Start continuous stepping in ``direction`` (+1 / -1).

        Fire-and-forget: continues until :meth:`stop` is called.  After
        ``stop()`` you may call :meth:`wait_until_idle` to confirm motion
        has actually ended.  Requires ``output_enabled`` cache to be ``True``.
        """
        self._require_output_on("step_continuous")
        d = self._encode_direction(direction)
        rc = self._dll.PositionerMoveContinuous(self._handle, self.axis_no, d)
        _check(rc, "PositionerMoveContinuous")

    def stop(self) -> None:
        """Stop any in-progress motion on this axis."""
        rc = self._dll.PositionerStopMoving(self._handle, self.axis_no)
        _check(rc, "PositionerStopMoving")

    # --- cache management --------------------------------------------------

    def set_output_cache(self, value: bool | None) -> None:
        """Seed (or clear) the output_enabled cache without touching the device.

        Useful after a kernel restart when the actual device state is known
        but not reflected in the freshly-constructed driver.
        """
        self._output_cache = None if value is None else bool(value)


# --- Top-level instrument ----------------------------------------------


class ANC350(Instrument):
    """attocube ANC350 piezo motion controller (v2 USB protocol).

    Parameters
    ----------
    name : str
        QCoDeS instrument name.
    dll_dir : str
        Directory containing ``anc350v2.dll`` and ``libusb0.dll``.
    device_no : int
        USB device index (0-based). Default 0 — the only meaningful value
        when a single chassis is attached.
    num_axes : int
        Number of axes to expose as channels. Default 3 (the chassis
        maximum); pass 2 to skip the unused third slot.
    **kwargs
        Forwarded to :class:`qcodes.instrument.Instrument`.
    """

    def __init__(
        self,
        name: str,
        dll_dir: str,
        *,
        device_no: int = 0,
        num_axes: int = 3,
        **kwargs: Any,
    ) -> None:
        super().__init__(name, **kwargs)

        self._dll: ctypes.CDLL = _load_dll(dll_dir)
        self._device_no: int = device_no
        self._handle: int = 0

        # Confirm the device is present before grabbing it.
        info_ptr = ctypes.POINTER(_PositionerInfo)()
        n = self._dll.PositionerCheck(ctypes.byref(info_ptr))
        if n <= 0:
            raise ANC350Error("PositionerCheck", n if n < 0 else -1)
        if device_no >= n:
            raise IndexError(
                f"device_no={device_no} out of range; only {n} ANC350(s) attached"
            )
        self._positioner_id: int = info_ptr[device_no].id

        h = ctypes.c_int32(0)
        rc = self._dll.PositionerConnect(device_no, ctypes.byref(h))
        _check(rc, "PositionerConnect")
        self._handle = h.value

        axes = [ANC350Axis(self, f"axis{i}", i) for i in range(num_axes)]
        self.add_submodule(
            "axes", ChannelTuple(self, "axes", ANC350Axis, axes)
        )

        self.connect_message()

    def get_idn(self) -> dict[str, str | None]:
        return {
            "vendor": "attocube",
            "model": "ANC350",
            "serial": str(self._positioner_id) if self._positioner_id != -1 else None,
            "firmware": None,
        }

    def close(self) -> None:
        if self._handle:
            try:
                self._dll.PositionerClose(self._handle)
            finally:
                self._handle = 0
        super().close()
