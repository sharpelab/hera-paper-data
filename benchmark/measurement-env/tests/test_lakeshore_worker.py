"""The lakeshore worker's two output surfaces: the logfile and the publisher.

The worker writes tab-delimited lines; the measurement kernel reads them back
via sharpelab_nb.thermometry.temperature_from_logfiles. These two formats are
coupled by column layout (unix at col 0, kelvin at col -3) — the first tests
pin that contract so a worker-side format change can't silently break the
kernel. Heater power rides inside the status column for exactly that reason.

The rest cover LakeshorePublisher and Ls335Source, the two halves the worker
hands to core.poller: what lands in the logfiles and InfluxDB each cycle
(temperatures on the 30 s cadence, heater state also on any change), the
RDGST gate that keeps a faulted input's 0 K out of every sink, and the LS335
chained poll query with MODE 0 as the last command of each poll. The loop itself is
core.poller's and is tested there.
"""

from __future__ import annotations

import dataclasses
import time
import warnings

import pytest

from sharpelab_nb.thermometry import StaleThermometryWarning, temperature_from_logfiles
from workers import lakeshore
from workers.lakeshore import (
    INFLUX_EVERY,
    FakeLs335Source,
    InputReading,
    LakeshorePublisher,
    POLL_QUERY,
    Ls335Source,
    format_log_line,
    format_status,
    parse_poll,
)


def _write(path, t_unix, kelvin, *, sensor=1234.5, status="R0 P0.0"):
    # The tail reader walks back to the newline preceding the last line, so a
    # real (always multi-line) logfile is needed — write a prior reading too.
    prior = format_log_line(t_unix - 30, time.ctime(t_unix - 30), sensor, kelvin, status)
    last = format_log_line(t_unix, time.ctime(t_unix), sensor, kelvin, status)
    path.write_text(prior + last)


def test_logfile_roundtrips_through_temperature_from_logfiles(tmp_path):
    log = tmp_path / "VTI_sample.txt"
    _write(log, int(time.time()), 1.2345)

    T = temperature_from_logfiles("T_sample", [str(log)])
    assert T() == pytest.approx(1.2345)


def test_status_column_carries_power_without_moving_kelvin(tmp_path):
    """Range + power share one tab column, so kelvin stays at split index -3."""
    log = tmp_path / "VTI_vaporizer.txt"
    _write(log, int(time.time()), 4.2, status=format_status(3, 45.2))

    line = log.read_text().splitlines()[-1]
    assert line.split("\t")[-2] == "R3 P45.2"
    T = temperature_from_logfiles("T_vaporizer", [str(log)])
    assert T() == pytest.approx(4.2)


def test_freshest_candidate_is_chosen(tmp_path):
    now = int(time.time())
    stale = tmp_path / "VTI_stale.txt"
    fresh = tmp_path / "VTI_fresh.txt"
    _write(stale, now - 10_000, 9.999)
    _write(fresh, now, 1.500)

    T = temperature_from_logfiles("T_sample", [str(stale), str(fresh)])
    assert T() == pytest.approx(1.500)


def test_stale_logfile_warns_but_returns_value(tmp_path):
    log = tmp_path / "VTI_sample.txt"
    _write(log, int(time.time()) - 10_000, 1.2345)

    T = temperature_from_logfiles("T_sample", [str(log)], stale_after=300.0)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        value = T()
    assert value == pytest.approx(1.2345)
    assert any(issubclass(w.category, StaleThermometryWarning) for w in caught)


# --- Publisher: logfiles, InfluxDB cadence, and the [data] payload ---------

_SAMPLE = InputReading(kelvin=1.2345, sensor=1234.5, rdgst=0, range=0, power=0.0,
                       setpoint=0.0, mode=1, tlimit=320.0)
_VAPORIZER = InputReading(kelvin=4.2, sensor=987.65, rdgst=0, range=2, power=33.5,
                          setpoint=5.0, mode=1, tlimit=320.0)
_READINGS = {"sample": _SAMPLE, "vaporizer": _VAPORIZER}

_EXPECTED_LOGS = {
    "VTI_sample.txt": (1234.5, 1.2345, "R0 P0.0"),
    "VTI_vaporizer.txt": (987.65, 4.2, "R2 P33.5"),
}

_SAMPLE_STATE = [
    ("vti", "sample heater range", 0.0, ""),
    ("vti", "sample heater power", 0.0, "%"),
    ("vti", "sample setpoint", 0.0, "K"),
    ("vti", "sample control mode", 1.0, ""),
    ("vti", "tlimit a", 320.0, "K"),
    ("vti", "sample reading status", 0.0, ""),
]
_VAPORIZER_STATE = [
    ("vti", "vaporizer heater range", 2.0, ""),
    ("vti", "vaporizer heater power", 33.5, "%"),
    ("vti", "vaporizer setpoint", 5.0, "K"),
    ("vti", "vaporizer control mode", 1.0, ""),
    ("vti", "tlimit b", 320.0, "K"),
    ("vti", "vaporizer reading status", 0.0, ""),
]
_BATCH = (
    [("vti", "sample temperature", 1.2345, "K")] + _SAMPLE_STATE
    + [("vti", "vaporizer temperature", 4.2, "K")] + _VAPORIZER_STATE
)


