import itertools
import math
import unittest
from unittest import mock

from qcodes import validators
from qcodes.parameters import Parameter

from drivers.FastBi1K5 import FastBi1K5

# Replies the fake supply serves per query (status-healthy defaults).
HEALTHY = {
    "OUT:?": "#OUT:ON",
    "SWITCH:PERSISTENT:?": "#SWITCH:PERSISTENT:ENABLED",
    "LOOP:?": "#LOOP:I",
    "UPMODE:?": "#UPMODE:NORMAL",
    "GET:I:?": "#GET:I:7.3",
    "GET:V:?": "#GET:V:1.5",
    "REG:STATUS:?": "#REG:STATUS:00000000",
}

RAMPING = "#REG:STATUS:00200000"  # bit 21 set
IDLE = "#REG:STATUS:00000000"

_names = itertools.count()


class FakeSocket:
    """Scripted TCP supply: records sent command lines, replies per command."""

    def __init__(self, replies: dict) -> None:
        self.replies = dict(replies)
        self.sent: list[str] = []
        self._pending: list[bytes] = []
        self.closed = False

    def sendall(self, data: bytes) -> None:
        cmd = data.decode("ascii").rstrip("\r\n")
        self.sent.append(cmd)
        if cmd.startswith("SET:I:") or cmd.startswith("SWITCH:PERSISTENT:EN") or cmd.startswith("SWITCH:PERSISTENT:DIS"):
            reply = self.replies.get(cmd, "#AK")
        else:
            reply = self.replies[cmd]
        if callable(reply):
            reply = reply()
        self._pending.append((reply + "\r\n").encode("ascii"))

    def recv(self, _n: int) -> bytes:
        return self._pending.pop(0)

    def settimeout(self, _t) -> None:
        pass

    def connect(self, _addr) -> None:
        pass

    def close(self) -> None:
        self.closed = True


def make_magnet(replies=HEALTHY) -> tuple[FastBi1K5, FakeSocket]:
    fake = FakeSocket(replies)
    with mock.patch("drivers.FastBi1K5.socket") as socket_mod:
        socket_mod.socket.return_value = fake
        magnet = FastBi1K5(f"magnet_test_{next(_names)}", "127.0.0.1")
    return magnet, fake


class FastBi1K5TestCase(unittest.TestCase):
    def setUp(self) -> None:
        sleep_patch = mock.patch("drivers.FastBi1K5.time.sleep")
        self.sleeps = sleep_patch.start()
        self.addCleanup(sleep_patch.stop)

    def make(self, replies=HEALTHY) -> tuple[FastBi1K5, FakeSocket]:
        magnet, fake = make_magnet(replies)
        self.addCleanup(magnet.close)
        return magnet, fake


class TestFieldParameter(FastBi1K5TestCase):
    def test_get_returns_scaled_field(self) -> None:
        magnet, _ = self.make()
        self.assertAlmostEqual(magnet.field(), 7.3 * magnet.T_per_A)  # = 1.0 T

    def test_get_uses_averaged_readback(self) -> None:
        magnet, fake = self.make()
        magnet.field()
        self.assertEqual(fake.sent, ["GET:I:?"])

    def test_is_qcodes_parameter(self) -> None:
        magnet, _ = self.make()
        self.assertIsInstance(magnet.field, Parameter)
        self.assertEqual(magnet.field.full_name, f"{magnet.name}_field")
        self.assertIs(magnet.field.instrument, magnet)
        self.assertEqual(magnet.field.unit, "T")


