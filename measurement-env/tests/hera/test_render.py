"""Snapshot-style render tests against Nathan's RPL19/18 fixture.

Asserts shape stability of the rendered markdown — checks for required headings,
finding labels, the coordinate guard line, and the brief-mode shape.
"""

from __future__ import annotations

import json
from pathlib import Path

from hera.models import Annotation
from hera.render import coordinate_guard, render, render_brief


def _load(nathan_dataset_root: Path, scan: str) -> Annotation:
    return Annotation.model_validate_json(
        (nathan_dataset_root / scan / "annotations.json").read_text()
    )


def test_render_full_includes_required_sections(
    nathan_dataset_root: Path, tmp_path: Path,
) -> None:
    ann = _load(nathan_dataset_root, "RPL19/18")
    sidecar = tmp_path / "sidecar.json"
    md = render(
        ann,
        timestamp="2026-05-05T12:00:00Z",
        model="gemini-2.5-flash",
        channels=["Rxx", "phase", "current"],
        sidecar_path=str(sidecar),
    )
    assert md.startswith("## Scan analysis: 18 @ ")
    assert "**Channels analyzed:** Rxx, phase, current" in md
    assert "**Scan limits:** Vbg ∈ [-8.0, 6.5], Vtg ∈ [-1.0, 1.0]" in md
    assert "**Model:** gemini-2.5-flash" in md
    assert "**Findings:**" in md
    # Each Nathan finding has an `id` so the heading uses it as the label.
    assert "### cnp_diagonal — Charge neutrality line" in md
    assert "**Coordinate guard:** all findings within scan limits ✓" in md
    assert f"**Sidecar:** {sidecar}" in md


def test_render_brief_one_paragraph(nathan_dataset_root: Path) -> None:
    ann = _load(nathan_dataset_root, "RPL19/18")
    out = render_brief(ann)
    assert out.startswith("18: 4 findings — ")
    assert out.count("\n") == 1  # single paragraph + trailing newline


def test_coordinate_guard_clean(nathan_dataset_root: Path) -> None:
    for scan in ["RPL19/18", "RPL19/21", "RPL10/24", "RPL10/220"]:
        ann = _load(nathan_dataset_root, scan)
        violations = coordinate_guard(ann)
        assert violations == [], f"unexpected violations in {scan}: {violations}"


def test_coordinate_guard_fires_on_violation(nathan_dataset_root: Path) -> None:
    raw = json.loads(
        (nathan_dataset_root / "RPL19/18/annotations.json").read_text()
    )
    raw["findings"][0]["region_gate"]["vbg_end"] = 99.0
    ann = Annotation.model_validate(raw)
    violations = coordinate_guard(ann)
    assert len(violations) == 1
    assert violations[0].finding_id == "cnp_diagonal"
    assert "99.0" in violations[0].detail

    md = render(ann, timestamp="t", model="m")
    assert "**Coordinate guard:** ✗ cnp_diagonal:" in md


def test_brief_handles_zero_findings() -> None:
    from hera.models import ScanLimits

    ann = Annotation(
        scan_limits=ScanLimits(vbg_min=-1, vbg_max=1, vtg_min=-1, vtg_max=1),
        device="RPL19",
        scan_id="dummy",
        findings=[],
    )
    out = render_brief(ann)
    assert "0 findings — no findings" in out
