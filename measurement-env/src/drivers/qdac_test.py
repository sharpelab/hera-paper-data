import unittest

from qcodes import validators

from drivers.qdac import bring_up_qdac_gate


class FakeParam:
    """Callable stand-in for a qcodes Parameter: ``p()`` gets, ``p(x)`` sets."""

    def __init__(self, value=None) -> None:
        self._value = value
        self.step = None
        self.vals = None
        self.sets: list = []

    def __call__(self, *args):
        if args:
            self._value = args[0]
            self.sets.append(args[0])
            return None
        return self._value


class FakeChannel:
    def __init__(self) -> None:
        self.dc_constant_V = FakeParam(0.0)
        self.read_current_A = FakeParam(0.0)
        self.dc_slew_rate_V_per_s = FakeParam()
        self.output_range = FakeParam()
        self.output_filter = FakeParam()
        self.measurement_range = FakeParam()
        self.measurement_nplc = FakeParam()


class TestBringUpQdacGate(unittest.TestCase):
    def test_defaults_configure_channel(self) -> None:
        ch = FakeChannel()
        out = bring_up_qdac_gate(ch, limit=(-8, 8))
        self.assertIs(out, ch)
        self.assertEqual(ch.output_range(), "high")
        self.assertEqual(ch.output_filter(), "dc")
        self.assertEqual(ch.dc_constant_V.step, 0.005)
        # hard fence installed and enforced
        self.assertIsInstance(ch.dc_constant_V.vals, validators.Numbers)
        ch.dc_constant_V.vals.validate(7.9)  # inside fence: ok
        with self.assertRaises(ValueError):
            ch.dc_constant_V.vals.validate(9.0)  # outside fence: rejected
        # optional knobs left untouched
        self.assertEqual(ch.dc_slew_rate_V_per_s.sets, [])
        self.assertEqual(ch.measurement_range.sets, [])
        self.assertEqual(ch.measurement_nplc.sets, [])

    def test_limit_exceeding_high_range_rejected(self) -> None:
        # The Si-gate guardrail: a ±50 V fence cannot fit the QDAC ±10 V range.
        ch = FakeChannel()
        with self.assertRaises(AssertionError):
            bring_up_qdac_gate(ch, limit=(-50, 50))

    def test_limit_exceeding_low_range_rejected(self) -> None:
        ch = FakeChannel()
        with self.assertRaises(AssertionError):
            bring_up_qdac_gate(ch, limit=(-8, 8), output_range="low")

    def test_optional_knobs_passed_through(self) -> None:
        ch = FakeChannel()
        bring_up_qdac_gate(
            ch,
            limit=(-2, 2),
            step=0.001,
            slew=0.5,
            output_range="low",
            output_filter="med",
            meas_range="low",
            meas_nplc=10,
        )
        self.assertEqual(ch.output_range(), "low")
        self.assertEqual(ch.output_filter(), "med")
        self.assertEqual(ch.dc_slew_rate_V_per_s(), 0.5)
        self.assertEqual(ch.dc_constant_V.step, 0.001)
        self.assertEqual(ch.measurement_range(), "low")
        self.assertEqual(ch.measurement_nplc(), 10)


if __name__ == "__main__":
    unittest.main()
