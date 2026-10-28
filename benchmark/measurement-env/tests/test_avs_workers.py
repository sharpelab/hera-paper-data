"""The two AVS-47B bridge workers: Source wiring and publish payloads.

core.poller owns the loop (tests/test_poller.py), so each worker is a Source
over one persistent GPIB session plus a publish that fans a reading out to
InfluxDB, the local temperature logfiles the kernel reads back, and the
[data] payload. These pin what read() yields, that close() tears the session
down, and the exact metric/value/unit, logfile line, and payload published.
"""

from __future__ import annotations

import re

from workers import avs_fridge, avs_probe
from workers.avs_calibration import SENSORS_FRIDGE, SENSORS_PROBE1


class FakeAvs:
    """Scripted AVS-47B: answers the queries the scan/measure paths issue."""

    def __init__(self, ohms_by_channel: dict[int, float], *, mux=3, exc=1, inp=1):
        self.ohms = ohms_by_channel
        self.state = f"MUX {mux};EXC {exc};INP {inp}"
        self.writes: list[str] = []
        self.closed = False
        self.cleared = 0

    def write(self, cmd):
        self.writes.append(cmd)
        if cmd.startswith("REM 1;MUX "):
            self.state = cmd.removeprefix("REM 1;").removesuffix(";REM 0")

    def query(self, cmd):
        if cmd == "*OPC?":
            return "1"
        if cmd == "MUX ?; EXC ?; INP ?":
            return self.state
        if cmd.startswith("REM 1;SCR "):
            ch = int(re.search(r"SCR (\d)", cmd).group(1))
            return f"AVE {self.ohms[ch]};STD 0.5"
        if cmd == "REM 1;AVE?;STD?;REM 0":
            mux = int(self.state.split(";")[0].split()[1])
            return f"AVE {self.ohms[mux]};STD 0.5"
        raise AssertionError(f"unexpected query {cmd!r}")

    def clear(self):
        self.cleared += 1

    def close(self):
        self.closed = True


def connect_to(monkeypatch, module, avs):
    opened: list[str] = []

    def fake_connect(addr):
        opened.append(addr)
        return ("rm", avs)

    monkeypatch.setattr(module, "connect_gpib", fake_connect)
    return opened


def record_writes(monkeypatch, module) -> list[tuple]:
    writes: list[tuple] = []
    monkeypatch.setattr(
        module, "write_point",
        lambda api, org, bucket, measurement, metric, value, unit: writes.append(
            (measurement, metric, value, unit)),
    )
    return writes


# --- fridge -------------------------------------------------------------------


def test_fridge_read_scans_every_channel(monkeypatch):
    avs = FakeAvs({ch: 1000.0 + ch for ch in range(6)})
    opened = connect_to(monkeypatch, avs_fridge, avs)
    source = avs_fridge.FridgeBridge("GPIB11::21::INSTR")
    source.connect()

    scan = source.read()

    assert opened == ["GPIB11::21::INSTR"]
    assert [(ch, ohms) for ch, ohms, _std in scan] == [
        (ch, 1000.0 + ch) for ch in range(6)]
    assert "REM 1;SCN 0;REM 0" in avs.writes


def test_fridge_close_tears_down_the_session(monkeypatch):
    avs = FakeAvs({})
    connect_to(monkeypatch, avs_fridge, avs)
    source = avs_fridge.FridgeBridge("GPIB11::21::INSTR")
    source.connect()

    source.close()

    assert avs.closed


def test_fridge_publish_writes_influx_logfiles_and_payload(monkeypatch, tmp_path):
    writes = record_writes(monkeypatch, avs_fridge)
    scan = [(ch, 2000.0, 0.5) for ch in range(6)]

    data = avs_fridge.make_publish(None, "dgg", "b", tmp_path)(scan, 0)

    names = [SENSORS_FRIDGE[ch][0] for ch in range(6)]
    assert [m for m, *_ in writes] == ["AVS_bridge"] * 12
    assert [metric for _, metric, _, _ in writes] == [n for n in names for _ in (0, 1)]
    assert [unit for *_, unit in writes] == ["ohms", "kelvin"] * 6
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted(
        f"Fridge_{n}.txt" for n in names)
    line = (tmp_path / "Fridge_MixingCh_low.txt").read_text()
    assert line.count("\n") == 1
    assert "\t   2000.00\t" in line and line.endswith("\tIdle\t\n")
    assert set(data) == set(names) | {"_summary"}
    assert data["_summary"].startswith("MixCh: ")
    assert "(2000.0 Ω)" in data["MixingCh_low"]