def _assert_logfile(path, cycles):
    """Every line must be exactly what format_log_line produces for its stamp."""
    sensor, kelvin, status = _EXPECTED_LOGS[path.name]
    lines = path.read_text().splitlines(keepends=True)
    assert len(lines) == cycles
    for line in lines:
        t_unix = int(line.split("\t")[0])
        assert line == format_log_line(t_unix, time.ctime(t_unix), sensor, kelvin, status)


def test_publisher_writes_both_logfiles_every_cycle(tmp_path):
    publisher = LakeshorePublisher(tmp_path, None)

    for cycle in range(3):
        data = publisher(_READINGS, cycle)

    assert data == {
        "sample T": "1.234 K",
        "sample heater": "range 0, 0.0%, PID",
        "sample setpoint": "0.000 K",
        "tlimit a": "320 K",
        "vaporizer T": "4.200 K",
        "vaporizer heater": "range 2, 33.5%, PID",
        "vaporizer setpoint": "5.000 K",
        "tlimit b": "320 K",
        "_summary": "HEATING vap 4.2K→5K 34% · sam 1.234K",
    }
    for name in _EXPECTED_LOGS:
        _assert_logfile(tmp_path / name, cycles=3)


def test_tlimit_zero_reads_as_off(tmp_path):
    publisher = LakeshorePublisher(tmp_path, None)
    readings = {"sample": dataclasses.replace(_SAMPLE, tlimit=0.0), "vaporizer": _VAPORIZER}

    data = publisher(readings, 0)

    assert data["tlimit a"] == "off"
    assert "tlimit" not in data["_summary"]


@pytest.mark.parametrize("sample_range, vap_range, expected", [
    (0, 0, "sam 1.234K · vap 4.200K"),
    (3, 3, "HEATING sam 1.2K→0K 0%, vap 4.2K→5K 34%"),
    (0, 1, "HEATING vap 4.2K→5K 34% · sam 1.234K"),
    (2, 0, "HEATING sam 1.2K→0K 0% · vap 4.200K"),
])
def test_summary_leads_with_heating_loops(tmp_path, sample_range, vap_range, expected):
    publisher = LakeshorePublisher(tmp_path, None)
    readings = {"sample": dataclasses.replace(_SAMPLE, range=sample_range),
                "vaporizer": dataclasses.replace(_VAPORIZER, range=vap_range)}

    assert publisher(readings, 0)["_summary"] == expected


def test_summary_warmup_shape(tmp_path):
    readings = {"sample": dataclasses.replace(_SAMPLE, kelvin=150.2, range=3, setpoint=300.0, power=45.2),
                "vaporizer": dataclasses.replace(_VAPORIZER, kelvin=95.1, range=3, setpoint=100.0, power=12.0)}

    assert LakeshorePublisher(tmp_path, None)(readings, 0)["_summary"] == (
        "HEATING sam 150.2K→300K 45%, vap 95.1K→100K 12%")


def _record_points(monkeypatch):
    """Capture every write_point call as (measurement, metric, value, unit)."""
    points = []

    def fake_write_point(write_api, org, bucket, measurement, metric, value, unit):
        points.append((measurement, metric, value, unit))

    monkeypatch.setattr(lakeshore, "write_point", fake_write_point)
    return points


def test_influx_batch_lands_every_influx_every_cycles(tmp_path, monkeypatch):
    points = _record_points(monkeypatch)
    publisher = LakeshorePublisher(tmp_path, ("api", "dgg", "vti"))

    publisher(_READINGS, 0)
    assert points == _BATCH

    # Steady heater state: nothing lands between batches.
    for cycle in range(1, INFLUX_EVERY):
        publisher(_READINGS, cycle)
    assert len(points) == len(_BATCH)

    publisher(_READINGS, INFLUX_EVERY)
    assert points == _BATCH * 2
    # Both logfiles still got all seven cycles.
    for name in _EXPECTED_LOGS:
        _assert_logfile(tmp_path / name, cycles=INFLUX_EVERY + 1)


