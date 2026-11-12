import inspect
import unittest
from functools import partial

import numpy as np

from sharpelab_nb.leakage import (
    LeakageDetector,
    k2400_leakage_guard,
    leakage_check,
    leakage_check_after,
)


def _ramp(v_end=10.0, n=600, offset=20e-12, slope=0.5e-12, noise=2e-12, seed=0):
    """A continuous outward push: flat-ish baseline + small noise, no knee."""
    rng = np.random.default_rng(seed)
    V = np.linspace(0.0, v_end, n)
    I = offset + slope * V + rng.normal(0.0, noise, n)
    return V, I


def _knee(V, I, knee=7.0, strength=20e-12):
    return I + np.where(V > knee, strength * (V - knee) ** 2, 0.0)


def _replay(V, I, **kw):
    g = LeakageDetector(**kw)
    for v, i in zip(V, I):
        if g.update(float(v), float(i)):
            break
    return g


class _Station:
    interrupt_requested = False


def _dispatch(fn, args, context):
    """Mirror ``sweep.Station._run_run_{befores,afters}``: pass ``args`` positionally,
    inject only the context entries whose names match the callable's parameters."""
    sig = inspect.signature(fn)
    accepted = {k: v for k, v in context.items() if k in sig.parameters}
    return fn(*args, **accepted)


class TestLeakageDetector(unittest.TestCase):
    def test_sharp_knee_trips_at_the_foot(self) -> None:
        V, I = _ramp()
        g = _replay(V, _knee(V, I))
        self.assertTrue(g.tripped)
        assert g.trip_V is not None
        self.assertGreater(g.trip_V, 6.0)   # foot near the knee...
        self.assertLess(g.trip_V, 8.5)      # ...not deep into the runaway

    def test_flat_ramp_does_not_trip(self) -> None:
        V, I = _ramp()
        self.assertFalse(_replay(V, I).tripped)

    def test_higher_stationary_noise_does_not_trip(self) -> None:
        # self-calibration tolerates a uniformly noisier device (no knee): the
        # baseline noise estimate scales, so nothing exceeds threshold.
        # (Known limitation, NOT asserted: a sharp *non-stationary* noise burst
        # can still false-abort -- accepted, since a live restart is cheap, and the
        # recipe's averaging step keeps bursts small.)
        V, I = _ramp(noise=5e-12, seed=2)
        self.assertFalse(_replay(V, I).tripped)

    def test_baseline_calibrated_from_safe_start(self) -> None:
        g = _replay(*_ramp())
        self.assertIsNotNone(g.b0)
        self.assertIsNotNone(g.sigma_I)

    def test_leakage_check_sets_interrupt(self) -> None:
        V, I = _ramp()
        I = _knee(V, I)
        station = _Station()
        det = LeakageDetector()
        idx = [0]
        for k in range(len(V)):
            idx[0] = k
            leakage_check(det, lambda: float(I[idx[0]]), lambda: float(V[idx[0]]), station)
            if station.interrupt_requested:
                break
        self.assertTrue(station.interrupt_requested)


class _FakeK2400:
    """Minimal qcodes-2400 stand-in: nplci/rangei params, write/ask, curr/volt feed."""

    def __init__(self, V, I) -> None:
        self._V, self._I, self._idx = V, I, 0
        self._nplci, self._rangei = 1.0, 1e-6
        self.scpi: list[str] = []

    def nplci(self, v=None):
        if v is None:
            return self._nplci
        self._nplci = v

    def rangei(self, v=None):
        if v is None:
            return self._rangei
        self._rangei = v

    def write(self, cmd: str) -> None:
        self.scpi.append(cmd)

    def ask(self, _cmd: str) -> str:
        return "0"

    def volt(self) -> float:
        return float(self._V[self._idx])

    def curr(self) -> float:
        return float(self._I[self._idx])


class TestK2400Guard(unittest.TestCase):
    def test_configures_trips_and_restores(self) -> None:
        V, I = _ramp()
        I = _knee(V, I)
        k = _FakeK2400(V, I)
        station = _Station()
        with k2400_leakage_guard(k, nplc=10, avg_n=6, rangei=1e-9) as guard:
            self.assertEqual(k.nplci(), 10)          # configured
            self.assertEqual(k.rangei(), 1e-9)
            self.assertTrue(any("AVER:COUNT 6" in c for c in k.scpi))
            for j in range(len(V)):
                k._idx = j
                guard.check(station)
                if guard.tripped:
                    break
            self.assertTrue(guard.tripped)
            assert guard.trip_V is not None
        # restored on exit
        self.assertEqual(k.nplci(), 1.0)
        self.assertEqual(k.rangei(), 1e-6)


class _NoReadK2400(_FakeK2400):
    """A 2400 stand-in whose live-read parameters BLOW UP — proves ``check_after``
    never touches the instrument (its values come from the sweep's ``data`` row)."""

    def volt(self) -> float:
        raise AssertionError("check_after must not read volt()")

    def curr(self) -> float:
        raise AssertionError("check_after must not read curr()")


