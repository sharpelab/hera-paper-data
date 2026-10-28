"""QSwitch-backed contact-pair switching with truthful metadata.

Wraps a connected ``drivers.QSwitch.QSwitch`` with the lab's wiring
model: device contacts arrive on QSwitch *lines* (1-24), instrument
cables sit on the breakout-BNC *taps* (1-8). A ``ContactMux`` holds the
two maps (device-card content), switches between named contact
configurations with a ground-during-transition sequence, and emits the
``measurement_config`` fragment that keeps the per-run contact truth in
``metadata.json`` — the invariant that manual re-wiring used to carry in
hand-edited config dicts.

Port-naming convention consumed by :meth:`ContactMux.mc_fragment`:
``source`` and ``drain`` ports label the current path; ``srN+``/``srN-``
port pairs are lock-in differential inputs and render as the corpus'
``"srN": "<plus>-<minus>"`` pair strings. Ports outside the convention
still land in ``qswitch_routing`` — nothing is dropped, the convention
only adds the familiar keys.

Switching disturbs the lock-ins: after the relays settle, the readouts
need several time constants to recover. ``settle_s`` defaults to 10 s
(the value used in the QSwitch's prior live use on the VTI); calibrate
it per setup with the buffer-trace procedure in
``hera/docs/vti/qswitch-smoke-test.md``.
"""

from collections.abc import Mapping, Sequence
from time import sleep

GROUND_TAP = 0
CONNECT_TAP = 9
_BREAKOUT_TAPS = range(1, 9)
_LINES = range(1, 25)

State = list[tuple[int, int]]


def _as_contacts(value: str | Sequence[str]) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    return tuple(value)


def target_state(
    lines: Mapping[str, int],
    breakouts: Mapping[str, int],
    routing: Mapping[str, str | Sequence[str]],
) -> State:
    """Relay closures realizing ``routing`` — pure, for tests and review.

    Args:
        lines: contact name -> QSwitch line (1-24).
        breakouts: port name -> breakout tap (1-8).
        routing: port name -> contact name(s) to connect to that port.

    Returns:
        Sorted ``(line, tap)`` closures, grounds excluded.
    """
    seen: dict[str, str] = {}
    state: State = []
    for port, value in routing.items():
        if port not in breakouts:
            raise ValueError(f'Unknown port "{port}" (breakouts: {sorted(breakouts)})')
        for contact in _as_contacts(value):
            if contact not in lines:
                raise ValueError(
                    f'Unknown contact "{contact}" (lines: {sorted(lines)})'
                )
            if contact in seen:
                raise ValueError(
                    f'Contact "{contact}" routed to both "{seen[contact]}" and '
                    f'"{port}" — one contact, one port'
                )
            seen[contact] = port
            state.append((lines[contact], breakouts[port]))
    return sorted(state)


