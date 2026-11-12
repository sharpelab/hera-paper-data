"""pink.toml.example must parse with the current PinkConfig schema.

Pins the config contract the pink workers depend on: the example template
(the shape the rig's pink.toml is created from at cutover) has to expose
the LC logs folder and the health sections the launcher + workers read,
so a schema change can't silently leave the deployed config short a key.

The shipped template has an intentionally empty influxdb.token (filled on
the rig), which the loader treats as missing — so the test injects a dummy
token into a tmp copy before loading, exercising the real load path.
"""

from __future__ import annotations

import pytest

from core import REPO_DIR
from core.config import load_pink_config

EXAMPLE = REPO_DIR / "pink.toml.example"


@pytest.fixture
def loaded(tmp_path):
    text = EXAMPLE.read_text().replace('token = ""', 'token = "dummy"')
    cfg_path = tmp_path / "pink.toml"
    cfg_path.write_text(text)
    return load_pink_config(cfg_path)


def test_example_parses_with_full_hardware_schema(loaded):
    assert loaded.hardware.lc_logs_folder
    assert loaded.hardware.ami430_addr
    assert loaded.influxdb.bucket == "016_pink"


def test_example_has_health_entries_for_every_worker(loaded):
    # health_key -> the worker panel that reads it
    for key in ("lc_scrapper_fp", "lc_scrapper_tc", "magnet"):
        assert key in loaded.health, f"missing [health.{key}]"
        assert loaded.health[key].metrics
