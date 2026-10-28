"""Tests for hera.analysis. Fixtures from the b1c2 post-session archive."""

import warnings
from pathlib import Path

import numpy as np
import pytest

from hera.analysis import open_run, summarize_run

REPO_ROOT = Path(__file__).resolve().parents[2]
B1C2_DATA = REPO_ROOT / "hera/docs/notes/2026-05-05-b1c2-session/data"


@pytest.fixture
def run_119():
    return open_run(B1C2_DATA / "119")


def test_open_run_basic(run_119):
    assert run_119.rows == 101
    assert run_119.kind == "1D"
    assert run_119.recipe == "gate-current-sanity-check"
    assert run_119.tags == ["gate: tg"]
    assert run_119.swept_axis == "k_tg_volt"
    assert not run_119.interrupted
    assert run_119.setpoints is not None
    assert len(run_119.setpoints) == 101


def test_col_unique(run_119):
    T = run_119.col("T")
    assert T.shape == (101,)
    assert T.mean() == pytest.approx(0.494, abs=0.01)


def test_col_duplicate_returns_planned_with_warning(run_119):
    # k_tg_volt appears at idx 1 (planned setpoint) and idx 3 (readback):
    # col() returns the planned instance and warns with the indices.
    with pytest.warns(UserWarning, match=r"appears at indices \[1, 3\]"):
        arr = run_119.col("k_tg_volt")
    assert np.array_equal(arr, run_119.col_at(1))


def test_col_unique_does_not_warn(run_119):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        run_119.col("T")


def test_col_at(run_119):
    arr = run_119.col_at(1)
    assert arr[0] == pytest.approx(0.0)
    assert arr[-1] == pytest.approx(1.0)


def test_col_missing_raises(run_119):
    with pytest.raises(KeyError):
        run_119.col("nonexistent")


def test_col_indices(run_119):
    assert run_119.col_indices("k_tg_volt") == [1, 3]
    assert run_119.col_indices("T") == [2]
    assert run_119.col_indices("nonexistent") == []


def test_metadata_aliases_meta(run_119):
    assert run_119.metadata is run_119.meta


def test_summarize_run(run_119):
    out = summarize_run(run_119)
    assert "run 119" in out
    assert "1D sweep" in out
    assert "gate-current-sanity-check" in out
    assert "gate: tg" in out
    assert "101 of 101" in out
    assert "complete" in out
    assert "k_tg_volt" in out
    assert "monotonic" in out
    assert "0.494" in out  # T mean


def test_open_run_missing_metadata(tmp_path):
    with pytest.raises(FileNotFoundError):
        open_run(tmp_path)


def test_open_run_not_a_directory(tmp_path):
    f = tmp_path / "not_a_dir"
    f.write_text("hi")
    with pytest.raises(FileNotFoundError):
        open_run(f)


def test_open_run_column_count_mismatch(tmp_path):
    (tmp_path / "metadata.json").write_text('{"columns": ["a", "b", "c"]}')
    (tmp_path / "data.tsv").write_text("1.0\t2.0\n3.0\t4.0\n")
    with pytest.raises(ValueError, match="column count mismatch"):
        open_run(tmp_path)


def test_summarize_run_omits_T_when_absent(tmp_path):
    (tmp_path / "metadata.json").write_text(
        '{"columns": ["x", "y"], "type": "1D", "param": "x", '
        '"setpoints": [0.0, 0.5, 1.0], "interrupted": false}'
    )
    (tmp_path / "data.tsv").write_text("0.0\t10.0\n0.5\t20.0\n1.0\t30.0\n")
    out = summarize_run(open_run(tmp_path))
    assert "T:" not in out
    assert "complete" in out


def test_summarize_run_interrupted(tmp_path):
    (tmp_path / "metadata.json").write_text(
        '{"columns": ["x"], "type": "1D", "param": "x", '
        '"setpoints": [0.0, 0.5, 1.0], "interrupted": true}'
    )
    (tmp_path / "data.tsv").write_text("0.0\n0.5\n")
    out = summarize_run(open_run(tmp_path))
    assert "interrupted at 2/3" in out


# --------------------------------------------------------------------------
# In-flight runs: names map from metadata.json (on disk from sweep start);
# the growing TSV may end mid-row.
# --------------------------------------------------------------------------

_INFLIGHT_META = (
    '{"columns": ["x", "y"], "type": "1D", "param": "x", '
    '"setpoints": [0.0, 0.5, 1.0], "interrupted": false}'
)


def test_open_run_in_flight_drops_partial_trailing_row(tmp_path):
    (tmp_path / "metadata.json").write_text(_INFLIGHT_META)
    (tmp_path / "data.tsv").write_text("0.0\t10.0\n0.5\t20.0\n1.0\t3")
    run = open_run(tmp_path)
    assert run.rows == 2
    assert not run.complete
    assert np.array_equal(run.col("y"), [10.0, 20.0])


def test_open_run_in_flight_zero_rows(tmp_path):
    # Sweep creates the TSV before the first point lands.
    (tmp_path / "metadata.json").write_text(_INFLIGHT_META)
    (tmp_path / "data.tsv").write_text("")
    run = open_run(tmp_path)
    assert run.rows == 0
    assert run.cols == ["x", "y"]
    assert run.data.shape == (0, 2)


def test_open_run_in_flight_only_partial_row(tmp_path):
    (tmp_path / "metadata.json").write_text(_INFLIGHT_META)
    (tmp_path / "data.tsv").write_text("0.0\t1")
    assert open_run(tmp_path).rows == 0


def test_open_run_crlf_line_endings(tmp_path):
    # The rigs are Windows; csv.writer emits \r\n there. newline="" writes the
    # \r\n verbatim on every platform (text mode would double the \r on Windows).
    (tmp_path / "metadata.json").write_text(_INFLIGHT_META)
    (tmp_path / "data.tsv").write_text("0.0\t10.0\r\n0.5\t20.0\r\n", newline="")
    run = open_run(tmp_path)
    assert run.rows == 2
    assert np.array_equal(run.col("y"), [10.0, 20.0])


def test_run_complete_property(tmp_path, run_119):
    assert run_119.complete  # archived run: end_time present
    (tmp_path / "metadata.json").write_text(_INFLIGHT_META)
    (tmp_path / "data.tsv").write_text("0.0\t10.0\n")
    assert not open_run(tmp_path).complete


def test_summarize_run_in_flight(tmp_path):
    (tmp_path / "metadata.json").write_text(_INFLIGHT_META)
    (tmp_path / "data.tsv").write_text("0.0\t10.0\n0.5\t20.0\n")
    out = summarize_run(open_run(tmp_path))
    assert "2 of 3 (in flight)" in out
