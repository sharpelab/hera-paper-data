"""Leiden Cryogenics QCS v1 heater current source (via MCC USB-3101 DAQ).

The QCS v1 is analog-programmed — there is no command protocol and **no
on/off DIO bit**. Per channel: an analog out carries the setpoint
(``V = I[µA] × 1e-6 × R[range]``; OFF = 0 V on the DAC), and two AUXPORT
DIO bits (bits [2c+1:2c]) carry the range code, all four codes written as
one port byte. Status readback flips a channel's *inactive* range bit to
input and reads it. Map extracted from the vendor VI block diagrams —
full derivation and open unknowns in docs/manuals/leiden_qcs/README.md.

Safety invariants enforced here (not in the GUI):
  - unknown channels (incl. 0 = N.C.) are rejected;
  - set_current clamps to the per-channel config max and the top range max;
  - every output write recomputes the FULL port byte and volts from this
    driver's commanded state and re-asserts port direction — no partial
    updates, so a failed write can never leave a stale range scaling a
    later value write (10–100× overcurrent class; regression-tested);
  - the port byte is seeded from the hardware latch at configure_io(), so
    a fresh start cannot silently re-range channels somebody left driven;
  - nothing here writes any output until the first explicit set_current /
    set_on call (never-auto-zero: restarts must not move heaters).

``QCS_V1_MAP`` is filled from the extraction but ``validated=False`` until
the deploy-window checks pass (AO scaling, status-bit polarity, rig-copy
diff) — the worker runs but warns loudly, and the CLI is the bring-up tool:
    python -m drivers.leiden_qcs --status
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass

from core.config import load_config

try:  # Windows-only optional dep; guarded per repo convention
    from mcculw import ul as _mcc_ul
    from mcculw.enums import DigitalIODirection, DigitalPortType, ULRange
except ImportError:
    _mcc_ul = None


class QcsError(Exception):
    """Configuration, mapping, or IO failure in the QCS driver."""


# --- Wiring map -----------------------------------------------------------


@dataclass(frozen=True)
class RangeSpec:
    """One QCS output range."""

    name: str  # "x10" / "x100"
    code: int  # 2-bit range code on the channel's DIO pair
    r_ohm: float  # conversion resistor: volts = uA * 1e-6 * r_ohm
    max_ua: float  # ceiling for range selection (first with max >= |I|)


@dataclass(frozen=True)
class QcsMap:
    """Wiring of a QCS unit to its MCC DAQ (see the manual reference doc)."""

    channels: dict[int, str]  # heater/aout channel -> name; ch 0 (N.C.) omitted
    ranges: tuple[RangeSpec, ...]  # ascending by max_ua; live build has no x1
    ao_range: str  # mcculw ULRange name for v_out
    status_true_means_on: bool = True  # polarity UNKNOWN until bring-up
    validated: bool = False  # flipped after deploy-window checks pass


# Extracted 2026-07-25 from the public Leiden-TC VI block diagrams
# (docs/manuals/leiden_qcs/README.md). validated=False until bring-up:
# AO volts-vs-counts, status polarity, and a rig-copy diff are unverified.
QCS_V1_MAP = QcsMap(
    channels={1: "3K", 2: "Still", 3: "MC"},  # 0 = N.C., rejected
    ranges=(
        RangeSpec("x10", code=0b01, r_ohm=2_000.0, max_ua=5_000.0),  # tops at 10 V
        RangeSpec("x100", code=0b10, r_ohm=100.0, max_ua=50_000.0),  # compliance 5 V
    ),
    ao_range="UNI10VOLTS",
)


def _range_shift(channel: int) -> int:
    """AUXPORT bit position of *channel*'s 2-bit range code."""
    return 2 * channel


# --- IO seam --------------------------------------------------------------


class McculwIO:
    """Production IO: MCC Universal Library via mcculw (Windows-only)."""

    def __init__(self, board_num: int, ao_range: str) -> None:
        if _mcc_ul is None:  # pragma: no cover - Windows-only dep
            raise QcsError("mcculw not available (Windows-only dependency)")
        self._ul = _mcc_ul
        self._board = board_num
        self._port = DigitalPortType.AUXPORT
        self._ao_range = getattr(ULRange, ao_range)

    def board_name(self) -> str:
        return self._ul.get_board_name(self._board)

    def a_out_volts(self, channel: int, volts: float) -> None:
        self._ul.v_out(self._board, channel, self._ao_range, volts)

    def config_port_out(self) -> None:
        self._ul.d_config_port(self._board, self._port, DigitalIODirection.OUT)

    def config_bit_in(self, bit: int) -> None:
        self._ul.d_config_bit(self._board, self._port, bit, DigitalIODirection.IN)

    def d_out_port(self, byte: int) -> None:
        self._ul.d_out(self._board, self._port, byte)

    def d_in_port(self) -> int:
        return self._ul.d_in(self._board, self._port)

    def d_bit_in(self, bit: int) -> bool:
        return bool(self._ul.d_bit_in(self._board, self._port, bit))


