import math
import socket
import time

from qcodes.instrument import Instrument


class FastBi1K5(Instrument):
    """
    QCoDeS instrument for CAEN ELS FAST-Bi / FAST-PS series.
    Uses raw TCP ASCII protocol (CRLF terminated).

    Field readback truth (CAEN ELS "Command Reference Manual,
    Fast-Bi-1K5 - Fast-PS+", GET Command section):

    - ``GET:I:?`` returns the output current READ, **averaged** value —
      a measurement, smoothed by a 2-stage moving-average filter
      (8 samples @ 100 kHz, then 1024 samples @ 25 kHz; ~41 ms lag,
      i.e. ~0.1 mT at the fixed 2.3 mT/s slew — negligible).
    - ``GET:I:SAMPLE:?`` returns the output current READ,
      **instantaneous** single sample (noisier; unused here).

    Both are measurements of the output current, NOT the commanded
    set-point. The ``field`` parameter's get uses the averaged readback
    scaled by ``T_per_A``; the commanded target is not retrievable from
    the supply, so the driver stashes it (``_ramp_target``) at issue.

    Ramp surfaces:

    - ``field(target)`` — blocking ramp (issue then wait + settle).
    - ``start_field_ramp(target)`` — issue and return immediately
      (non-blocking; enables measure-while-ramping).
    - ``is_ramping`` — gettable, the controller ramp flag.
    - ``wait_for_ramp(timeout, tol)`` — block on an in-progress ramp.
    """

    def __init__(self, name: str, host: str, **kwargs):
        super().__init__(name, **kwargs)

        self.host = host
        self.port = 10001
        self.timeout_s = 2

        # magnet parameters
        self.T_per_A = float(1/7.3)                         # coil constant in Tesla per Amp
        self.max_field_T = float(14.0)                      # unit in Tesla (magnet limit, ruled 2026-06-12)
        self.slew_T_per_s = float(1/7.3/60)                 # unit in Tesla per second

        # ramp timing (tunable)
        self.settle_s = 3.0                                 # flat post-ramp dwell (wait_for_ramp, tol=None)
        self.poll_interval_s = 0.02                         # sleep between ramp-flag / readback polls

        # last commanded ramp, stashed at issue (the supply does not expose
        # the commanded setpoint as a field). Used by wait_for_ramp for the
        # tol convergence target and the auto-timeout |dB|.
        self._ramp_start: float | None = None
        self._ramp_target: float | None = None

        self.field = self.add_parameter(
            "field",
            unit="T",
            label="Magnetic field",
            get_cmd=self._get_field,
            set_cmd=self._ramp_field,
            docstring=(
                "Magnetic field in Tesla. Get: measured (averaged) current "
                "readback x T_per_A. Set: blocking ramp to target (safety "
                "checks, SET:I, poll the ramping flag, settle_s dwell). For "
                "the non-blocking path use start_field_ramp + wait_for_ramp."
            ),
        )

        self.is_ramping = self.add_parameter(
            "is_ramping",
            label="Ramping",
            get_cmd=self._is_ramping,
            docstring="True while the controller ramp flag (REG:STATUS bit 21) is set.",
        )

        # open socket now
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(self.timeout_s)
        self._sock.connect((self.host, self.port))

        # print status
        print(f'Connected to: Fast-Bi-1K5 Magnet Controller')

    def close(self) -> None:
        """Close the TCP socket before deregistering the instrument."""
        # Guard: qcodes registers the instance before the socket connects,
        # so a failed connect leaves an instrument without a _sock.
        sock = getattr(self, "_sock", None)
        if sock is not None:
            sock.close()
        super().close()

    # -------------------------------
    # Low-level communication helpers
    # -------------------------------
    def _send(self, cmd: str) -> None:
        """Send one command line (adds CRLF)."""
        if not cmd.endswith("\r\n"):
            cmd += "\r\n"
        self._sock.sendall(cmd.encode("ascii"))

    def _recv_line(self) -> str:
        """Read one reply line (ends with \\n)."""
        data = b""
        while True:
            chunk = self._sock.recv(4096)
            if not chunk:
                raise RuntimeError("Device closed the socket")
            data += chunk
            if b"\n" in data:
                break
        line = data.split(b"\n", 1)[0].decode("ascii", errors="replace").rstrip("\r")
        return line

    def _write(self, cmd: str) -> None:
        """
        Write command: expect '#AK' (ok) or '#NAK:...' (error).
        """
        self._send(cmd)
        reply = self._recv_line()

        if reply == "#AK":
            return

        if reply.startswith("#NAK"):
            raise RuntimeError(f"Device NAK for {cmd!r}: {reply}")

        raise RuntimeError(f"Unexpected reply for {cmd!r}: {reply!r}")

    def _ask(self, cmd: str) -> str:
        """
        Query command: returns raw reply like '#GET:I:0.123'
        """
        self._send(cmd)
        reply = self._recv_line()
        if not reply.startswith("#"):
            raise RuntimeError(f"Unexpected reply for {cmd!r}: {reply!r}")
        return reply

    def _ask_value(self, cmd: str, prefix: str) -> str:
        """Query and strip expected prefix."""
        reply = self._ask(cmd)
        if not reply.startswith(prefix):
            raise RuntimeError(f"Expected prefix {prefix!r}, got {reply!r}")
        return reply[len(prefix):]

    # -------------------------------
    # User functions
    # -------------------------------
    def output_enabled(self) -> bool:
        """True if the supply output stage is on (OUT:?). Read-only."""
        return self._ask_value("OUT:?", "#OUT:") == "ON"

    def persistent_switch_on(self) -> bool:
        """True if the persistent-switch heater is energized (SWITCH:PERSISTENT:?). Read-only."""
        ps_state = self._ask_value("SWITCH:PERSISTENT:?", "#SWITCH:PERSISTENT:").upper()
        return "ENAB" in ps_state

    def _status(self) -> dict:
        """
        Query magnet/supply status; returns a dict of values.
        """
        output_enabled = self.output_enabled()
        persistent_on = self.persistent_switch_on()

        loop_mode = self._ask_value("LOOP:?", "#LOOP:")
        update_mode = self._ask_value("UPMODE:?", "#UPMODE:")
        field   = float(self._ask_value("GET:I:?", "#GET:I:")) * self.T_per_A
        voltage = float(self._ask_value("GET:V:?", "#GET:V:"))

        status_dict = {
            "voltage": voltage,
            "field": field,
            "output_enabled": output_enabled,
            "persistent_switch_on": persistent_on,
            "loop_mode": loop_mode,
            "update_mode": update_mode,
        }
        return status_dict

    def status(self) -> None:
        s = self._status()
        print("---------- Magnet Status ----------")
        print(f"Field:               : {s['field']:.3f} Tesla")
        print(f"Current:             : {s['field'] / self.T_per_A:.3f} A")
        print(f"Voltage:             : {s['voltage']:.3f} V")
        print(f"Output Enabled       : {s['output_enabled']}")
        print(f"Persistent Switch On : {s['persistent_switch_on']}")
        print(f"Loop Mode            : {s['loop_mode']}")
        print(f"Update Mode          : {s['update_mode']}")
        print("-----------------------------------")

    def heater_on(self) -> None:
        """
        Turn on persistent switch heater.
        (Supply command is SWITCH:PERSISTENT:ENABLE.)
        """
        self._write("SWITCH:PERSISTENT:ENABLE")
        time.sleep(10)

    def heater_off(self) -> None:
        """
        Turn off persistent switch heater.
        """
        self._write("SWITCH:PERSISTENT:DISABLE")
        time.sleep(10)

    def _is_ramping(self) -> bool:
        status_hex = self._ask_value("REG:STATUS:?", "#REG:STATUS:")
        status = int(status_hex, 16)
        return bool((status >> 21) & 1)

    def _get_field(self) -> float:
        """Measured field in Tesla: averaged current readback x T_per_A."""
        return float(self._ask_value("GET:I:?", "#GET:I:")) * self.T_per_A

    @property
    def commanded_field(self) -> float | None:
        """Last field target (Tesla) commanded via this driver, or None before
        any ramp this session. The supply does not expose its commanded
        set-point; this is the value stashed at issue. Reliable because the
        driver is the only ramp path — compare against the measured `field()`."""
        return self._ramp_target

    # -------------------------------
    # Ramp control
    # -------------------------------
    def _check_target(self, field_target: float) -> None:
        """
        Validate a ramp target before any setpoint is issued: the hard
        magnet limit plus the ``field`` parameter's validator (the session
        cap). The qcodes Parameter layer already runs the validator on
        ``field(target)``; calling it here makes the same cap apply on the
        non-blocking ``start_field_ramp`` path, which bypasses that layer.
        """
        if abs(field_target) > self.max_field_T:
            raise ValueError(f"Target field exceeds maximum field {self.max_field_T} Tesla!")
        self.field.validate(field_target)

    def start_field_ramp(self, field_target: float) -> None:
        """
        Issue a field ramp and return immediately (non-blocking).

        Validates the target, checks supply preconditions, sends the
        setpoint, and stashes (start, target) for ``wait_for_ramp``. Does
        NOT poll the ramp flag or settle. Pair with ``is_ramping`` /
        ``wait_for_ramp`` (or sample lock-ins while ``field()`` is read) to
        measure on the fly.
        """
        self._check_target(field_target)

        status = self._status()
        if status["persistent_switch_on"] == False: # switch heater status check
            raise ValueError(f"Persistent Switch On : {status['persistent_switch_on']}")

        if status["output_enabled"] == False: # magnet controller output check
            raise ValueError(f"Output Enabled       : {status['output_enabled']}")

        current_target    = field_target / self.T_per_A
        slew_A_per_s      = self.slew_T_per_s / self.T_per_A

        self._ramp_start = status["field"]
        self._ramp_target = field_target

        self._write(f"SET:I:{slew_A_per_s}:{current_target}")
        time.sleep(0.1)

    def wait_for_ramp(self, timeout: float | None = None, tol: float | None = None) -> None:
        """
        Block until the in-progress field ramp completes, then settle.

        Phase 1 polls the controller ramp flag (``is_ramping``) until it
        clears. Phase 2 settles: with ``tol=None`` a flat ``settle_s``
        dwell; with ``tol`` set, a dynamic settle that polls the field
        readback until it is within ``tol`` Tesla of the stashed target
        (``tol`` must exceed the ~0.1 mT readback noise or it never
        converges — the timeout then trips).

        ``timeout``: ``None`` auto-bounds from ``|dB|/slew``; a float is a
        hard cap in seconds; ``math.inf`` waits forever. Exceeding it
        raises ``TimeoutError``.
        """
        deadline = self._ramp_deadline(timeout)

        while self.is_ramping():
            self._check_deadline(deadline)
            time.sleep(self.poll_interval_s)

        if tol is None:
            time.sleep(self.settle_s)
            return

        target = self._ramp_target
        while abs(self._get_field() - target) > tol:
            self._check_deadline(deadline)
            time.sleep(self.poll_interval_s)

    def _ramp_field(self, field_target: float) -> None:
        """Set and ramp the magnetic field. BLOCKING until the ramp completes."""
        self.start_field_ramp(field_target)
        self.wait_for_ramp()

    def _auto_timeout(self) -> float:
        """Auto-bound for a ramp wait: ~1.5x the bare traverse plus settle and
        a guard. Falls back to a worst-case full-range traverse if nothing was
        stashed (wait called with no prior ramp this session)."""
        start = self._ramp_start
        target = self._ramp_target
        if start is None or target is None:
            dB = 2 * self.max_field_T
        else:
            dB = abs(target - start)
        return dB / self.slew_T_per_s * 1.5 + self.settle_s + 30.0

    def _ramp_deadline(self, timeout: float | None) -> float:
        if timeout is None:
            timeout = self._auto_timeout()
        if timeout == math.inf:
            return math.inf
        return time.monotonic() + timeout

    def _check_deadline(self, deadline: float) -> None:
        if deadline != math.inf and time.monotonic() > deadline:
            raise TimeoutError(
                f"Field ramp did not complete within timeout (target {self._ramp_target} T)"
            )