class ContactMux:
    """Named-contact switching over a QSwitch, metadata kept truthful.

    Args:
        qswitch: connected ``drivers.QSwitch.QSwitch`` (only
            ``close_relays`` / ``open_relays`` / ``state`` are used).
        lines: contact name -> QSwitch line (1-24). Contacts not in this
            map are invisible to the mux — wire them past the QSwitch or
            extend the map.
        breakouts: port name -> breakout tap (1-8). Tap 0 (ground) and
            tap 9 (through-connect) are managed by the mux and may not
            be assigned.
        settle_s: post-switch settle (relay actuation + lock-in
            recovery), used when ``select``/``park`` aren't given one.
    """

    def __init__(
        self,
        qswitch,
        lines: Mapping[str, int],
        breakouts: Mapping[str, int],
        settle_s: float = 10.0,
    ) -> None:
        for name, line in lines.items():
            if line not in _LINES:
                raise ValueError(f'Line {line} for contact "{name}" outside 1-24')
        for name, tap in breakouts.items():
            if tap not in _BREAKOUT_TAPS:
                raise ValueError(f'Tap {tap} for port "{name}" outside 1-8')
        if len(set(lines.values())) != len(lines):
            raise ValueError("Duplicate line numbers in lines map")
        if len(set(breakouts.values())) != len(breakouts):
            raise ValueError("Duplicate tap numbers in breakouts map")
        self._qswitch = qswitch
        self._lines = dict(lines)
        self._breakouts = dict(breakouts)
        self._settle_s = settle_s
        self._routing: dict[str, tuple[str, ...]] = {}

    # -- switching ----------------------------------------------------

    def select(
        self,
        routing: Mapping[str, str | Sequence[str]],
        settle_s: float | None = None,
    ) -> None:
        """Switch to ``routing`` (port -> contact(s)).

        Sequence, make-before-break against ground so no managed contact
        ever floats unterminated mid-transition:

        1. ground every managed line and open all its taps;
        2. close the target (line, tap) relays — lines briefly see
           instrument and ground together;
        3. open every managed line's ground — routed lines go live,
           unused lines float (the campaigns' "float other contacts"
           convention: grounding unused contacts would tie them into a
           shared node through the device);
        4. settle.

        Step 1 grounds every managed line: if a gate or DC-bias source
        is wired through the mux, ramp it to zero before switching.
        """
        state = target_state(self._lines, self._breakouts, routing)
        managed = sorted(self._lines.values())
        self._qswitch.close_relays([(line, GROUND_TAP) for line in managed])
        self._qswitch.open_relays(
            [
                (line, tap)
                for line in managed
                for tap in (*_BREAKOUT_TAPS, CONNECT_TAP)
            ]
        )
        if state:
            self._qswitch.close_relays(state)
        self._qswitch.open_relays([(line, GROUND_TAP) for line in managed])
        self._routing = {
            port: _as_contacts(value) for port, value in routing.items()
        }
        sleep(self._settle_s if settle_s is None else settle_s)

    def park(self, settle_s: float | None = None) -> None:
        """Ground every managed line (idle/safe state), clear routing."""
        managed = sorted(self._lines.values())
        self._qswitch.close_relays([(line, GROUND_TAP) for line in managed])
        self._qswitch.open_relays(
            [
                (line, tap)
                for line in managed
                for tap in (*_BREAKOUT_TAPS, CONNECT_TAP)
            ]
        )
        self._routing = {}
        sleep(self._settle_s if settle_s is None else settle_s)

    # -- metadata -----------------------------------------------------

    def mc_fragment(self) -> dict:
        """``measurement_config`` entries recording the live contact truth.

        Always: ``qswitch_routing`` (port -> contact string) and
        ``qswitch_state`` (the instrument's own compressed relay list,
        read back from hardware — intent and actuality both on record).
        When ports follow the house convention, additionally the corpus'
        familiar keys: ``"srN": "<plus>-<minus>"`` from ``srN+``/``srN-``
        pairs and ``"sr0": "drain current on <contacts>"`` from
        ``drain``.
        """
        frag: dict = {
            "qswitch_routing": {
                port: "&".join(contacts)
                for port, contacts in self._routing.items()
            },
            "qswitch_state": self._qswitch.state(),
        }
        plus = {
            port[:-1]: contacts
            for port, contacts in self._routing.items()
            if port.endswith("+")
        }
        minus = {
            port[:-1]: contacts
            for port, contacts in self._routing.items()
            if port.endswith("-")
        }
        for name in sorted(set(plus) & set(minus)):
            frag[name] = f'{"&".join(plus[name])}-{"&".join(minus[name])}'
        if "drain" in self._routing:
            frag["sr0"] = (
                f'drain current on {"&".join(self._routing["drain"])}'
            )
        if "source" in self._routing:
            frag["qswitch_source"] = (
                f'source current on {"&".join(self._routing["source"])}'
            )
        return frag

    @property
    def settle_s(self) -> float:
        """Default post-switch settle (s), used when select/park aren't given one."""
        return self._settle_s

    @property
    def routing(self) -> dict[str, tuple[str, ...]]:
        """Last selected routing (port -> contact names)."""
        return dict(self._routing)