class TestRamp(FastBi1K5TestCase):
    def test_set_sequence(self) -> None:
        polls = iter([RAMPING, RAMPING, IDLE])
        replies = dict(HEALTHY, **{"REG:STATUS:?": lambda: next(polls)})
        magnet, fake = self.make(replies)

        magnet.field(1.0)

        slew_A_per_s = magnet.slew_T_per_s / magnet.T_per_A
        current_target = 1.0 / magnet.T_per_A
        expected_set = f"SET:I:{slew_A_per_s}:{current_target}"
        self.assertIn(expected_set, fake.sent)
        # safety status queries precede the setpoint
        self.assertLess(fake.sent.index("OUT:?"), fake.sent.index(expected_set))
        # polled until the ramping bit cleared (3 polls), all after SET:I
        self.assertEqual(fake.sent.count("REG:STATUS:?"), 3)
        self.assertLess(fake.sent.index(expected_set), fake.sent.index("REG:STATUS:?"))
        # throttled poll (no tight spin) then the settle dwell
        self.assertIn(mock.call(magnet.poll_interval_s), self.sleeps.call_args_list)
        self.assertIn(mock.call(magnet.settle_s), self.sleeps.call_args_list)

    def test_rejects_field_over_max(self) -> None:
        magnet, fake = self.make()
        with self.assertRaisesRegex(ValueError, "exceeds maximum field"):
            magnet.field(14.1)
        self.assertEqual(fake.sent, [])  # rejected before any hardware traffic

    def test_rejects_persistent_switch_off(self) -> None:
        replies = dict(HEALTHY, **{"SWITCH:PERSISTENT:?": "#SWITCH:PERSISTENT:DISABLED"})
        magnet, fake = self.make(replies)
        with self.assertRaisesRegex(ValueError, "Persistent Switch On : False"):
            magnet.field(1.0)
        self.assertFalse(any(c.startswith("SET:I:") for c in fake.sent))

    def test_rejects_output_disabled(self) -> None:
        replies = dict(HEALTHY, **{"OUT:?": "#OUT:OFF"})
        magnet, fake = self.make(replies)
        with self.assertRaisesRegex(ValueError, "Output Enabled       : False"):
            magnet.field(1.0)
        self.assertFalse(any(c.startswith("SET:I:") for c in fake.sent))

    def test_session_cap_via_vals(self) -> None:
        # SAFETIES cell sets magnet.field.vals to enforce B_SESSION_CAP.
        magnet, fake = self.make()
        magnet.field.vals = validators.Numbers(-8.0, 8.0)
        with self.assertRaises(ValueError):
            magnet.field(9.0)
        self.assertEqual(fake.sent, [])  # rejected before any hardware traffic

    def test_nak_raises(self) -> None:
        replies = dict(HEALTHY)
        magnet, fake = self.make(replies)
        slew_A_per_s = magnet.slew_T_per_s / magnet.T_per_A
        current_target = 1.0 / magnet.T_per_A
        fake.replies[f"SET:I:{slew_A_per_s}:{current_target}"] = "#NAK:09"
        with self.assertRaisesRegex(RuntimeError, "NAK"):
            magnet.field(1.0)


class TestStartFieldRamp(FastBi1K5TestCase):
    def test_issues_and_returns_without_polling(self) -> None:
        magnet, fake = self.make()
        magnet.start_field_ramp(1.0)
        self.assertTrue(any(c.startswith("SET:I:") for c in fake.sent))
        # non-blocking: never reads the ramp flag, never settles
        self.assertEqual(fake.sent.count("REG:STATUS:?"), 0)
        self.assertNotIn(mock.call(magnet.settle_s), self.sleeps.call_args_list)

    def test_stashes_start_and_target(self) -> None:
        magnet, _ = self.make()
        magnet.start_field_ramp(2.0)
        self.assertEqual(magnet._ramp_target, 2.0)
        self.assertAlmostEqual(magnet._ramp_start, 1.0)  # field at issue (7.3 A x T_per_A)

    def test_cap_via_vals_applies_to_async_path(self) -> None:
        # _check_target runs field.validate, so the session cap fences the
        # non-blocking path too (it bypasses the qcodes Parameter layer).
        magnet, fake = self.make()
        magnet.field.vals = validators.Numbers(-8.0, 8.0)
        with self.assertRaises(ValueError):
            magnet.start_field_ramp(9.0)
        self.assertEqual(fake.sent, [])

    def test_over_max_rejected_async(self) -> None:
        magnet, fake = self.make()
        with self.assertRaisesRegex(ValueError, "exceeds maximum field"):
            magnet.start_field_ramp(14.1)
        self.assertEqual(fake.sent, [])


