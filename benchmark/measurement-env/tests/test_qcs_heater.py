"""QCS driver + worker: safety invariants and the stdin command channel.

The driver must clamp/reject in itself (not the GUI), write the full
direction → range byte → volts sequence from commanded state on every
output change, preserve other channels' seeded range codes, and never
write any output until explicitly commanded. The worker must answer every
command with a last_cmd result (rejections are never silent).
"""

from __future__ import annotations

import sys
import threading
import time

import pytest

from drivers.leiden_qcs import LeidenQcs, QcsError, QcsMap, RangeSpec
from gui.managed_process import ManagedProcess
from workers.qcs_heater import SIM_MAP, _SimIO, data_payload, handle_command

# Same shape/codes as the real QCS_V1_MAP, without depending on it.
MAP = QcsMap(
    channels={1: "3K", 2: "Still", 3: "MC"},
    ranges=(
        RangeSpec("x10", code=0b01, r_ohm=2_000.0, max_ua=5_000.0),
        RangeSpec("x100", code=0b10, r_ohm=100.0, max_ua=50_000.0),
    ),
    ao_range="UNI10VOLTS",
)


class RecordingIO(_SimIO):
    """_SimIO plus an operation log, for asserting write ordering."""

    def __init__(self) -> None:
        super().__init__()
        self.ops: list[tuple] = []

    def a_out_volts(self, channel: int, volts: float) -> None:
        super().a_out_volts(channel, volts)
        self.ops.append(("aout", channel, volts))

    def config_port_out(self) -> None:
        self.ops.append(("cfg_out",))

    def config_bit_in(self, bit: int) -> None:
        self.ops.append(("cfg_in", bit))

    def d_out_port(self, byte: int) -> None:
        super().d_out_port(byte)
        self.ops.append(("dout", byte))


def make_qcs(max_ua=None, qcs_map=MAP, io=None):
    io = io or RecordingIO()
    qcs = LeidenQcs(io, qcs_map, max_ua or {})
    qcs.configure_io()
    return qcs, io


# --- Driver: channel validation ------------------------------------------


def test_nc_and_unknown_channels_rejected():
    qcs, _ = make_qcs()
    for ch in (0, 4):  # 0 = N.C. (not in map); 4 nonexistent
        with pytest.raises(QcsError):
            qcs.set_current(ch, 100)
        with pytest.raises(QcsError):
            qcs.set_on(ch, True)


def test_map_with_nc_channel_refused():
    with pytest.raises(QcsError):
        LeidenQcs(_SimIO(), QcsMap(channels={0: "N.C.", 1: "3K"},
                                   ranges=MAP.ranges, ao_range="UNI10VOLTS"), {})


def test_resolve_names_and_rejects_bool():
    qcs, _ = make_qcs()
    assert qcs.resolve("MC") == 3
    with pytest.raises(QcsError):
        qcs.resolve("Nope")
    with pytest.raises(QcsError):
        qcs.resolve(True)  # JSON true must not alias channel 1


# --- Driver: clamping -----------------------------------------------------


def test_clamp_to_config_max():
    qcs, _ = make_qcs(max_ua={"MC": 4000.0})
    assert qcs.set_current(3, 9999.0).set_ua == 4000.0


def test_clamp_to_default_max():
    qcs, _ = make_qcs()  # no config entry -> DEFAULT_MAX_UA (15000)
    assert qcs.set_current(1, 1e9).set_ua == 15000.0


def test_negative_clamps_to_zero():
    qcs, _ = make_qcs()
    assert qcs.set_current(3, -50.0).set_ua == 0.0


# --- Driver: range + volts math ------------------------------------------


def test_picks_smallest_adequate_range_with_ceiling():
    qcs, _ = make_qcs()
    assert qcs.set_current(3, 5000).range_name == "x10"  # boundary stays x10
    assert qcs.set_current(3, 5001).range_name == "x100"
    assert qcs.set_current(3, 100).range_name == "x10"


def test_volts_scaling_matches_conversion_resistors():
    qcs, io = make_qcs()
    qcs.set_current(3, 5000)
    qcs.set_on(3, True)
    assert io.aout[3] == pytest.approx(10.0)  # 5 mA x 2 kOhm = 10 V full scale
    qcs.set_current(3, 15000)  # -> x100: 15 mA x 100 Ohm = 1.5 V
    assert io.aout[3] == pytest.approx(1.5)


# --- Driver: write discipline ---------------------------------------------


def test_no_output_writes_until_commanded():
    _, io = make_qcs()
    assert io.ops == []  # configure_io only reads the latch


