import logging
import tempfile
import unittest

from qcodes.instrument_drivers.mock_instruments import DummyInstrument
from qcodes.parameters import Parameter

import sweep


class DummyBase(DummyInstrument):
    """Base for lock-in mocks: adds X, Y, R, P parameters."""

    def __init__(self, name: str) -> None:
        super().__init__(name, gates=["X", "Y", "R", "P"])
        self.X(1.0)
        self.Y(2.0)
        self.R(3.0)
        self.P(4.0)


class DummySR830(DummyBase):
    """Mock SR830 with SNAP_PARAMETERS and snap()."""

    SNAP_PARAMETERS: dict[str, str] = {
        "x": "1",
        "y": "2",
        "r": "3",
        "p": "4",
    }

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.snap_call_count = 0

    def snap(self, *names: str) -> tuple[float, ...]:
        self.snap_call_count += 1
        lookup = {n.lower(): getattr(self, n.upper())() for n in names}
        return tuple(lookup[n.lower()] for n in names)


class DummySR86x(DummyBase):
    """Mock SR86x with PARAMETER_NAMES and get_values()."""

    PARAMETER_NAMES: dict[str, str] = {
        "X": "0",
        "Y": "1",
        "R": "2",
        "P": "3",
    }

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.get_values_call_count = 0

    def get_values(self, *names: str) -> tuple[float, ...]:
        self.get_values_call_count += 1
        return tuple(getattr(self, n)() for n in names)


class FlakySR830(DummySR830):
    """Mock SR830 whose snap() raises ValueError for the first `failures` calls."""

    def __init__(self, name: str, failures: int) -> None:
        super().__init__(name)
        self.failures = failures

    def snap(self, *names: str) -> tuple[float, ...]:
        if self.failures > 0:
            self.failures -= 1
            self.snap_call_count += 1
            raise ValueError("could not convert string to float: '173.232-'")
        return super().snap(*names)


def _close_sweep_log_handlers() -> None:
    """Windows: the Station's log FileHandler keeps log.log open, which blocks
    TemporaryDirectory cleanup (WinError 32). Close them before rmtree."""
    for name, logger in list(logging.Logger.manager.loggerDict.items()):
        if name.startswith("sweep_log") and isinstance(logger, logging.Logger):
            for h in list(logger.handlers):
                h.close()
                logger.removeHandler(h)


