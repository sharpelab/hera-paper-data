"""Schema round-trip: every annotated scan in Nathan's dataset must validate
against our Annotation model. Lossless re-serialization expected."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hera.models import Annotation
from tests.hera.conftest import ANNOTATED_SCANS


@pytest.mark.parametrize("scan", ANNOTATED_SCANS)
def test_annotation_roundtrip(nathan_dataset_root: Path, scan: str) -> None:
    src = (nathan_dataset_root / scan / "annotations.json").read_text()
    ann = Annotation.model_validate_json(src)
    # Round-trip should produce equivalent JSON shape (after kind inference fills in defaults).
    out = ann.model_dump(exclude_none=True)
    src_data = json.loads(src)
    assert out["device"] == src_data["device"]
    assert out["scan_id"] == src_data["scan_id"]
    assert len(out["findings"]) == len(src_data["findings"])
    # Sanity: every finding's region (when present) has a kind
    for f in out["findings"]:
        rg = f.get("region_gate")
        if rg is not None:
            assert rg.get("kind"), f"region_gate missing kind: {rg}"


def test_invalid_region_gate_rejected() -> None:
    from pydantic import ValidationError
    from hera.models import RegionGate

    # All coordinates None and no description → must reject.
    with pytest.raises(ValidationError):
        RegionGate()


def test_finding_normalizes_string_region_gate() -> None:
    from hera.models import Finding

    f = Finding(title="x", description="y", region_gate="upper-left corner")  # type: ignore[arg-type]
    assert f.region_gate is not None
    assert f.region_gate.kind == "descriptive"
    assert f.region_gate.description == "upper-left corner"