class TestStash(FastBi1K5TestCase):
    """The stash invariant: _ramp_target == the last commanded target."""

    def test_blocking_set_stashes_target(self) -> None:
        polls = iter([IDLE])
        replies = dict(HEALTHY, **{"REG:STATUS:?": lambda: next(polls)})
        magnet, _ = self.make(replies)
        magnet.field(1.0)
        self.assertEqual(magnet._ramp_target, 1.0)

    def test_restamped_on_each_ramp(self) -> None:
        magnet, _ = self.make()
        magnet.start_field_ramp(1.0)
        self.assertEqual(magnet._ramp_target, 1.0)
        magnet.start_field_ramp(2.0)
        self.assertEqual(magnet._ramp_target, 2.0)  # no stale carry-over

    def test_unset_before_any_ramp(self) -> None:
        magnet, _ = self.make()
        self.assertIsNone(magnet._ramp_target)
        self.assertIsNone(magnet._ramp_start)

    def test_commanded_field_property(self) -> None:
        magnet, _ = self.make()
        self.assertIsNone(magnet.commanded_field)  # no ramp yet
        magnet.start_field_ramp(2.0)
        self.assertEqual(magnet.commanded_field, 2.0)


class TestIsRamping(FastBi1K5TestCase):
    def test_true_when_bit_set(self) -> None:
        magnet, fake = self.make(dict(HEALTHY, **{"REG:STATUS:?": RAMPING}))
        self.assertTrue(magnet.is_ramping())
        self.assertEqual(fake.sent, ["REG:STATUS:?"])  # single query, no dwell

    def test_false_when_idle(self) -> None:
        magnet, fake = self.make(dict(HEALTHY, **{"REG:STATUS:?": IDLE}))
        self.assertFalse(magnet.is_ramping())
        self.assertEqual(fake.sent, ["REG:STATUS:?"])

    def test_is_qcodes_parameter(self) -> None:
        magnet, _ = self.make()
        self.assertIsInstance(magnet.is_ramping, Parameter)


class TestWaitForRamp(FastBi1K5TestCase):
    def test_polls_flag_then_flat_settle(self) -> None:
        polls = iter([RAMPING, IDLE])
        replies = dict(HEALTHY, **{"REG:STATUS:?": lambda: next(polls)})
        magnet, fake = self.make(replies)
        magnet._ramp_target = 1.0
        magnet._ramp_start = 0.0
        magnet.wait_for_ramp()
        self.assertEqual(fake.sent.count("REG:STATUS:?"), 2)
        self.assertIn(mock.call(magnet.settle_s), self.sleeps.call_args_list)

    def test_dynamic_settle_waits_for_readback_convergence(self) -> None:
        # flag idle immediately; then poll field() until within tol of target.
        gets = iter(["#GET:I:7.0", "#GET:I:7.3"])  # 0.959 T (far) -> 1.0 T (converged)
        replies = dict(
            HEALTHY,
            **{"REG:STATUS:?": IDLE, "GET:I:?": lambda: next(gets)},
        )
        magnet, fake = self.make(replies)
        magnet._ramp_target = 1.0
        magnet._ramp_start = 0.0
        magnet.wait_for_ramp(tol=0.01)
        self.assertEqual(fake.sent.count("GET:I:?"), 2)  # one far, one converged
        # dynamic settle, not the flat dwell
        self.assertNotIn(mock.call(magnet.settle_s), self.sleeps.call_args_list)

    def test_timeout_auto_raises(self) -> None:
        magnet, _ = self.make(dict(HEALTHY, **{"REG:STATUS:?": RAMPING}))
        magnet._ramp_target = 0.0
        magnet._ramp_start = 0.0  # dB=0 -> small auto bound
        with mock.patch("drivers.FastBi1K5.time.monotonic", side_effect=[0.0, 1e6]):
            with self.assertRaises(TimeoutError):
                magnet.wait_for_ramp()

    def test_timeout_inf_never_trips(self) -> None:
        polls = iter([RAMPING, IDLE])
        replies = dict(HEALTHY, **{"REG:STATUS:?": lambda: next(polls)})
        magnet, _ = self.make(replies)
        magnet._ramp_target = 1.0
        magnet._ramp_start = 0.0
        with mock.patch("drivers.FastBi1K5.time.monotonic", return_value=1e9):
            magnet.wait_for_ramp(timeout=math.inf)  # must not raise

    def test_auto_timeout_fallback_without_stash(self) -> None:
        magnet, _ = self.make()
        self.assertGreater(magnet._auto_timeout(), 0.0)  # no stash -> finite worst-case bound