def test_fridge_publish_survives_write_failures(monkeypatch, tmp_path, capsys):
    def boom(*args, **kwargs):
        raise RuntimeError("401 Unauthorized")

    monkeypatch.setattr(avs_fridge, "write_point", boom)

    data = avs_fridge.make_publish(None, "dgg", "b", tmp_path / "missing")(
        [(3, 2000.0, 0.5)], 1)

    out = capsys.readouterr().out
    assert "[error] InfluxDB write failed (MixingCh_low): 401 Unauthorized" in out
    assert "[error] Log write failed (MixingCh_low):" in out
    assert "MixingCh_low" in data


def test_fridge_first_scan_gets_a_longer_data_timeout():
    # One scan takes ~210 s; the driver default (60 s) would kill the worker
    # before its first reading.
    assert avs_fridge.DATA_TIMEOUT > avs_fridge.SCAN_INTERVAL


# --- probe --------------------------------------------------------------------


def test_probe_read_reconfigures_only_when_the_bridge_state_differs(monkeypatch):
    avs = FakeAvs({3: 1500.0, 4: 1600.0}, mux=3, exc=1, inp=1)
    connect_to(monkeypatch, avs_probe, avs)
    source = avs_probe.ProbeBridge("GPIB10::20::INSTR", channel=3, excitation=1,
                                   averages=10)
    source.connect()

    assert source.read() == (1500.0, 0.5)
    assert avs.cleared == 0  # already on MUX 3 / EXC 1 / INP 1

    other = avs_probe.ProbeBridge("GPIB10::20::INSTR", channel=4, excitation=2,
                                  averages=10)
    other.connect()
    assert other.read() == (1600.0, 0.5)
    assert avs.cleared == 1
    assert "REM 1;MUX 4;EXC 2;INP 1;REM 0" in avs.writes


def test_probe_close_tears_down_the_session(monkeypatch):
    avs = FakeAvs({})
    connect_to(monkeypatch, avs_probe, avs)
    source = avs_probe.ProbeBridge("GPIB10::20::INSTR", 3, 1, 10)
    source.connect()

    source.close()

    assert avs.closed


def test_probe_publish_writes_influx_logfile_and_payload(monkeypatch, tmp_path):
    writes = record_writes(monkeypatch, avs_probe)
    name, cal_fn = SENSORS_PROBE1[3]
    publish = avs_probe.make_publish(None, "dgg", "b", tmp_path, 1, name, cal_fn)

    data = publish((2000.0, 0.5), 0)

    kelvin = cal_fn(2000.0)
    assert writes == [
        ("AVS_bridge", "P1_MixingCh_low", 2000.0, "ohms"),
        ("AVS_bridge", "P1_MixingCh_low", kelvin, "kelvin"),
        ("AVS_bridge", "probe status", 0, "status"),
    ]
    assert (tmp_path / "Probe1_MixingCh_low.txt").read_text().endswith("\tIdle\t\n")
    assert set(data) == {"_summary", "P1_MixingCh_low"}
    assert data["_summary"].startswith("P1 MixCh: ")
    assert data["P1_MixingCh_low"].endswith("(2000.0 Ω)")



def test_probe_status_metric_is_written_whatever_is_selected(monkeypatch, tmp_path):
    """The freshness guard keys on this, not on the selection-named metric."""
    writes = record_writes(monkeypatch, avs_probe)
    name, cal_fn = SENSORS_PROBE1[1]
    avs_probe.make_publish(None, "dgg", "b", tmp_path, 2, name, cal_fn)((900.0, 0.1), 5)

    assert ("AVS_bridge", "probe status", avs_probe.STATUS_VALID, "status") in writes
    assert not any(metric == "P1_MixingCh_low" for _, metric, _, _ in writes)
