"""vti.toml.example must parse with the current VtiConfig schema.

Pins the config contract the VTI workers depend on: the example template (the
shape the rig's vti.toml is created from at cutover) has to expose every
hardware address and health section the launcher + workers read, so a schema
change can't silently leave the deployed config short a key.

The shipped template has an intentionally empty influxdb.token (filled on the
rig), which the loader treats as missing — so the test injects a dummy token
into a tmp copy before loading, exercising the real load path.
"""

from __future__ import annotations

import pytest

from core import REPO_DIR
from core.config import load_vti_config

EXAMPLE = REPO_DIR / "vti.toml.example"


@pytest.fixture
def loaded(tmp_path):
    text = EXAMPLE.read_text().replace('token = ""', 'token = "dummy"')
    cfg_path = tmp_path / "vti.toml"
    cfg_path.write_text(text)
    return load_vti_config(cfg_path)


def test_example_parses_with_full_hardware_schema(loaded):
    hw = loaded.hardware
    assert hw.lakeshore_gpib
    assert hw.ami1700_addr
    assert hw.terranova_addr
    assert hw.lakeshore218_gpib
    assert hw.fastbi_host


def test_example_has_health_entries_for_every_worker(loaded):
    # health_key -> the worker panel that reads it
    for key in ("lakeshore", "vti_aux", "magnet"):
        assert key in loaded.health, f"missing [health.{key}]"
        assert loaded.health[key].metric