class TestLeakageCheckAfter(unittest.TestCase):
    """The zero-read ``register_run_after`` path: detector fed V=setpoint, I=fp."""

    def test_module_after_trips_at_knee(self) -> None:
        # data = [time, setpoint, gate_curr]; i_col=2 (gate current is first fp).
        V, I = _ramp()
        I = _knee(V, I)
        station = _Station()
        det = LeakageDetector()
        for v, i in zip(V, I):
            leakage_check_after(det, station, [0.0, float(v), float(i)])
            if station.interrupt_requested:
                break
        self.assertTrue(station.interrupt_requested)
        assert det.trip_V is not None
        self.assertGreater(det.trip_V, 6.0)
        self.assertLess(det.trip_V, 8.5)

    def test_module_after_flat_ramp_does_not_trip(self) -> None:
        V, I = _ramp()
        station = _Station()
        det = LeakageDetector()
        for v, i in zip(V, I):
            leakage_check_after(det, station, [0.0, float(v), float(i)])
        self.assertFalse(station.interrupt_requested)

    def test_after_uses_v_setpoint_and_i_col(self) -> None:
        # gate current parked at col 3, a decoy flat column at 2; V=setpoint at col 1.
        V, I = _ramp()
        I = _knee(V, I)
        station = _Station()
        det = LeakageDetector()
        for v, i in zip(V, I):
            leakage_check_after(det, station, [0.0, float(v), 0.0, float(i)], i_col=3)
            if station.interrupt_requested:
                break
        self.assertTrue(station.interrupt_requested)

    def test_guard_check_after_no_instrument_reads_and_restores(self) -> None:
        # The SMU's volt()/curr() raise; check_after must trip purely off `data`.
        V, I = _ramp()
        I = _knee(V, I)
        k = _NoReadK2400(V, I)
        station = _Station()
        with k2400_leakage_guard(k, nplc=10, avg_n=6, rangei=1e-9) as guard:
            for v, i in zip(V, I):
                guard.check_after(station, [0.0, float(v), float(i)])
                if guard.tripped:
                    break
            self.assertTrue(guard.tripped)
            assert guard.trip_V is not None
        # restored on exit
        self.assertEqual(k.nplci(), 1.0)
        self.assertEqual(k.rangei(), 1e-6)

    def test_guard_check_after_flat_ramp_does_not_trip(self) -> None:
        V, I = _ramp()
        k = _NoReadK2400(V, I)
        station = _Station()
        with k2400_leakage_guard(k) as guard:
            for v, i in zip(V, I):
                guard.check_after(station, [0.0, float(v), float(i)])
            self.assertFalse(station.interrupt_requested)
            self.assertFalse(guard.tripped)


class TestHookRegistration(unittest.TestCase):
    """Registration correctness against the real sweep hook-dispatch semantics:
    ``args`` positional, context (station/data) injected by parameter name."""

    def test_run_before_guard_args_empty_is_correct(self) -> None:
        # run_before injects `station`; the correct registration is args=().
        V, I = _ramp()
        I = _knee(V, I)
        k = _FakeK2400(V, I)
        station = _Station()
        with k2400_leakage_guard(k) as guard:
            for j in range(len(V)):
                k._idx = j
                _dispatch(guard.check, (), {"station": station, "writer": None})
                if guard.tripped:
                    break
            self.assertTrue(guard.tripped)

    def test_run_before_guard_args_station_double_binds(self) -> None:
        # The fixed bug: args=(s,) + context station => duplicate `station` argument.
        k = _FakeK2400(*_ramp())
        station = _Station()
        with k2400_leakage_guard(k) as guard:
            with self.assertRaises(TypeError):
                _dispatch(guard.check, (station,), {"station": station, "writer": None})

    def test_run_before_module_leakage_check_registration(self) -> None:
        # leakage_check(detector, curr, volt, station): station from context, rest args.
        V, I = _ramp()
        I = _knee(V, I)
        station = _Station()
        det = LeakageDetector()
        idx = [0]
        for k in range(len(V)):
            idx[0] = k
            _dispatch(
                leakage_check,
                (det, lambda: float(I[idx[0]]), lambda: float(V[idx[0]])),
                {"station": station, "writer": None},
            )
            if station.interrupt_requested:
                break
        self.assertTrue(station.interrupt_requested)

    def test_run_after_guard_partial_pins_i_col(self) -> None:
        # The recipe idiom: partial(guard.check_after, i_col=N) + run_after dispatch
        # (station + data injected), with a no-read SMU proving zero instrument reads.
        V, I = _ramp()
        I = _knee(V, I)
        k = _NoReadK2400(V, I)
        station = _Station()
        with k2400_leakage_guard(k) as guard:
            fn = partial(guard.check_after, i_col=3)
            for v, i in zip(V, I):
                _dispatch(
                    fn,
                    (),
                    {"station": station, "data": [0.0, float(v), 0.0, float(i)], "writer": None},
                )
                if guard.tripped:
                    break
            self.assertTrue(guard.tripped)


if __name__ == "__main__":
    unittest.main()