# --- Driver ---------------------------------------------------------------


@dataclass
class ChannelState:
    """Last-commanded + last-readback state of one heater channel."""

    name: str
    set_ua: float | None  # commanded setpoint; None until first command
    range_name: str | None  # "x10"/"x100" for the commanded setpoint
    on: bool | None  # status readback; None = unknown (no code on pins)
    commanded_on: bool  # what we last told the DAC (False until commanded)


class LeidenQcs:
    """QCS driver: clamped setpoints, analog on/off, full-port writes.

    io       — an object with the McculwIO surface (fake in tests)
    qcs_map  — instrument wiring (synthetic in tests)
    max_ua   — per-channel-name clamp from config; missing names fall back
               to DEFAULT_MAX_UA
    """

    DEFAULT_MAX_UA = 15000.0  # the TC config's only limit hint

    def __init__(self, io, qcs_map: QcsMap, max_ua: dict[str, float] | None = None):
        if not qcs_map.channels:
            raise QcsError("QCS map has no channels")
        if 0 in qcs_map.channels:
            raise QcsError("channel 0 is N.C. and must not be in the map")
        self._io = io
        self._map = qcs_map
        self._max_ua = dict(max_ua or {})
        self._state: dict[int, ChannelState] = {
            ch: ChannelState(name=name, set_ua=None, range_name=None,
                             on=None, commanded_on=False)
            for ch, name in qcs_map.channels.items()
        }
        # Per-channel 2-bit range codes composing the AUXPORT byte. Seeded
        # from the hardware latch in configure_io(); codes for channels we
        # haven't commanded are preserved on every write.
        self._range_codes: dict[int, int] = {}

    # -- helpers --

    def _require(self, channel: int) -> ChannelState:
        state = self._state.get(channel)
        if state is None:
            raise QcsError(
                f"channel {channel} not driveable (valid: {sorted(self._state)})"
            )
        return state

    def resolve(self, channel: int | str) -> int:
        """Accept a channel number or name ("MC"); return the number."""
        if isinstance(channel, str):
            for ch, name in self._map.channels.items():
                if name == channel:
                    return ch
            raise QcsError(f"unknown channel name {channel!r}")
        if isinstance(channel, bool):  # JSON true would alias channel 1
            raise QcsError(f"invalid channel {channel!r}")
        self._require(channel)
        return channel

    def clamp(self, channel: int, ua: float) -> float:
        """The current that set_current(channel, ua) would actually program."""
        state = self._require(channel)
        if not math.isfinite(ua):
            # NaN slides through min/max and would poison the stored
            # setpoint — which must never happen: even turning a channel
            # OFF goes through the setpoint math.
            raise QcsError(f"{state.name}: non-finite current {ua!r}")
        limit = min(
            self._max_ua.get(state.name, self.DEFAULT_MAX_UA),
            self._map.ranges[-1].max_ua,
        )
        return min(max(ua, 0.0), limit)

    def _pick_range(self, ua: float) -> RangeSpec:
        for spec in self._map.ranges:
            if ua <= spec.max_ua:
                return spec
        raise QcsError(f"{ua} µA exceeds top range")  # unreachable post-clamp

    def _port_byte(self, override_ch: int, override_code: int) -> int:
        # Unmapped pairs (incl. ch 0 = N.C.) compose as 00; any physically
        # connected channel must be in the map or its range gets zeroed.
        byte = (override_code & 0b11) << _range_shift(override_ch)
        for ch, code in self._range_codes.items():
            if ch != override_ch:
                byte |= (code & 0b11) << _range_shift(ch)
        return byte

    def _write_channel(self, channel: int) -> None:
        """Re-assert direction, full range byte, and this channel's volts —
        always the whole sequence, from commanded state only.

        The range-code cache is committed only AFTER d_out_port succeeds:
        the cache seeds every later port byte for ALL channels, so caching
        an unwritten code would let a failed write here silently re-range
        this channel the next time any other channel is commanded — with
        this channel's DAC still driving old-range volts (10–100×)."""
        state = self._state[channel]
        spec = self._pick_range(state.set_ua or 0.0)
        volts = 0.0
        if state.commanded_on and state.set_ua:
            volts = state.set_ua * 1e-6 * spec.r_ohm
        self._io.a_out_volts(channel, 0.0)
        self._io.config_port_out()
        self._io.d_out_port(self._port_byte(channel, spec.code))
        self._range_codes[channel] = spec.code
        state.range_name = spec.name
        self._io.a_out_volts(channel, volts)

    # -- init --

    def configure_io(self) -> None:
        """Seed the range-code cache from the hardware latch; write nothing.

        Reading the AUXPORT latch preserves range codes on channels someone
        left driven (a fresh start composing the port byte from an empty
        cache would silently re-range them). NOTE: after a DAQ power cycle
        the latch reads reset — pin behavior at that point is a deploy-
        checklist validation item, not an assumption.
        """
        latch = self._io.d_in_port()
        for ch in self._map.channels:
            self._range_codes[ch] = (latch >> _range_shift(ch)) & 0b11

    # -- operations --

    def set_current(self, channel: int, ua: float) -> ChannelState:
        """Program *channel*'s setpoint, clamped. If the channel is
        commanded on, the new value goes to the DAC now; if off, the DAC
        stays at 0 V and the setpoint takes effect on set_on(True)."""
        state = self._require(channel)
        state.set_ua = self.clamp(channel, ua)
        self._write_channel(channel)
        return self.read_channel(channel)

    def set_on(self, channel: int, on: bool) -> ChannelState:
        """Drive *channel* on (setpoint volts) or off (0 V). There is no
        enable bit — this IS the DAC write."""
        state = self._require(channel)
        if on and state.set_ua is None:
            raise QcsError(
                f"{state.name}: no setpoint — set a current before turning on"
            )
        state.commanded_on = on
        self._write_channel(channel)
        return self.read_channel(channel)

    def read_channel(self, channel: int) -> ChannelState:
        """Refresh one channel's status readback and return its state.

        Reads the channel's *inactive* range bit as an input, then restores
        port direction. Channels with no range code on the pins read as
        unknown (on=None) — the vendor's low-range fallback injects a test
        current and is deliberately not implemented ("heats up the
        cryostat")."""
        state = self._require(channel)
        code = self._range_codes.get(channel, 0)
        if code not in (0b01, 0b10):  # no/garbage code: readback undefined
            state.on = None
            return state
        inactive = _range_shift(channel) + (1 if code == 0b01 else 0)
        self._io.config_bit_in(inactive)
        try:
            raw = self._io.d_bit_in(inactive)
        finally:
            self._io.config_port_out()  # never leave the pin floating
        state.on = raw == self._map.status_true_means_on
        return state

    def status(self) -> dict[int, ChannelState]:
        """Refresh readback on every channel."""
        return {ch: self.read_channel(ch) for ch in self._state}

    def cached_status(self) -> dict[int, ChannelState]:
        """Commanded/cached state with no hardware IO (readback may be
        stale) — for reporting when the DAQ is unreachable."""
        return dict(self._state)


