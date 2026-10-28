"""The VTI aux worker connects all-or-nothing (fail-hard).

A single instrument that fails to connect must not be silently dropped — that
once let a busy pressure-gauge port go unnoticed in Grafana. _connect_instruments
attempts every bus (so all failures are logged) but raises InstrumentConnectError
if any is down; main() turns that into a non-zero exit the launcher shows red.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from workers import vti_aux
from workers.vti_aux import InstrumentConnectError, _connect_instruments

_HW = SimpleNamespace(
    ami1700_addr="TCPIP0::fake::7180::SOCKET",
    terranova_addr="ASRL8::INSTR",
    lakeshore218_gpib="GPIB0::15::INSTR",
)


class _FakeAMI:
    def __init__(self, *_a, **_k):
        pass

    def He_level(self):
        return 18.0


class _FakeL218:
    def __init__(self, *_a, **_k):
        pass

    def magnet_temperature(self):
        return 3.9

    def gm_temperature(self):
        return 40.0


class _FakeTerranova:
    def __init__(self, *_a, **_k):
        pass

    def pressure(self):
        return 1.2e-4


def _patch(monkeypatch, *, ami=_FakeAMI, terranova=_FakeTerranova, l218=_FakeL218):
    monkeypatch.setattr(vti_aux, "AMI_1700", ami)
    monkeypatch.setattr(vti_aux, "Terranova_906A", terranova)
    monkeypatch.setattr(vti_aux, "Lakeshore_218", l218)


def _boom(*_a, **_k):
    raise RuntimeError("VI_ERROR_RSRC_BUSY")


def test_all_instruments_up_returns_full_reading_set(monkeypatch):
    _patch(monkeypatch)
    readings = _connect_instruments(_HW)
    metrics = [m for m, _u, _fn in readings]
    assert metrics == [
        "He level",
        "probe space pressure",
        "magnet temperature",
        "gm temperature",
    ]


def test_one_instrument_down_fails_hard(monkeypatch):
    # Terranova busy (the real-world case) — must not run degraded.
    _patch(monkeypatch, terranova=_boom)
    with pytest.raises(InstrumentConnectError) as excinfo:
        _connect_instruments(_HW)
    assert "Terranova 906A" in str(excinfo.value)


def test_failure_message_names_every_down_instrument(monkeypatch):
    _patch(monkeypatch, terranova=_boom, ami=_boom)
    with pytest.raises(InstrumentConnectError) as excinfo:
        _connect_instruments(_HW)
    msg = str(excinfo.value)
    assert "AMI 1700" in msg
    assert "Terranova 906A" in msg
