"""The three VTI monitor workers: Source wiring and publish payloads.

Each worker owns one instrument and hands the loop to core.poller, so the only
worker-specific code is the Source (connect/close/read) and publish. These
tests pin publish's exact [data] dict and its InfluxDB points — Grafana and the
launcher panel both read those verbatim — plus the two behaviours the driver
does not cover: close() clearing the qcodes registry, and publish swallowing an
InfluxDB write failure into an [error] line.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from workers import vti_he_level, vti_l218, vti_pressure

_HW = SimpleNamespace(
    ami1700_addr="TCPIP0::fake::7180::SOCKET",
    terranova_addr="ASRL8::INSTR",
    lakeshore218_gpib="GPIB0::15::INSTR",
)
_INFLUX = ("client", "write_api", "dgg", "vti")

MODULES = (vti_he_level, vti_pressure, vti_l218)


class FakeInstrumentRegistry:
    """Stand-in for qcodes' Instrument; records close_all() calls."""

    closed = 0

    @classmethod
    def close_all(cls):
        cls.closed += 1


@pytest.fixture
def writes(monkeypatch):
    """Collect (measurement, metric, value, unit) from every write_point."""
    recorded: list[tuple] = []

    def fake_write_point(write_api, org, bucket, measurement, metric, value, unit):
        assert (write_api, org, bucket) == _INFLUX[1:]
        recorded.append((measurement, metric, value, unit))

    for module in MODULES:
        monkeypatch.setattr(module, "write_point", fake_write_point)
    return recorded


@pytest.fixture
def make_publish(monkeypatch):
    """Run a worker's main() with the driver stubbed out; hand back publish."""

    def build(module):
        captured = {}

        def fake_run(source, *, interval, publish):
            captured.update(source=source, interval=interval, publish=publish)

        monkeypatch.setattr(module, "run", fake_run)
        monkeypatch.setattr(module, "load_vti_config",
                            lambda: SimpleNamespace(hardware=_HW, influxdb=None))
        monkeypatch.setattr(module, "setup_influx", lambda cfg: _INFLUX)
        module.main([])
        assert captured["interval"] == module.READ_INTERVAL
        return captured["publish"]

    return build


def _source_closes_the_registry(monkeypatch, module, source):
    monkeypatch.setattr(module, "Instrument", FakeInstrumentRegistry)
    before = FakeInstrumentRegistry.closed
    source.inst = object()
    source.close()
    assert FakeInstrumentRegistry.closed == before + 1
    assert source.inst is None


# --- He level (AMI 1700) --------------------------------------------------


def test_he_level_source_reads_and_closes(monkeypatch):
    source = vti_he_level.Ami1700Source(_HW.ami1700_addr)
    source.inst = SimpleNamespace(He_level=lambda: 18.25)
    assert source.read() == pytest.approx(18.25)
    _source_closes_the_registry(monkeypatch, vti_he_level, source)


def test_he_level_publish(make_publish, writes):
    publish = make_publish(vti_he_level)
    assert publish(18.246, 0) == {"He level": "18.25 in", "_summary": "He 18.2 in"}
    assert writes == [("vti", "He level", 18.246, "in")]


# --- Probe space pressure (Terranova 906A) --------------------------------


def test_pressure_source_reads_and_closes(monkeypatch):
    source = vti_pressure.Terranova906ASource(_HW.terranova_addr)
    source.inst = SimpleNamespace(pressure=lambda: 1.2e-4)
    assert source.read() == pytest.approx(1.2e-4)
    _source_closes_the_registry(monkeypatch, vti_pressure, source)


def test_pressure_publish(make_publish, writes):
    publish = make_publish(vti_pressure)
    assert publish(1.234e-4, 0) == {
        "probe space pressure": "1.23e-04 Torr",
        "_summary": "1.23e-04 Torr",
    }
    assert writes == [("vti", "probe space pressure", 1.234e-4, "Torr")]


# --- Lakeshore 218 --------------------------------------------------------


def test_l218_source_reads_both_channels_and_closes(monkeypatch):
    source = vti_l218.Lakeshore218Source(_HW.lakeshore218_gpib)
    source.inst = SimpleNamespace(magnet_temperature=lambda: 3.9,
                                  gm_temperature=lambda: 40.0)
    assert source.read() == (pytest.approx(3.9), pytest.approx(40.0))
    _source_closes_the_registry(monkeypatch, vti_l218, source)


def test_l218_publish_writes_both_metrics(make_publish, writes):
    publish = make_publish(vti_l218)
    assert publish((3.9127, 40.0512), 0) == {
        "magnet temperature": "3.913 K",
        "gm temperature": "40.051 K",
        "_summary": "magnet 3.913 K",
    }
    assert writes == [
        ("vti", "magnet temperature", 3.9127, "K"),
        ("vti", "gm temperature", 40.0512, "K"),
    ]


# --- InfluxDB failures are non-fatal --------------------------------------


@pytest.mark.parametrize("module, reading, metric", [
    (vti_he_level, 18.0, "He level"),
    (vti_pressure, 1.2e-4, "probe space pressure"),
    (vti_l218, (3.9, 40.0), "magnet temperature"),
])
def test_write_failure_is_logged_not_raised(monkeypatch, capsys, make_publish,
                                            module, reading, metric):
    publish = make_publish(module)

    def boom(*_a, **_k):
        raise RuntimeError("401 Unauthorized")

    monkeypatch.setattr(module, "write_point", boom)
    data = publish(reading, 0)

    assert metric in data
    errors = [line for line in capsys.readouterr().out.splitlines()
              if line.startswith("[error]")]
    assert f"[error] InfluxDB write failed ({metric}): 401 Unauthorized" in errors


def test_data_payload_is_json_serializable(make_publish, writes):
    publish = make_publish(vti_l218)
    assert json.loads(json.dumps(publish((3.9, 40.0), 0)))["_summary"] == "magnet 3.900 K"
