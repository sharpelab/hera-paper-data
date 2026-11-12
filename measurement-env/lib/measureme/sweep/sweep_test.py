import logging
import signal
import tempfile
import unittest
from typing import Any, cast

from qcodes.instrument_drivers.mock_instruments import DummyInstrument

import sweep
import sweep.db as db
import sweep.sweep
from sweep.types import SweepMetadata


def _close_sweep_log_handlers() -> None:
    """Windows: the Station's log FileHandler keeps log.log open, which blocks
    TemporaryDirectory cleanup (WinError 32). Close them before rmtree."""
    for name, logger in list(logging.Logger.manager.loggerDict.items()):
        if name.startswith("sweep_log") and isinstance(logger, logging.Logger):
            for h in list(logger.handlers):
                h.close()
                logger.removeHandler(h)


class TestStation(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        self.dac = DummyInstrument("dac", gates=["ch1", "ch2", "ch3"])

    def tearDown(self) -> None:
        self.dac.close()
        _close_sweep_log_handlers()
        self.dir.cleanup()

    def test_measure(self) -> None:
        self.dac.ch1(1.0)
        self.dac.ch2(2.0)
        s = sweep.Station(basedir=self.dir.name, verbose=True)
        s.fp(self.dac.ch1).fp(self.dac.ch2)
        res = s.measure()
        with db.Reader(res.basedir, res.id) as r:
            self.assertEqual(r.metadata["type"], "0D")
            self.assertEqual(r.metadata["columns"][0], "time")
            self.assertEqual(r.metadata["columns"][1], "dac_ch1")
            self.assertEqual(len(r.all_data()), 1)
            self.assertEqual(float(r.all_data()[0][1]), 1.0)

    def test_sweep(self) -> None:
        self.dac.ch2(1.0)
        self.dac.ch3(2.0)
        s = sweep.Station(basedir=self.dir.name, verbose=True)
        s.fp(self.dac.ch2).fp(self.dac.ch3)
        res = s.sweep(self.dac.ch1, range(100))
        with db.Reader(res.basedir, res.id) as r:
            md = cast(SweepMetadata, r.metadata)
            self.assertEqual(md["type"], "1D")
            self.assertEqual(md["param"], "dac_ch1")
            self.assertEqual(md["columns"][0], "time")
            self.assertEqual(md["columns"][1], "dac_ch1")
            self.assertEqual(md["columns"][2], "dac_ch2")
            self.assertEqual(md["columns"][3], "dac_ch3")
            self.assertEqual(len(r.all_data()), 100)

    def test_sweep_plot(self) -> None:
        self.dac.ch2(1.0)
        self.dac.ch3(2.0)
        s = sweep.Station(basedir=self.dir.name, verbose=True)
        s.fp(self.dac.ch2).fp(self.dac.ch3)
        s.plot("dac_ch1", "dac_ch2")
        res = s.sweep(self.dac.ch1, range(10))
        with db.Reader(res.basedir, res.id) as r:
            self.assertEqual(len(r.all_data()), 10)
            self.assertTrue(len(r.blob("plot.png")) > 0)


class TestInterrupt(unittest.TestCase):
    """Contract: an interrupt during sweep N of a loop ends sweep N gracefully
    (point finished, writer closed, metadata flagged) and then propagates, so
    sweep N+1 never starts."""

    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        self.dac = DummyInstrument("dac", gates=["ch1", "ch2"])

    def tearDown(self) -> None:
        sweep.sweep._shutdown_handler = None
        sweep.sweep._shutdown_requested = False
        self.dac.close()
        _close_sweep_log_handlers()
        self.dir.cleanup()

    def _station(self) -> sweep.Station:
        s = sweep.Station(basedir=self.dir.name, verbose=False)
        s.fp(self.dac.ch2)
        return s

    def _interrupt_at(self, s: sweep.Station, point: int) -> None:
        """Deliver SIGINT after the sweep has measured `point` points."""
        count = [0]

        def hook() -> None:
            count[0] += 1
            if count[0] == point:
                signal.raise_signal(signal.SIGINT)

        s.register_run_after(hook, args=())

    def test_interrupt_ends_sweep_gracefully_then_raises(self) -> None:
        s = self._station()
        self._interrupt_at(s, 3)
        with self.assertRaises(KeyboardInterrupt):
            s.sweep(self.dac.ch1, range(10))
        # Graceful wind-down: writer closed (gzip readable), interrupt recorded,
        # the in-flight point completed and nothing after it ran.
        with db.Reader(self.dir.name, 0) as r:
            self.assertTrue(r.metadata["interrupted"])
            self.assertEqual(len(r.all_data()), 3)
        # Second line of defense: reusing the same station raises immediately.
        with self.assertRaises(InterruptedError):
            s.sweep(self.dac.ch1, range(10))

    def test_interrupt_stops_loop_of_fresh_stations(self) -> None:
        # The zf1 Tc-ladder shape (2026-06-23 cell 65): a fresh station per
        # rung. Interrupt during rung 1 -> rung 2 must never start.
        started: list[int] = []
        completed: list[int] = []
        with self.assertRaises(KeyboardInterrupt):
            for i in range(2):
                s = self._station()
                self._interrupt_at(s, 2)
                started.append(i)
                s.sweep(self.dac.ch1, range(5))
                completed.append(i)
        self.assertEqual(started, [0])
        self.assertEqual(completed, [])

    def test_finally_still_runs_on_interrupt(self) -> None:
        # Hardware-safety semantics: park/safe code in finally must execute.
        parked: list[bool] = []
        s = self._station()
        self._interrupt_at(s, 1)
        with self.assertRaises(KeyboardInterrupt):
            try:
                s.sweep(self.dac.ch1, range(5))
            finally:
                parked.append(True)
        self.assertEqual(parked, [True])

    def test_megasweep_interrupt_ends_gracefully_then_raises(self) -> None:
        s = self._station()
        self._interrupt_at(s, 4)
        with self.assertRaises(KeyboardInterrupt):
            s.megasweep(self.dac.ch1, range(3), self.dac.ch2, range(5))
        with db.Reader(self.dir.name, 0) as r:
            self.assertTrue(r.metadata["interrupted"])
            self.assertEqual(len(r.all_data()), 4)

    def test_shutdown_parks_then_propagates(self) -> None:
        parked: list[bool] = []
        sweep.set_shutdown_handler(lambda: parked.append(True))
        s = self._station()
        count = [0]

        def hook() -> None:
            count[0] += 1
            if count[0] == 2:
                sweep.request_shutdown()

        s.register_run_after(hook, args=())
        with self.assertRaises(InterruptedError):
            s.sweep(self.dac.ch1, range(10))
        self.assertEqual(parked, [True])
        self.assertFalse(sweep.shutdown_requested())
        with db.Reader(self.dir.name, 0) as r:
            self.assertTrue(r.metadata["interrupted"])
            self.assertEqual(len(r.all_data()), 2)


class TestProgress(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        self.dac = DummyInstrument("dac", gates=["ch1", "ch2"])

    def tearDown(self) -> None:
        sweep.set_progress(lambda it, **k: it)
        self.dac.close()
        _close_sweep_log_handlers()
        self.dir.cleanup()

    def test_default_is_noop(self) -> None:
        # Under the default no-op factory a sweep runs to completion and every
        # setpoint is recorded (the iterable is passed through untouched).
        s = sweep.Station(basedir=self.dir.name, verbose=False)
        s.fp(self.dac.ch2)
        res = s.sweep(self.dac.ch1, range(50))
        with db.Reader(res.basedir, res.id) as r:
            self.assertEqual(len(r.all_data()), 50)

    def test_set_progress_invoked(self) -> None:
        calls: list[dict[str, Any]] = []

        def factory(iterable: Any, **kwargs: Any) -> Any:
            calls.append(kwargs)
            return iterable

        sweep.set_progress(factory)
        s = sweep.Station(basedir=self.dir.name, verbose=False)
        s.fp(self.dac.ch2)
        res = s.sweep(self.dac.ch1, range(10))
        self.assertTrue(calls)
        with db.Reader(res.basedir, res.id) as r:
            self.assertEqual(len(r.all_data()), 10)


if __name__ == "__main__":
    unittest.main()