# --- CLI probe mode -------------------------------------------------------


def _cli() -> int:
    parser = argparse.ArgumentParser(
        description="Leiden QCS probe CLI (bring-up tool; see plan doc)"
    )
    parser.add_argument("--board", type=int, default=None,
                        help="MCC board number (default: from toploader.toml)")
    parser.add_argument("--id", action="store_true", help="print DAQ board name")
    parser.add_argument("--status", action="store_true", help="read all channels")
    parser.add_argument("--set", metavar="CH=UA", help="set channel current (µA)")
    parser.add_argument("--on", type=int, metavar="CH", help="enable channel output")
    parser.add_argument("--off", type=int, metavar="CH", help="disable channel output")
    args = parser.parse_args()

    config = load_config()
    board = args.board if args.board is not None else config.hardware.qcs_board_num
    if board < 0:
        print("no board: pass --board or set hardware.qcs_board_num in toploader.toml")
        return 2
    if not QCS_V1_MAP.validated:
        print("NOTE: QCS_V1_MAP is unvalidated — bring-up checks pending "
              "(docs/plans/QCS_HEATER_CONTROL.md)")

    io = McculwIO(board, QCS_V1_MAP.ao_range)
    if args.id:
        print(f"board {board}: {io.board_name()}")
    qcs = LeidenQcs(io, QCS_V1_MAP,
                    {k: float(v) for k, v in config.hardware.qcs_max_ua.items()})
    qcs.configure_io()

    try:
        if args.set:
            ch_str, _, ua_str = args.set.partition("=")
            state = qcs.set_current(int(ch_str), float(ua_str))
            print(f"ch{ch_str} ({state.name}): set {state.set_ua} µA ({state.range_name})")
        if args.on is not None:
            qcs.set_on(args.on, True)
        if args.off is not None:
            qcs.set_on(args.off, False)
    except QcsError as e:
        print(f"error: {e}")
        return 1

    if args.status or not (args.id or args.set or args.on is not None or args.off is not None):
        for ch, s in qcs.status().items():
            on = "?" if s.on is None else s.on
            print(f"ch{ch} {s.name}: on={on} commanded_on={s.commanded_on} "
                  f"set={s.set_ua} µA range={s.range_name}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