class TestAsyncStationBatchRead(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        _close_sweep_log_handlers()
        self.dir.cleanup()

    def _make_station(self) -> sweep.AsyncStation:
        return sweep.AsyncStation(basedir=self.dir.name, verbose=False)

    def test_sr830_snap_used(self) -> None:
        """SR830-style batch path taken, correct values."""
        sr830 = DummySR830("sr830_snap")
        s = self._make_station()
        s.fp(sr830.X).fp(sr830.Y)

        result = s._measure_by_inst([sr830.X, sr830.Y])

        self.assertEqual(result, [1.0, 2.0])
        self.assertEqual(sr830.snap_call_count, 1)
        sr830.close()

    def test_sr86x_get_values_used(self) -> None:
        """SR86x-style batch path taken, correct values."""
        sr86x = DummySR86x("sr86x_gv")
        s = self._make_station()
        s.fp(sr86x.X).fp(sr86x.Y)

        result = s._measure_by_inst([sr86x.X, sr86x.Y])

        self.assertEqual(result, [1.0, 2.0])
        self.assertEqual(sr86x.get_values_call_count, 1)
        sr86x.close()

    def test_single_param_no_snap(self) -> None:
        """Single param falls back to sequential (no snap)."""
        sr830 = DummySR830("sr830_single")
        s = self._make_station()
        s.fp(sr830.X)

        result = s._measure_by_inst([sr830.X])

        self.assertEqual(result, [1.0])
        self.assertEqual(sr830.snap_call_count, 0)
        sr830.close()

    def test_dummy_instrument_fallback(self) -> None:
        """Standard DummyInstrument (no snap) falls back to sequential."""
        dac = DummyInstrument("dac_fallback", gates=["ch1", "ch2"])
        dac.ch1(5.0)
        dac.ch2(6.0)
        s = self._make_station()
        s.fp(dac.ch1).fp(dac.ch2)

        result = s._measure_by_inst([dac.ch1, dac.ch2])

        self.assertEqual(result, [5.0, 6.0])
        dac.close()

    def test_sr86x_too_many_params_fallback(self) -> None:
        """4 params on SR86x exceeds limit of 3, falls back to sequential."""
        sr86x = DummySR86x("sr86x_toomany")
        s = self._make_station()
        s.fp(sr86x.X).fp(sr86x.Y).fp(sr86x.R).fp(sr86x.P)

        result = s._measure_by_inst([sr86x.X, sr86x.Y, sr86x.R, sr86x.P])

        self.assertEqual(result, [1.0, 2.0, 3.0, 4.0])
        self.assertEqual(sr86x.get_values_call_count, 0)
        sr86x.close()

    def test_gain_with_batch_read(self) -> None:
        """Gains applied correctly after batch read."""
        sr830 = DummySR830("sr830_gain")
        sr830.X(10.0)
        sr830.Y(6.0)
        s = self._make_station()
        s.fp(sr830.X, gain=2.0).fp(sr830.Y, gain=3.0)

        # _measure applies gains via _measure → ret[p] / gain
        result = s._measure()

        self.assertEqual(result, [5.0, 2.0])
        self.assertEqual(sr830.snap_call_count, 1)
        sr830.close()

    def test_mixed_instruments(self) -> None:
        """SR830 (batched) + DummyInstrument (sequential) in same station."""
        sr830 = DummySR830("sr830_mixed")
        dac = DummyInstrument("dac_mixed", gates=["ch1"])
        dac.ch1(9.0)
        s = self._make_station()
        s.fp(sr830.X).fp(sr830.Y).fp(dac.ch1)

        result = s._measure()

        self.assertEqual(result, [1.0, 2.0, 9.0])
        self.assertEqual(sr830.snap_call_count, 1)
        sr830.close()
        dac.close()

    def test_unmapped_param_fallback(self) -> None:
        """Param name not in SNAP_PARAMETERS falls back to sequential."""
        sr830 = DummySR830("sr830_unmapped")
        # Add a parameter whose name isn't in SNAP_PARAMETERS
        sr830.add_parameter("Q", set_cmd=None, get_cmd=None)
        sr830.Q(7.0)
        s = self._make_station()
        s.fp(sr830.X).fp(sr830.Q)

        result = s._measure_by_inst([sr830.X, sr830.Q])

        self.assertEqual(result, [1.0, 7.0])
        self.assertEqual(sr830.snap_call_count, 0)
        sr830.close()


class TestReadRetry(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        _close_sweep_log_handlers()
        self.dir.cleanup()

    def _make_station(self) -> sweep.AsyncStation:
        return sweep.AsyncStation(basedir=self.dir.name, verbose=False)

    def test_snap_retried_once(self) -> None:
        """One garbled snap reply → warning + clean re-read, point survives."""
        sr830 = FlakySR830("sr830_flaky1", failures=1)
        s = self._make_station()
        s.fp(sr830.X).fp(sr830.Y)

        with self.assertLogs(s.logger, level="WARNING"):
            result = s._measure_by_inst([sr830.X, sr830.Y])

        self.assertEqual(result, [1.0, 2.0])
        self.assertEqual(sr830.snap_call_count, 2)
        sr830.close()

    def test_snap_second_failure_raises(self) -> None:
        """Two garbled replies in a row → ValueError propagates, no third try."""
        sr830 = FlakySR830("sr830_flaky2", failures=2)
        s = self._make_station()
        s.fp(sr830.X).fp(sr830.Y)

        with self.assertRaises(ValueError):
            s._measure_by_inst([sr830.X, sr830.Y])

        self.assertEqual(sr830.snap_call_count, 2)
        sr830.close()

    def test_serial_read_retried_once(self) -> None:
        """Base Station serial path retries a parameter get that fails once."""
        calls = {"n": 0}

        def flaky_get() -> float:
            calls["n"] += 1
            if calls["n"] == 1:
                raise ValueError("could not convert string to float: ''")
            return 42.0

        p = Parameter("flaky", get_cmd=flaky_get, set_cmd=None)
        s = sweep.Station(basedir=self.dir.name, verbose=False)
        s.fp(p)

        with self.assertLogs(s.logger, level="WARNING"):
            result = s._measure()

        self.assertEqual(result, [42.0])
        self.assertEqual(calls["n"], 2)


if __name__ == "__main__":
    unittest.main()