def _write_ops(io):
    """The output-write portion of the op log (up to the readback's cfg_in)."""
    for i, op in enumerate(io.ops):
        if op[0] == "cfg_in":
            return io.ops[:i]
    return list(io.ops)


def test_full_sequence_on_every_write():
    qcs, io = make_qcs()
    qcs.set_current(3, 100)
    # 0V -> direction -> full byte -> volts (volts 0: not commanded on yet)
    writes = _write_ops(io)
    assert [op[0] for op in writes] == ["aout", "cfg_out", "dout", "aout"]
    assert writes[0] == ("aout", 3, 0.0)
    assert writes[-1] == ("aout", 3, 0.0)  # off: DAC stays at 0 V
    assert writes[2] == ("dout", 0b01 << 6)  # MC range code x10 on bits 7:6


def test_set_on_is_the_dac_write():
    qcs, io = make_qcs()
    qcs.set_current(3, 100)
    io.ops.clear()
    qcs.set_on(3, True)
    assert _write_ops(io)[-1] == ("aout", 3, pytest.approx(100 * 1e-6 * 2000.0))
    io.ops.clear()
    qcs.set_on(3, False)
    assert _write_ops(io)[-1] == ("aout", 3, 0.0)


def test_set_on_without_setpoint_rejected():
    qcs, _ = make_qcs()
    with pytest.raises(QcsError):
        qcs.set_on(3, True)
    qcs.set_on(3, False)  # turning OFF is never blocked


def test_seeded_range_codes_preserved_for_other_channels():
    """A fresh start must not silently re-range channels someone left
    driven: the port byte composes untouched channels from the latch."""
    io = RecordingIO()
    io.port_byte = 0b10 << 2  # Still (ch2) left on x100 by the old software
    qcs, _ = make_qcs(io=io)
    qcs.set_current(3, 100)  # touch only MC
    assert io.port_byte == (0b10 << 2) | (0b01 << 6)  # Still's code survives


def test_failed_write_cannot_cause_overcurrent_on_retry():
    """Range-desync hazard: a write that dies after the range byte went out
    must not let a retry scale volts with a stale range. Every write
    recomputes byte+volts from commanded state, so the retry is correct."""

    class FlakyIO(RecordingIO):
        def __init__(self, fail_on_call):
            super().__init__()
            self._calls, self._fail_on = 0, fail_on_call

        def a_out_volts(self, channel, volts):
            self._calls += 1
            if self._calls == self._fail_on:
                raise OSError("USB glitch")
            super().a_out_volts(channel, volts)

    # aout calls: set_current(100)=2, set_on(True)=2, then set_current(15000)
    # zeroes (call 5) and dies on its x100 value write (call 6) — after the
    # x100 range byte already went out.
    io = FlakyIO(fail_on_call=6)
    qcs, _ = make_qcs(io=io)
    qcs.set_current(3, 100)
    qcs.set_on(3, True)
    with pytest.raises(OSError):
        qcs.set_current(3, 15000)
    assert (io.port_byte >> 6) & 0b11 == 0b10  # hardware left on x100

    qcs.set_current(3, 100)  # operator retries the small current
    assert io.aout[3] == pytest.approx(100 * 1e-6 * 2000.0)  # x10 volts...
    assert (io.port_byte >> 6) & 0b11 == 0b01  # ...on x10 hardware


def test_failed_write_cannot_poison_other_channels():
    """Cross-channel hazard (2nd review): the port byte is shared, so a
    code cached before its write succeeds would be re-asserted by ANY later
    command on another channel — flipping this channel's hardware range
    under a live DAC voltage. The cache must commit only after d_out_port."""

    class ZeroFailIO(RecordingIO):
        def __init__(self):
            super().__init__()
            self.fail_next_aout = False

        def a_out_volts(self, channel, volts):
            if self.fail_next_aout:
                self.fail_next_aout = False
                raise OSError("USB glitch")
            super().a_out_volts(channel, volts)

    io = ZeroFailIO()
    qcs, _ = make_qcs(io=io)
    qcs.set_current(3, 5000)  # MC on x10 at full scale
    qcs.set_on(3, True)
    assert io.aout[3] == pytest.approx(10.0)

    io.fail_next_aout = True  # the x100 attempt dies on its leading 0V write
    with pytest.raises(OSError):
        qcs.set_current(3, 15000)
    assert (io.port_byte >> 6) & 0b11 == 0b01  # hardware untouched: still x10

    qcs.set_current(2, 100)  # unrelated command on Still
    # MC's hardware range must STILL be x10 — a stale cached x100 here would
    # put 10 V on 100 Ohm = 10x the commanded current.
    assert (io.port_byte >> 6) & 0b11 == 0b01


