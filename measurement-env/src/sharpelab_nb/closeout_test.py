import contextlib
import io
import unittest

from qcodes.parameters import Parameter
from qcodes.validators import Numbers

from sharpelab_nb.closeout import StateRecord, close_out, read_state


def _memory_param(name: str, initial: float, log: list, log_name: str | None = None) -> Parameter:
    """A qcodes Parameter with real memory storage whose set_cmd also appends
    to a shared call-order log. Avoids qcodes' ``initial_value=`` kwarg,
    which would itself invoke set_cmd and pollute the log at construction
    time."""
    label = log_name or name
    state = {"value": initial}

    def _set(value: float) -> None:
        state["value"] = value
        log.append((label, value))

    def _get() -> float:
        return state["value"]

    return Parameter(name, set_cmd=_set, get_cmd=_get)


def _set_only_param(name: str, log: list) -> Parameter:
    """A drive whose get_cmd raises, like some DC205 set-only paths."""
    state = {"value": None}

    def _set(value: float) -> None:
        state["value"] = value
        log.append((name, value))

    def _get() -> float:
        raise RuntimeError("no readback on this channel")

    return Parameter(name, set_cmd=_set, get_cmd=_get)


class TestReadState(unittest.TestCase):
    def test_returns_record_with_values_and_prints_names(self) -> None:
        log: list = []
        p1 = _memory_param("p1", 1.5, log)
        p2 = _memory_param("p2", 2.5, log)

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            record = read_state(a=p1, b=p2)

        self.assertEqual(len(record), 2)
        items = record.items()
        self.assertEqual(items[0][0], "a")
        self.assertIs(items[0][1], p1)
        self.assertAlmostEqual(items[0][2], 1.5)
        self.assertEqual(items[1][0], "b")
        self.assertAlmostEqual(items[1][2], 2.5)

        out = buf.getvalue()
        self.assertIn("a", out)
        self.assertIn("b", out)
        self.assertIn("1.5", out)
        self.assertIn("2.5", out)


class TestCloseOutOrdering(unittest.TestCase):
    def test_stage_order_restore_excitation_heaters_gates_mux_field(self) -> None:
        log: list = []
        restore_param = _memory_param("restore_p", 0.0, log)
        exc_param = _memory_param("exc_p", 0.0, log)
        heater_param = _memory_param("heater_p", 0.0, log)
        gate_param = _memory_param("gate_p", 0.0, log)
        field_param = _memory_param("field_p", 0.0, log)

        state0 = StateRecord([("restore_p", restore_param, 9.0)])

        class FakeMux:
            def park(self) -> None:
                log.append(("mux_park", None))

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            close_out(
                (field_param, 1.23),
                restore=state0,
                excitation=[(exc_param, 1.0)],
                heaters=[(heater_param, 2.0)],
                gates=[(gate_param, 3.0)],
                mux=FakeMux(),
            )

        labels = [entry[0] for entry in log]
        self.assertEqual(
            labels,
            ["restore_p", "exc_p", "heater_p", "gate_p", "mux_park", "field_p"],
        )

    def test_omitted_stages_touch_nothing(self) -> None:
        log: list = []
        field_param = _memory_param("field_p", 0.0, log)

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            close_out((field_param, 5.0))

        self.assertEqual(log, [("field_p", 5.0)])

    def test_restore_replay_order_and_later_stage_set_wins(self) -> None:
        log: list = []
        p1 = _memory_param("p1", 0.0, log)
        p2 = _memory_param("p2", 0.0, log)
        field_param = _memory_param("field_p", 0.0, log)

        state0 = StateRecord(
            [
                ("p1", p1, 1.0),
                ("p2", p2, 2.0),
            ]
        )

        with contextlib.redirect_stdout(io.StringIO()):
            close_out(
                (field_param, 0.0),
                restore=state0,
                gates=[(p1, 99.0)],
            )

        # restore replays in capture order (p1 then p2), then the gates
        # stage re-sets p1 afterward, so p1's last write in the log wins.
        self.assertEqual(
            [entry[0] for entry in log],
            ["p1", "p2", "p1", "field_p"],
        )
        self.assertAlmostEqual(p1(), 99.0)