@pytest.mark.parametrize("field, value", [
    ("range", 3),
    ("setpoint", 300.0),
    ("mode", 3),
    ("tlimit", 0.0),
    ("rdgst", 160),
])
def test_heater_state_change_writes_immediately(tmp_path, monkeypatch, field, value):
    """A delta in range/setpoint/mode/tlimit/rdgst lands on the next poll, not the next batch."""
    points = _record_points(monkeypatch)
    publisher = LakeshorePublisher(tmp_path, ("api", "dgg", "vti"))
    publisher(_READINGS, 0)
    del points[:]

    changed = {"sample": _SAMPLE,
               "vaporizer": dataclasses.replace(_VAPORIZER, **{field: value})}
    publisher(changed, 1)

    # Only the changed loop's heater-state group — no temperatures, nothing for sample.
    assert [m for _, m, _, _ in points] == [
        "vaporizer heater range", "vaporizer heater power", "vaporizer setpoint",
        "vaporizer control mode", "tlimit b", "vaporizer reading status",
    ]
    assert dict((m, v) for _, m, v, _ in points)[_metric_for(field)] == float(value)

    # Same state again: quiet until the next batch.
    publisher(changed, 2)
    assert len(points) == 6


def _metric_for(field):
    return {"range": "vaporizer heater range", "setpoint": "vaporizer setpoint",
            "mode": "vaporizer control mode", "tlimit": "tlimit b",
            "rdgst": "vaporizer reading status"}[field]


def test_power_alone_does_not_trigger_a_write(tmp_path, monkeypatch):
    """PID power wanders every poll; it rides along with state, never triggers."""
    points = _record_points(monkeypatch)
    publisher = LakeshorePublisher(tmp_path, ("api", "dgg", "vti"))
    publisher(_READINGS, 0)
    del points[:]

    publisher({"sample": _SAMPLE, "vaporizer": dataclasses.replace(_VAPORIZER, power=48.1)}, 1)

    assert points == []


def test_delta_on_a_batch_cycle_writes_once(tmp_path, monkeypatch):
    points = _record_points(monkeypatch)
    publisher = LakeshorePublisher(tmp_path, ("api", "dgg", "vti"))
    publisher(_READINGS, 0)
    for cycle in range(1, INFLUX_EVERY):
        publisher(_READINGS, cycle)
    del points[:]

    publisher({"sample": _SAMPLE, "vaporizer": dataclasses.replace(_VAPORIZER, range=3)},
              INFLUX_EVERY)

    assert len(points) == len(_BATCH)
    assert ("vti", "vaporizer heater range", 3.0, "") in points


def test_invalid_input_publishes_no_temperature_anywhere(tmp_path, monkeypatch, capsys):
    """RDGST != 0 (curveless / faulted input reads 0 K): heater state still flows."""
    points = _record_points(monkeypatch)
    publisher = LakeshorePublisher(tmp_path, ("api", "dgg", "vti"))
    faulted = {"sample": dataclasses.replace(_SAMPLE, kelvin=0.0, sensor=5.0, rdgst=1),
               "vaporizer": _VAPORIZER}

    data = publisher(faulted, 0)

    assert not (tmp_path / "VTI_sample.txt").exists()
    _assert_logfile(tmp_path / "VTI_vaporizer.txt", cycles=1)
    faulted_state = [p if p[1] != "sample reading status" else ("vti", "sample reading status", 1.0, "")
                     for p in _SAMPLE_STATE]
    assert points == faulted_state + [("vti", "vaporizer temperature", 4.2, "K")] + _VAPORIZER_STATE
    assert data["sample T"] == "INVALID (RDGST 1)"
    assert data["_summary"] == "HEATING vap 4.2K→5K 34% · sam INVALID"

    # One [error] per transition, not one per cycle; recovery is announced once.
    publisher(faulted, 1)
    publisher(_READINGS, 2)
    publisher(_READINGS, 3)
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.startswith("[")]
    assert lines == [
        "[error] sample input invalid (RDGST 1): temperature not logged until it clears",
        "[init] sample input valid again (RDGST 0)",
    ]
    _assert_logfile(tmp_path / "VTI_sample.txt", cycles=2)


def test_logfile_failure_is_reported_and_influx_still_writes(tmp_path, monkeypatch, capsys):
    points = _record_points(monkeypatch)
    # A directory that does not exist: every open() for append raises.
    publisher = LakeshorePublisher(tmp_path / "gone", ("api", "dgg", "vti"))

    data = publisher(_READINGS, 0)

    errors = [line for line in capsys.readouterr().out.splitlines()
              if line.startswith("[error] ")]
    assert len(errors) == 2
    assert errors[0].startswith("[error] Log write failed (VTI_sample): ")
    assert errors[1].startswith("[error] Log write failed (VTI_vaporizer): ")
    assert points == _BATCH
    assert data["_summary"].startswith("HEATING vap ")