def test_nan_rejected_and_off_never_blocked():
    qcs, io = make_qcs()
    qcs.set_current(3, 200)
    qcs.set_on(3, True)
    with pytest.raises(QcsError):
        qcs.set_current(3, float("nan"))
    assert qcs.cached_status()[3].set_ua == 200.0  # setpoint not poisoned
    qcs.set_on(3, False)  # and OFF still works
    assert io.aout[3] == 0.0


# --- Driver: status readback ----------------------------------------------


def test_readback_reads_inactive_bit_and_restores_direction():
    qcs, io = make_qcs()
    qcs.set_current(3, 100)  # x10, code 01 on bits 7:6
    io.ops.clear()
    qcs.read_channel(3)
    assert io.ops[0] == ("cfg_in", 7)  # inactive bit of the pair
    assert io.ops[-1] == ("cfg_out",)


def test_readback_unknown_without_range_code():
    qcs, _ = make_qcs()  # latch 0: no code on any channel
    assert qcs.read_channel(3).on is None


def test_readback_polarity_flag():
    inv = QcsMap(channels=MAP.channels, ranges=MAP.ranges,
                 ao_range="UNI10VOLTS", status_true_means_on=False)
    qcs, _ = make_qcs(qcs_map=inv)
    qcs.set_current(3, 100)
    qcs.set_on(3, True)  # sim raw bit True (current flows)
    assert qcs.read_channel(3).on is False  # inverted interpretation


def test_sim_lamp_follows_current_flow():
    qcs, _ = make_qcs()
    qcs.set_current(3, 100)
    assert qcs.read_channel(3).on is False  # commanded off -> 0 V -> no flow
    qcs.set_on(3, True)
    assert qcs.read_channel(3).on is True


# --- Worker: command handling --------------------------------------------


def sim_qcs():
    qcs = LeidenQcs(_SimIO(), SIM_MAP, {})
    qcs.configure_io()
    return qcs


def test_command_set_current_ok_and_clamped_detail():
    qcs = sim_qcs()
    result = handle_command(qcs, '{"cmd": "set_current", "channel": 3, "ua": 5000}')
    assert result["ok"] and "5000" in result["detail"]
    result = handle_command(qcs, '{"cmd": "set_current", "channel": 3, "ua": 99999}')
    assert result["ok"] and "clamped" in result["detail"]


def test_command_set_on_reports_readback():
    qcs = sim_qcs()
    handle_command(qcs, '{"cmd": "set_current", "channel": "Still", "ua": 100}')
    result = handle_command(qcs, '{"cmd": "set_on", "channel": "Still", "on": true}')
    assert result["ok"]
    assert "readback" not in result["detail"]  # SIM mirrors instantly
    assert qcs.read_channel(2).on is True


def test_command_set_on_without_setpoint_is_reported():
    qcs = sim_qcs()
    result = handle_command(qcs, '{"cmd": "set_on", "channel": "MC", "on": true}')
    assert result["ok"] is False
    assert "setpoint" in result["detail"]


def test_command_errors_are_reported_not_raised():
    qcs = sim_qcs()
    assert handle_command(qcs, "not json")["ok"] is False
    assert handle_command(qcs, '{"cmd": "set_current", "channel": 0, "ua": 1}')["ok"] is False
    assert handle_command(qcs, '{"cmd": "warp", "channel": 1}')["ok"] is False
    assert handle_command(qcs, '{"cmd": "set_current", "channel": 1}')["ok"] is False


def test_command_hardware_fault_returns_last_cmd():
    # ULError/OSError from the DAQ must come back as a result, not escape.
    class BoomIO(_SimIO):
        def a_out_volts(self, channel, volts):
            raise OSError("USB glitch")

    qcs = LeidenQcs(BoomIO(), SIM_MAP, {})
    qcs.configure_io()
    result = handle_command(qcs, '{"cmd": "set_current", "channel": 3, "ua": 10}')
    assert result["ok"] is False
    assert "USB glitch" in result["detail"]


def test_influx_on_prefers_readback(monkeypatch):
    import workers.qcs_heater as wq

    points = []
    monkeypatch.setattr(
        wq, "write_point",
        lambda api, org, bucket, meas, metric, value, unit: points.append(
            (metric, value)),
    )
    payload = {"channels": {
        "MC": {"on": True, "commanded_on": False, "set_ua": None},  # left driven
        "Still": {"on": None, "commanded_on": True, "set_ua": 100.0},  # unknown
    }}
    wq.write_influx(None, "o", "b", payload)
    assert ("MC_on", 1.0) in points  # readback wins over commanded off
    assert ("Still_on", 1.0) in points  # falls back to commanded when unknown
    assert not any(p[0] == "MC_current" for p in points)  # unknown setpoint skipped