class TestCloseOutField(unittest.TestCase):
    def test_hold_variant_never_sets_field_and_reports_held(self) -> None:
        log: list = []
        field_param = _memory_param("field_p", 4.2, log)

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            close_out((field_param, "hold"))

        self.assertEqual(log, [])  # field never set
        self.assertAlmostEqual(field_param(), 4.2)
        out = buf.getvalue()
        self.assertIn("FIELD HELD", out)
        self.assertIn("4.2", out)

    def test_field_readback_is_measured_not_setpoint(self) -> None:
        """After a set, the field line reports the measured value (read-truth,
        rig-card doctrine) — e.g. remanence makes measured != setpoint."""
        log: list = []
        state = {"value": 0.0}

        def _set(value: float) -> None:
            state["value"] = value + 0.007  # remanence-like offset
            log.append(("field_p", value))

        field_param = Parameter("field_p", set_cmd=_set, get_cmd=lambda: state["value"])

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            close_out((field_param, 1.0))

        self.assertIn("field : 1.007 T", buf.getvalue())

    def test_field_in_restore_raises(self) -> None:
        log: list = []
        field_param = _memory_param("field_p", 0.0, log)
        state0 = StateRecord([("field_p", field_param, 1.0)])

        with self.assertRaises(ValueError):
            close_out((field_param, 0.0), restore=state0)

    def test_field_in_stage_raises(self) -> None:
        log: list = []
        field_param = _memory_param("field_p", 0.0, log)

        with self.assertRaises(ValueError):
            close_out((field_param, 0.0), gates=[(field_param, 1.0)])


class TestCloseOutStageItems(unittest.TestCase):
    def test_labeled_callable_executes_and_prints_label(self) -> None:
        log: list = []
        field_param = _memory_param("field_p", 0.0, log)
        called = {"n": 0}

        def _heater_off() -> None:
            called["n"] += 1
            log.append(("heater_off", None))

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            close_out(
                (field_param, 0.0),
                heaters=[("LS335 heater range off", _heater_off)],
            )

        self.assertEqual(called["n"], 1)
        self.assertIn("LS335 heater range off", buf.getvalue())
        self.assertEqual([e[0] for e in log], ["heater_off", "field_p"])


class TestCloseOutReadback(unittest.TestCase):
    def test_set_only_param_prints_setpoint_marker(self) -> None:
        log: list = []
        field_param = _memory_param("field_p", 0.0, log)
        drive = _set_only_param("drive", log)

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            close_out((field_param, 0.0), excitation=[(drive, 7.0)])

        out = buf.getvalue()
        self.assertIn("(setpoint — no readback)", out)
        self.assertIn("7.0", out)

    def test_validator_repr_appears_in_readback(self) -> None:
        log: list = []
        field_param = _memory_param("field_p", 0.0, log)
        gate = Parameter(
            "gate_v",
            set_cmd=lambda v: log.append(("gate_v", v)),
            get_cmd=lambda: 3.0,
            vals=Numbers(-10, 10),
        )

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            close_out((field_param, 0.0), gates=[(gate, 3.0)])

        out = buf.getvalue()
        self.assertIn("Numbers", out)

    def test_extra_readback_appended(self) -> None:
        log: list = []
        field_param = _memory_param("field_p", 0.0, log)
        extra = _memory_param("T_mix", 0.123, log)

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            close_out((field_param, 0.0), extra_readback={"T_mix": extra})

        out = buf.getvalue()
        self.assertIn("T_mix", out)
        self.assertIn("0.123", out)


if __name__ == "__main__":
    unittest.main()
