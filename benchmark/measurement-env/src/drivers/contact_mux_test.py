import unittest

from drivers.contact_mux import ContactMux, target_state

LINES = {"09": 4, "01": 24, "12": 22, "20": 20, "42": 19, "33": 18}
BREAKOUTS = {"source": 1, "drain": 2, "sr1+": 3, "sr1-": 4, "sr2+": 5}


class FakeQSwitch:
    """Records relay calls in order; tracks closed-relay state."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, list[tuple[int, int]]]] = []
        self.closed: set[tuple[int, int]] = set()

    def close_relays(self, relays) -> None:
        relays = list(relays)
        self.calls.append(("close", relays))
        self.closed.update(relays)

    def open_relays(self, relays) -> None:
        relays = list(relays)
        self.calls.append(("open", relays))
        self.closed.difference_update(relays)

    def state(self) -> str:
        return "(@" + ",".join(f"{l}!{t}" for l, t in sorted(self.closed)) + ")"


def make_mux() -> tuple[ContactMux, FakeQSwitch]:
    fake = FakeQSwitch()
    return ContactMux(fake, LINES, BREAKOUTS, settle_s=0), fake


class TestTargetState(unittest.TestCase):
    def test_basic_routing(self) -> None:
        state = target_state(
            LINES, BREAKOUTS, {"source": "20", "drain": "42", "sr1+": "09", "sr1-": "01"}
        )
        self.assertEqual(state, sorted([(20, 1), (19, 2), (4, 3), (24, 4)]))

    def test_multi_contact_port(self) -> None:
        state = target_state(LINES, BREAKOUTS, {"drain": ("09", "42")})
        self.assertEqual(state, sorted([(4, 2), (19, 2)]))

    def test_unknown_port(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown port"):
            target_state(LINES, BREAKOUTS, {"sr9+": "09"})

    def test_unknown_contact(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown contact"):
            target_state(LINES, BREAKOUTS, {"drain": "99"})

    def test_contact_in_two_ports(self) -> None:
        with self.assertRaisesRegex(ValueError, "one contact, one port"):
            target_state(LINES, BREAKOUTS, {"source": "20", "drain": "20"})


class TestConstructorValidation(unittest.TestCase):
    def test_rejects_ground_tap_assignment(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside 1-8"):
            ContactMux(FakeQSwitch(), LINES, {"gnd": 0})

    def test_rejects_connect_tap_assignment(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside 1-8"):
            ContactMux(FakeQSwitch(), LINES, {"thru": 9})

    def test_rejects_bad_line(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside 1-24"):
            ContactMux(FakeQSwitch(), {"09": 25}, BREAKOUTS)

    def test_rejects_duplicate_lines(self) -> None:
        with self.assertRaisesRegex(ValueError, "Duplicate line"):
            ContactMux(FakeQSwitch(), {"a": 1, "b": 1}, BREAKOUTS)

    def test_no_hardware_calls_in_ctor(self) -> None:
        fake = FakeQSwitch()
        ContactMux(fake, LINES, BREAKOUTS)
        self.assertEqual(fake.calls, [])


class TestSelect(unittest.TestCase):
    ROUTING = {"source": "20", "drain": "42", "sr1+": "09", "sr1-": "01"}

    def test_final_state(self) -> None:
        mux, fake = make_mux()
        mux.select(self.ROUTING)
        self.assertEqual(
            fake.closed, {(20, 1), (19, 2), (4, 3), (24, 4)}
        )  # routed taps closed; no grounds anywhere (unused lines float)

    def test_transition_grounds_before_routing(self) -> None:
        mux, fake = make_mux()
        mux.select(self.ROUTING)
        kinds = [k for k, _ in fake.calls]
        self.assertEqual(kinds, ["close", "open", "close", "open"])
        first_close = fake.calls[0][1]
        self.assertEqual(first_close, [(line, 0) for line in sorted(LINES.values())])
        last_open = fake.calls[3][1]
        self.assertEqual(last_open, [(line, 0) for line in sorted(LINES.values())])

    def test_reselect_clears_previous_routing(self) -> None:
        mux, fake = make_mux()
        mux.select(self.ROUTING)
        mux.select({"source": "20", "drain": "33", "sr1+": "12", "sr1-": "01"})
        self.assertEqual(
            fake.closed, {(20, 1), (18, 2), (22, 3), (24, 4)}
        )

    def test_routing_property(self) -> None:
        mux, _ = make_mux()
        mux.select({"drain": ("09", "42")})
        self.assertEqual(mux.routing, {"drain": ("09", "42")})


class TestPark(unittest.TestCase):
    def test_park_grounds_everything(self) -> None:
        mux, fake = make_mux()
        mux.select({"source": "20", "drain": "42"})
        mux.park()
        self.assertEqual(
            fake.closed, {(line, 0) for line in LINES.values()}
        )
        self.assertEqual(mux.routing, {})


class TestMcFragment(unittest.TestCase):
    def test_house_convention_keys(self) -> None:
        mux, _ = make_mux()
        mux.select(
            {"source": "20", "drain": "42", "sr1+": "09", "sr1-": "01"}
        )
        frag = mux.mc_fragment()
        self.assertEqual(frag["sr1"], "09-01")
        self.assertEqual(frag["sr0"], "drain current on 42")
        self.assertEqual(frag["qswitch_source"], "source current on 20")

    def test_multi_contact_drain_label(self) -> None:
        mux, _ = make_mux()
        mux.select({"drain": ("09", "42")})
        self.assertEqual(mux.mc_fragment()["sr0"], "drain current on 09&42")

    def test_routing_and_state_always_present(self) -> None:
        mux, fake = make_mux()
        mux.select({"sr2+": "12"})  # no '-' partner: no sr2 pair key
        frag = mux.mc_fragment()
        self.assertEqual(frag["qswitch_routing"], {"sr2+": "12"})
        self.assertNotIn("sr2", frag)
        self.assertEqual(frag["qswitch_state"], fake.state())

    def test_fragment_is_json_serializable(self) -> None:
        import json

        mux, _ = make_mux()
        mux.select({"source": "20", "drain": "42", "sr1+": "09", "sr1-": "01"})
        json.dumps(mux.mc_fragment())


class TestSettleAccessor(unittest.TestCase):
    def test_settle_s_default(self) -> None:
        self.assertEqual(ContactMux(FakeQSwitch(), LINES, BREAKOUTS).settle_s, 10.0)

    def test_settle_s_reflects_override(self) -> None:
        mux, _ = make_mux()  # constructed with settle_s=0
        self.assertEqual(mux.settle_s, 0)


if __name__ == "__main__":
    unittest.main()
