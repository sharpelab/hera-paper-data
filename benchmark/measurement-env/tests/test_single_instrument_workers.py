"""The three single-instrument workers: Source + publish, minus the driver.

core.poller owns the loop and the protocol (tests/test_poller.py pins those),
so what is left per worker is the pair the driver calls: a Source that talks to
one instrument and a publish that fans the reading out to InfluxDB and returns
the [data] payload. These tests pin what read() yields, that close() actually
tears the session down, and the exact metric/value/unit and payload published.
"""

from __future__ import annotations

import math

import pytest

from workers import magnet, thorlabs_thermo, vti_magnet


def record_writes(monkeypatch, module) -> list[tuple]:
    """Capture (measurement, metric, value, unit) for each write_point call."""
    writes: list[tuple] = []
    monkeypatch.setattr(
        module, "write_point",
        lambda api, org, bucket, measurement, metric, value, unit: writes.append(
            (measurement, metric, value, unit)),
    )
    return writes


# --- magnet (AMI 430) -----------------------------------------------------


class FakeAMI430:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.queries: list[str] = []

    def field(self):
        self.queries.append("field")
        return 1.23456

    def ramping_state(self):
        self.queries.append("state")
        return "holding"

    def is_quenched(self):
        self.queries.append("quench")
        return False


def test_magnet_reads_the_field_only_by_default(monkeypatch):
    monkeypatch.setattr(magnet, "AMIModel430", FakeAMI430)
    source = magnet.Magnet("TCPIP0::10.0.0.5::7180::SOCKET")
    source.connect()

    reading = source.read()

    assert reading.field_T == pytest.approx(1.23456)
    assert reading.state is None and reading.quenched is None
    assert source._mag.queries == ["field"]  # no extra traffic on the shared link


def test_magnet_reads_control_state_when_asked(monkeypatch):
    monkeypatch.setattr(magnet, "AMIModel430", FakeAMI430)
    source = magnet.Magnet("TCPIP0::10.0.0.5::7180::SOCKET", with_state=True)
    source.connect()

    assert source.read() == magnet.Reading(pytest.approx(1.23456), "holding", False)


def test_rig_table_pins_who_gets_state():
    assert magnet.RIGS["toploader"].with_state is False  # cost uncharacterized
    assert magnet.RIGS["pink"].with_state is True


def test_magnet_close_clears_the_qcodes_registry(monkeypatch):
    closed: list[str] = []
    monkeypatch.setattr(magnet, "AMIModel430", FakeAMI430)
    monkeypatch.setattr(magnet.Instrument, "close_all",
                        staticmethod(lambda: closed.append("close_all")))
    source = magnet.Magnet("TCPIP0::10.0.0.5::7180::SOCKET")
    source.connect()

    source.close()

    assert closed == ["close_all"]


@pytest.mark.parametrize("rig, measurement", [("toploader", "AVS_bridge"),
                                              ("pink", "AMI430")])
def test_magnet_publishes_field_in_tesla(monkeypatch, rig, measurement):
    writes = record_writes(monkeypatch, magnet)
    assert magnet.RIGS[rig][1] == measurement

    publish = magnet.make_publish(None, "dgg", "bucket", measurement)
    data = publish(magnet.Reading(1.23456), 0)

    assert data == {"_summary": "1.2346 T", "magnetic field": "1.2346 T"}
    assert writes == [(measurement, "magnetic field", 1.23456, "Tesla")]


@pytest.mark.parametrize("state, quenched, code, summary", [
    ("holding", False, 2, "1.2346 T holding"),
    ("ramping", False, 1, "1.2346 T ramping"),
    ("quench detected", True, 7, "1.2346 T QUENCH"),
    ("something new", False, -1, "1.2346 T something new"),
])
def test_magnet_publishes_control_state_as_codes(monkeypatch, state, quenched,
                                                 code, summary):
    writes = record_writes(monkeypatch, magnet)

    data = magnet.make_publish(None, "dgg", "bucket", "AMI430")(
        magnet.Reading(1.23456, state, quenched), 0)

    assert writes == [
        ("AMI430", "magnetic field", 1.23456, "Tesla"),
        ("AMI430", "ramping state", float(code), "state"),
        ("AMI430", "quenched", 1.0 if quenched else 0.0, "status"),
    ]
    assert data["_summary"] == summary
    assert data["ramping state"] == f"{state} ({code})"
    assert data["quenched"] == ("YES" if quenched else "no")


def test_magnet_publish_survives_an_influx_write_failure(monkeypatch, capsys):
    def boom(*args, **kwargs):
        raise RuntimeError("401 Unauthorized")

    monkeypatch.setattr(magnet, "write_point", boom)

    data = magnet.make_publish(None, "dgg", "bucket", "AVS_bridge")(magnet.Reading(0.5), 3)

    assert data["magnetic field"] == "0.5000 T"
    assert capsys.readouterr().out.strip() == (
        "[error] InfluxDB write failed: 401 Unauthorized")


