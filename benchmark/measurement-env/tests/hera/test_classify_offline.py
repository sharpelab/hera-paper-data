"""End-to-end CLI smoke test in --dry-run mode. No API calls.

Live-API validation against Nathan's dataset (the real correctness check) is
DEFERRED — it costs Flash dollars per run. When ready, add a separate
`test_classify_live.py` marked with @pytest.mark.live and gated behind
`pytest -m live`.
"""

from __future__ import annotations
import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from hera.classify import _run_main


@pytest.fixture
def target_image(
    nathan_dataset_root: Path, tmp_path: Path
) -> Path:
    src = nathan_dataset_root / "RPL19" / "21" / "plot.png"
    dst = tmp_path / "21" / "plot.png"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())
    return dst


def _run(args: list[str]) -> tuple[int, str, str]:
    """Run _run_main inline, capturing stdout and stderr."""

    stdout = StringIO()
    stderr = StringIO()
    rc: int
    with redirect_stdout(stdout), redirect_stderr(stderr):
        rc = _run_main(args)
    return rc, stdout.getvalue(), stderr.getvalue()


def test_dry_run_writes_sidecar_and_prints_markdown(target_image: Path) -> None:
    rc, out, err = _run(["--dry-run", str(target_image)])
    assert rc == 0, err
    assert "## Scan analysis: 21 @" in out
    assert "**Coordinate guard:**" in out
    sidecars = list((target_image.parent / "hera").glob("plot__*.json"))
    assert len(sidecars) == 1
    sidecar = json.loads(sidecars[0].read_text())
    assert sidecar["annotation"]["device"]
    assert sidecar["provenance"]["model"] == "gemini-2.5-flash"


def test_dry_run_brief(target_image: Path) -> None:
    rc, out, err = _run(["--dry-run", "--brief", str(target_image)])
    assert rc == 0, err
    assert out.startswith("21: ")
    assert "finding" in out


def test_no_sidecar_flag(target_image: Path) -> None:
    rc, _, err = _run(["--dry-run", "--no-sidecar", str(target_image)])
    assert rc == 0, err
    assert not (target_image.parent / "hera").exists()


def test_explicit_sidecar_path(tmp_path: Path, target_image: Path) -> None:
    sidecar = tmp_path / "explicit.json"
    rc, _, err = _run(["--dry-run", "--sidecar", str(sidecar), str(target_image)])
    assert rc == 0, err
    assert sidecar.exists()


def test_missing_image_fails_cleanly(tmp_path: Path) -> None:
    rc, _, err = _run(["--dry-run", str(tmp_path / "does-not-exist.png")])
    assert rc != 0
    assert "image does not exist" in err