def test_influx_failure_is_reported_per_loop(tmp_path, monkeypatch, capsys):
    def boom(*args, **kwargs):
        raise ConnectionError("influx down")

    monkeypatch.setattr(lakeshore, "write_point", boom)
    publisher = LakeshorePublisher(tmp_path, ("api", "dgg", "vti"))

    publisher(_READINGS, 0)

    errors = [line for line in capsys.readouterr().out.splitlines()
              if line.startswith("[error] ")]
    assert errors == [
        "[error] InfluxDB write failed (sample): influx down",
        "[error] InfluxDB write failed (vaporizer): influx down",
    ]
    for name in _EXPECTED_LOGS:
        _assert_logfile(tmp_path / name, cycles=1)


# --- Source: the LS335 as the poll driver sees it -------------------------

# The rig's own answer to POLL_QUERY (2026-09-02, probe out, vaporizer at 95 K)
# with the sample fields swapped for _READINGS' values.
_RESPONSE = ("+1.2345;+1234.5;000;+0320;0;+000.0;+00.000;1,1,0;"
             "+4.2000;+987.65;000;+0320;2;+033.5;+05.000;1,2,0")


class _FakeLs335:
    """Enough of the qcodes driver for Ls335Source.read(): records the bus traffic."""

    def __init__(self, response=_RESPONSE):
        self.traffic: list[tuple[str, str]] = []  # ("ask" | "write", command)
        self._response = response

    def ask(self, cmd):
        self.traffic.append(("ask", cmd))
        return self._response

    def write(self, cmd):
        self.traffic.append(("write", cmd))


def test_poll_query_is_one_chained_string_under_the_255_char_limit():
    assert POLL_QUERY == (
        "KRDG? A;SRDG? A;RDGST? A;TLIMIT? A;RANGE? 1;HTR? 1;SETP? 1;OUTMODE? 1;"
        "KRDG? B;SRDG? B;RDGST? B;TLIMIT? B;RANGE? 2;HTR? 2;SETP? 2;OUTMODE? 2"
    )
    assert len(POLL_QUERY) + len("\r\n") <= 255


def test_source_read_composes_both_inputs():
    source = Ls335Source("GPIB0::10::INSTR")
    source.inst = _FakeLs335()

    assert source.read() == _READINGS


def test_source_read_is_one_query_then_mode_0():
    """The worker is the bus's only polling master: one transaction, then unlock."""
    source = Ls335Source("GPIB0::10::INSTR")
    source.inst = _FakeLs335()

    source.read()

    assert source.inst.traffic == [("ask", POLL_QUERY), ("write", "MODE 0")]


def test_rig_probe_response_parses():
    """Verbatim rig answer: sample input faulted (RDGST 160 = T-over + SU-over)."""
    rig = ("+00.000;+000005;160;+0325;0;+000.0;+300.00;1,1,0;"
           "+95.112;+074.92;000;+0325;0;+000.0;+03.000;1,2,0")

    r = parse_poll(rig)

    assert r["sample"] == InputReading(kelvin=0.0, sensor=5.0, rdgst=160, range=0, power=0.0,
                                       setpoint=300.0, mode=1, tlimit=325.0)
    assert not r["sample"].valid
    assert r["vaporizer"].kelvin == 95.112 and r["vaporizer"].setpoint == 3.0


@pytest.mark.parametrize("response", [
    _RESPONSE + ";+1.0",  # one field too many
    _RESPONSE.rsplit(";", 1)[0],  # one too few
    "+1.2345",  # a single-query answer — another master's response
    "",
])
def test_foreign_response_raises_before_mode_0(response):
    """A field-count mismatch is not our answer (second-master collision) — the
    cycle must raise into the poll driver's reconnect path, with nothing written."""
    source = Ls335Source("GPIB0::10::INSTR")
    source.inst = _FakeLs335(response)

    with pytest.raises(ValueError, match="expected 16 fields"):
        source.read()
    assert source.inst.traffic == [("ask", POLL_QUERY)]


def test_source_close_clears_the_qcodes_registry(monkeypatch):
    calls = []

    class _FakeInstrument:
        @staticmethod
        def close_all():
            calls.append("close_all")

    monkeypatch.setattr(lakeshore, "Instrument", _FakeInstrument)
    source = Ls335Source("GPIB0::10::INSTR")
    source.inst = _FakeLs335()

    source.close()

    assert calls == ["close_all"]
    assert source.inst is None


def test_fake_source_readings_carry_the_full_heater_state(tmp_path):
    """--dry-run exercises the same publisher path as hardware."""
    source = FakeLs335Source()
    source.connect()

    data = LakeshorePublisher(tmp_path, None)(source.read(), 0)

    assert set(data) == {
        "sample T", "sample heater", "sample setpoint", "tlimit a",
        "vaporizer T", "vaporizer heater", "vaporizer setpoint", "tlimit b",
        "_summary",
    }
    assert data["tlimit a"] == "320 K"
    for name in _EXPECTED_LOGS:
        assert (tmp_path / name).exists()
