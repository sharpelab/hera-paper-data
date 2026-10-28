"""HealthEntry reads a `metrics` list and rejects everything else.

The scalar `metric = "x"` spelling the rig configs once used is gone; a
config still carrying it fails to load with the key named, so a stale
deployed toml is caught at launcher start rather than read as healthy.
"""

from __future__ import annotations

import pytest

from core.config import ConfigError, HealthEntry, load_vti_config

_BASE = """
[hardware]
lakeshore_gpib = "GPIB0::10::INSTR"
temperature_log_dir = 'C:\\\\logs'
ami1700_addr = "TCPIP0::1.2.3.4::7180::SOCKET"
terranova_addr = "ASRL8::INSTR"
lakeshore218_gpib = "GPIB0::15::INSTR"
fastbi_host = "192.168.0.10"

[influxdb]
url = "https://example.invalid"
token = "dummy"
org = "dgg"
bucket = "vti"
"""


def _load(tmp_path, health: str):
    path = tmp_path / "vti.toml"
    path.write_text(_BASE + health)
    return load_vti_config(path)


def test_metrics_list_is_kept_in_order():
    entry = HealthEntry.from_toml({"metrics": ["a", "b"], "threshold": 90})
    assert entry.metrics == ("a", "b")
    assert entry.threshold == 90


def test_scalar_spelling_is_rejected(tmp_path):
    with pytest.raises(ConfigError, match=r"health\.demo\.metrics"):
        _load(tmp_path, '''
[health.demo]
metric = "magnet temperature"
threshold = 90
''')


def test_list_config_loads(tmp_path):
    cfg = _load(tmp_path, '''
[health.demo]
metrics = ["He level", "probe space pressure"]
threshold = 90
''')
    assert cfg.health["demo"].metrics == ("He level", "probe space pressure")


def test_neither_spelling_reports_metrics(tmp_path):
    with pytest.raises(ConfigError, match=r"health\.demo\.metrics"):
        _load(tmp_path, '''
[health.demo]
threshold = 90
''')


def test_empty_metrics_list_reports_metrics(tmp_path):
    with pytest.raises(ConfigError, match=r"health\.demo\.metrics"):
        _load(tmp_path, '''
[health.demo]
metrics = []
threshold = 90
''')


def test_metrics_as_a_bare_string_is_rejected(tmp_path):
    # tuple("He level") is nine one-character metrics — catch it at the
    # boundary rather than sending nonsense to InfluxDB.
    with pytest.raises(ConfigError, match=r"health\.demo\.metrics"):
        _load(tmp_path, '''
[health.demo]
metrics = "He level"
threshold = 90
''')


def test_missing_threshold_reports_threshold(tmp_path):
    with pytest.raises(ConfigError, match=r"health\.demo\.threshold"):
        _load(tmp_path, '''
[health.demo]
metrics = ["He level"]
''')