class TestSupplySurface(FastBi1K5TestCase):
    def test_status_dict(self) -> None:
        magnet, _ = self.make()
        s = magnet._status()
        self.assertAlmostEqual(s["field"], 1.0)
        self.assertAlmostEqual(s["voltage"], 1.5)
        self.assertTrue(s["output_enabled"])
        self.assertTrue(s["persistent_switch_on"])
        self.assertEqual(s["loop_mode"], "I")
        self.assertEqual(s["update_mode"], "NORMAL")

    def test_status_queries_each_value_once(self) -> None:
        magnet, fake = self.make()
        magnet.status()
        for cmd in ("OUT:?", "SWITCH:PERSISTENT:?", "LOOP:?", "UPMODE:?", "GET:I:?", "GET:V:?"):
            self.assertEqual(fake.sent.count(cmd), 1)

    def test_output_enabled_accessor(self) -> None:
        magnet, fake = self.make()
        self.assertTrue(magnet.output_enabled())
        self.assertEqual(fake.sent, ["OUT:?"])  # single query, no full status round

    def test_output_enabled_false(self) -> None:
        magnet, _ = self.make(dict(HEALTHY, **{"OUT:?": "#OUT:OFF"}))
        self.assertFalse(magnet.output_enabled())

    def test_persistent_switch_on_accessor(self) -> None:
        magnet, fake = self.make()
        self.assertTrue(magnet.persistent_switch_on())
        self.assertEqual(fake.sent, ["SWITCH:PERSISTENT:?"])  # single query

    def test_persistent_switch_off(self) -> None:
        magnet, _ = self.make(
            dict(HEALTHY, **{"SWITCH:PERSISTENT:?": "#SWITCH:PERSISTENT:DISABLED"})
        )
        self.assertFalse(magnet.persistent_switch_on())

    def test_heater_on_off(self) -> None:
        magnet, fake = self.make()
        magnet.heater_on()
        magnet.heater_off()
        self.assertEqual(
            fake.sent, ["SWITCH:PERSISTENT:ENABLE", "SWITCH:PERSISTENT:DISABLE"]
        )
        self.assertEqual(self.sleeps.call_args_list, [mock.call(10), mock.call(10)])

    def test_close_shuts_socket(self) -> None:
        magnet, fake = self.make()
        magnet.close()
        self.assertTrue(fake.closed)


class TestSweepCompat(FastBi1K5TestCase):
    """What sweep.Station actually requires of a swept/followed param."""

    def test_followable(self) -> None:
        magnet, _ = self.make()
        p = magnet.field
        self.assertAlmostEqual(p() / 1.0, 1.0)  # Station._measure: p() / gain
        self.assertIsInstance(p.full_name, str)  # Station._col_names
        self.assertIsNotNone(p.instrument)       # Station._instruments

    def test_sweepable(self) -> None:
        polls = iter([IDLE])
        replies = dict(HEALTHY, **{"REG:STATUS:?": lambda: next(polls)})
        magnet, _ = self.make(replies)
        magnet.field(0.5)  # Station sweeps call param(value)


if __name__ == "__main__":
    unittest.main()