# --- thorlabs_thermo (TSP01B) ---------------------------------------------


class FakeResource:
    def __init__(self):
        self.closed = False

    def query(self, command):
        return {"SENS1:TEMP:DATA?": " 23.42\n", "SENS2:HUM:DATA?": "42.13"}[command]

    def close(self):
        self.closed = True


class FakeResourceManager:
    def __init__(self, resources):
        self._resources = resources
        self.resource = FakeResource()
        self.opened = None

    def list_resources(self):
        return self._resources

    def open_resource(self, name):
        self.opened = name
        return self.resource


def fake_visa(monkeypatch, resources):
    rm = FakeResourceManager(resources)
    monkeypatch.setattr(thorlabs_thermo.pyvisa, "ResourceManager", lambda: rm)
    return rm


def test_thorlabs_reads_temperature_and_humidity(monkeypatch):
    rm = fake_visa(monkeypatch, ("ASRL1::INSTR", "USB0::0x1313::0x8099::INSTR"))
    source = thorlabs_thermo.Thermometer()
    source.connect()

    assert rm.opened == "USB0::0x1313::0x8099::INSTR"
    assert source.read() == (pytest.approx(23.42), pytest.approx(42.13))


def test_thorlabs_connect_raises_when_no_usb_device_is_present(monkeypatch):
    fake_visa(monkeypatch, ("ASRL1::INSTR",))

    with pytest.raises(RuntimeError, match="No USB device found"):
        thorlabs_thermo.Thermometer().connect()


def test_thorlabs_close_closes_the_visa_resource(monkeypatch):
    rm = fake_visa(monkeypatch, ("USB0::0x1313::0x8099::INSTR",))
    source = thorlabs_thermo.Thermometer()
    source.connect()

    source.close()

    assert rm.resource.closed


def test_thorlabs_publishes_both_metrics_and_announces_the_first_reading(
        monkeypatch, capsys):
    writes = record_writes(monkeypatch, thorlabs_thermo)
    publish = thorlabs_thermo.make_publish(None, "dgg", "bucket")

    first = publish((23.42, 42.13), 0)
    later = publish((22.0, 40.0), 1)

    assert first == {"_summary": "23.4C — Wow so warm!", "temp": "23.4 C",
                     "humidity": "42.1%"}
    assert later == {"_summary": "22.0C — Oh so chilly!", "temp": "22.0 C",
                     "humidity": "40.0%"}
    assert writes == [
        ("thorlabs_thermo", "temp", 23.42, "C"),
        ("thorlabs_thermo", "humidity", 42.13, "%"),
        ("thorlabs_thermo", "temp", 22.0, "C"),
        ("thorlabs_thermo", "humidity", 40.0, "%"),
    ]
    # The first-reading line belongs to cycle 0 only.
    assert capsys.readouterr().out == "[init] First reading: 23.42 C, 42.13%\n"


# --- vti_magnet (FastBi1K5) -----------------------------------------------


class FakeFastBi1K5:
    def __init__(self, name, host):
        self.name = name
        self.host = host
        self.closed = False

    def field(self):
        return 0.98765

    def close(self):
        self.closed = True


def test_vti_magnet_reads_the_field_as_a_float(monkeypatch):
    monkeypatch.setattr(vti_magnet, "FastBi1K5", FakeFastBi1K5)
    source = vti_magnet.Magnet("192.168.1.50")
    source.connect()

    assert source.read() == pytest.approx(0.98765)


def test_vti_magnet_close_closes_the_driver(monkeypatch):
    made: list[FakeFastBi1K5] = []

    def make(name, host):
        made.append(FakeFastBi1K5(name, host))
        return made[-1]

    monkeypatch.setattr(vti_magnet, "FastBi1K5", make)
    source = vti_magnet.Magnet("192.168.1.50")
    source.connect()

    source.close()

    assert made[0].host == "192.168.1.50"
    assert made[0].closed


def test_vti_magnet_publishes_field_in_t(monkeypatch):
    writes = record_writes(monkeypatch, vti_magnet)

    data = vti_magnet.make_publish(None, "dgg", "bucket")(0.98765, 0)

    assert data == {"_summary": "0.9877 T", "magnetic field": "0.9877 T"}
    assert writes == [("vti", "magnetic field", 0.98765, "T")]


def test_vti_magnet_dry_run_publishes_the_same_payload_without_influx(monkeypatch):
    writes = record_writes(monkeypatch, vti_magnet)
    source = vti_magnet.FakeMagnet()

    field_T = source.read()
    data = vti_magnet.dry_publish(field_T, 0)

    assert field_T == pytest.approx(2.0 * math.sin(1 / 11.0))
    assert data == {"_summary": f"{field_T:.4f} T",
                    "magnetic field": f"{field_T:.4f} T"}
    assert writes == []