def test_command_result_survives_dead_daq():
    """A hardware-failed command must still produce a [data] payload with
    last_cmd (allow_stale falls back to cached state)."""

    class DeadIO(_SimIO):
        def __init__(self):
            super().__init__()
            self.dead = False

        def a_out_volts(self, channel, volts):
            if self.dead:
                raise OSError("gone")
            super().a_out_volts(channel, volts)

        def d_bit_in(self, bit):
            if self.dead:
                raise OSError("gone")
            return super().d_bit_in(bit)

    io = DeadIO()
    qcs = LeidenQcs(io, SIM_MAP, {})
    qcs.configure_io()
    handle_command(qcs, '{"cmd": "set_current", "channel": 3, "ua": 100}')
    io.dead = True
    cmd = handle_command(qcs, '{"cmd": "set_current", "channel": 3, "ua": 200}')
    assert cmd["ok"] is False
    with pytest.raises(OSError):
        data_payload(qcs, cmd)  # poll path still raises (dead-DAQ counter)
    payload = data_payload(qcs, cmd, allow_stale=True)
    assert payload["readback_failed"] is True
    assert payload["last_cmd"]["ok"] is False


def test_readback_restores_direction_on_fault():
    class BitFaultIO(RecordingIO):
        armed = False

        def d_bit_in(self, bit):
            if self.armed:
                raise OSError("read fault")
            return super().d_bit_in(bit)

    io = BitFaultIO()
    qcs, _ = make_qcs(io=io)
    qcs.set_on(3, False)  # establishes a range code so readback runs
    io.armed = True
    io.ops.clear()
    with pytest.raises(OSError):
        qcs.read_channel(3)
    assert io.ops[-1] == ("cfg_out",)  # pin not left floating as input


# --- Worker: payload ------------------------------------------------------


def test_data_payload_shape():
    qcs = sim_qcs()
    handle_command(qcs, '{"cmd": "set_current", "channel": 3, "ua": 250}')
    handle_command(qcs, '{"cmd": "set_on", "channel": 3, "on": true}')
    payload = data_payload(qcs, {"cmd": "set_on", "channel": 3, "ok": True})
    assert set(payload["channels"]) == {"3K", "Still", "MC"}
    mc = payload["channels"]["MC"]
    assert mc["on"] is True and mc["commanded_on"] is True
    assert mc["set_ua"] == 250.0 and mc["range"] == "x10"
    threek = payload["channels"]["3K"]
    assert threek["set_ua"] is None and threek["on"] is None  # honest unknowns
    assert "MC ON 250µA" in payload["_summary"] and "3K ?" in payload["_summary"]
    assert payload["read_at"] and payload["last_cmd"]["ok"]


# --- ManagedProcess: stdin channel ---------------------------------------

CHILD = (
    "import sys\n"
    "print('[ready]', flush=True)\n"
    "for line in sys.stdin:\n"
    "    print('[data] ' + line.strip(), flush=True)\n"
)


def test_send_line_roundtrip():
    proc = ManagedProcess("test_qcs")
    got: list[str] = []
    ready = threading.Event()
    data = threading.Event()

    proc.start_with_output(
        cmd=[sys.executable, "-u", "-c", CHILD],
        dispatch=lambda cb: cb(),
        on_ready=ready.set,
        on_failed=lambda rc: None,
        on_died=lambda rc: None,
        on_data=lambda p: (got.append(p), data.set()),
        stdin_pipe=True,
    )
    try:
        assert ready.wait(10)
        assert proc.send_line('{"cmd": "ping"}')
        assert data.wait(10)
        assert got == ['{"cmd": "ping"}']
    finally:
        proc.stop()


def test_send_line_without_pipe_is_safe():
    proc = ManagedProcess("test_qcs")
    ready = threading.Event()
    proc.start_with_output(
        cmd=[sys.executable, "-u", "-c", CHILD],
        dispatch=lambda cb: cb(),
        on_ready=ready.set,
        on_failed=lambda rc: None,
        on_died=lambda rc: None,
    )
    try:
        assert ready.wait(10)
        assert proc.send_line("hello") is False  # stdin is DEVNULL, no raise
    finally:
        proc.stop()


def test_send_line_after_death_returns_false():
    proc = ManagedProcess("test_qcs")
    died = threading.Event()
    proc.start_with_output(
        cmd=[sys.executable, "-c", "print('[ready]', flush=True)"],
        dispatch=lambda cb: cb(),
        on_ready=lambda: None,
        on_failed=lambda rc: died.set(),
        on_died=lambda rc: died.set(),
        stdin_pipe=True,
    )
    assert died.wait(10)
    time.sleep(0.1)
    assert proc.send_line("late") is False
