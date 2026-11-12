"""Tests for hera.watch — the live run-dir digest engine.

Geometry / gain / format tests use the committed b1c2 archive fixtures
(117 = 2D, 119 = 1D). The live-tail path is exercised against a synthetic
run dir grown row-by-row, with injected clock/sleep so no wall time passes.
"""

import gzip
import json
import re
from pathlib import Path

import numpy as np
import pytest

from hera.watch import (
    build_model,
    digest_once,
    existing_run_ids,
    fmt_eng,
    fmt_sp,
    header_lines,
    read_rows,
    ready_run_ids,
    resolve_next_run,
    run_complete,
    run_dir_ready,
    run_dir_started,
    wait_for_metadata,
    wait_for_next_run,
    wait_for_run,
    watch,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
B1C2_DATA = REPO_ROOT / "hera/docs/notes/2026-05-05-b1c2-session/data"


# --------------------------------------------------------------------------
# fmt helpers
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value,unit,expected",
    [
        (1.6e-9, "A", "1.60nA"),
        (-1.6e-9, "A", "-1.60nA"),
        (410.0, "Ω", "410Ω"),
        (95.37, "Ω", "95.4Ω"),
        (3960.0, "Ω", "3.96kΩ"),
        (5e-9, "A", "5.00nA"),
        (0.0, "A", "0A"),
        (1.2e6, "Ω", "1.20MΩ"),
    ],
)
def test_fmt_eng(value, unit, expected):
    assert fmt_eng(value, unit) == expected


def test_fmt_eng_nan():
    assert fmt_eng(float("nan"), "A") == "nan"


def test_fmt_sp_snaps_near_zero():
    assert fmt_sp(2.132e-14) == "0"
    assert fmt_sp(0.0) == "0"
    assert fmt_sp(8.0) == "+8"
    assert fmt_sp(-5.95) == "-5.95"


# --------------------------------------------------------------------------
# model: geometry + gain/channel mapping
# --------------------------------------------------------------------------


@pytest.fixture
def model_117():
    # 2D: magnet_field × (k_tg/k_bg), 401 × 51, gains present in mc.
    return build_model(B1C2_DATA / "117")


@pytest.fixture
def model_119():
    # 1D: k_tg_volt, 101 pts.
    return build_model(B1C2_DATA / "119")


def test_2d_geometry(model_117):
    assert model_117.kind == "2D"
    assert model_117.is_2d
    assert model_117.n_slow == 401
    assert model_117.n_fast == 51
    assert model_117.expected_rows == 401 * 51
    assert model_117.slow_param == "magnet_field"
    assert model_117.fast_params == ["k_tg_volt", "k_bg_volt"]


def test_1d_geometry(model_119):
    assert model_119.kind == "1D"
    assert not model_119.is_2d
    assert model_119.n_slow == 1
    assert model_119.n_fast == 101
    assert model_119.expected_rows == 101


def test_channel_gain_mapping_b1c2(model_117):
    # b1c2 columns are sr830_1_X..sr830_4_X; gains keyed sr1_gain..sr4_gain.
    by_cid = {c.cid: c for c in model_117.channels}
    assert set(by_cid) == {"sr830_1", "sr830_2", "sr830_3", "sr830_4"}
    # sr1_gain = -1e6 -> current channel; sr2/3/4_gain = 1e2 -> voltage.
    assert by_cid["sr830_1"].gain == -1e6
    assert by_cid["sr830_1"].is_current
    assert by_cid["sr830_2"].gain == 100.0
    assert not by_cid["sr830_2"].is_current


def test_i_bias_from_mc(model_117):
    # Legacy fallback: flat bias_voltage_1 = 0.1, bias_resistor = 1e8 -> 1 nA.
    assert model_117.i_bias == pytest.approx(0.1 / 1e8)


def test_i_bias_from_snapshot(tmp_path):
    # No flat bias_voltage; drive amplitude comes from the live station snapshot.
    d = tmp_path / "run"
    d.mkdir()
    _write_meta(
        d,
        measurement_config={
            "sr1": "a-b", "bias_channel": "sr830_1", "bias_resistor": 1e8,
        },
        instruments={
            "sr830_1": {"snapshot": {"parameters": {"amplitude": {"value": 0.1}}}}
        },
    )
    assert build_model(d).i_bias == pytest.approx(0.1 / 1e8)


def test_i_bias_snapshot_beats_stale_mc(tmp_path):
    # The zf1 ×25 bug: a stale flat bias_voltage_1 (residual 4 mV) must lose to
    # the live snapshot amplitude (0.1 V) when bias_channel is present.
    d = tmp_path / "run"
    d.mkdir()
    _write_meta(
        d,
        measurement_config={
            "sr1": "a-b", "bias_channel": "sr830_1",
            "bias_voltage_1": 0.004, "bias_resistor": 1e8,
        },
        instruments={
            "sr830_1": {"snapshot": {"parameters": {"amplitude": {"value": 0.1}}}}
        },
    )
    assert build_model(d).i_bias == pytest.approx(0.1 / 1e8)


def test_channel_filter():
    m = build_model(B1C2_DATA / "117", channels=["sr830_2"])
    assert [c.cid for c in m.channels] == ["sr830_2"]


def test_bias_current_override():
    m = build_model(B1C2_DATA / "117", bias_current=2e-9)
    assert m.i_bias == 2e-9


def test_missing_dir():
    with pytest.raises(FileNotFoundError):
        build_model(B1C2_DATA / "does-not-exist")


def test_megasweep_singular_schema(tmp_path):
    # Plain megasweep writes singular slow_param/fast_param and flat
    # setpoint lists (multimegasweep writes the plurals). Both resolve.
    d = tmp_path / "run"
    d.mkdir()
    _write_meta(
        d,
        function="megasweep",
        slow_params=None, fast_params=None,
        slow_param="mag", fast_param="k_bg_volt",
        slow_setpoints=[0.0, 1.0, 2.0],
        fast_setpoints=[-1.0, 0.0, 1.0],
    )
    m = build_model(d)
    assert m.is_2d
    assert m.slow_param == "mag"
    assert m.fast_params == ["k_bg_volt"]
    assert m.n_slow == 3 and m.n_fast == 3


def test_megasweep_digest_labels_slow_axis(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    _write_meta(
        d,
        function="megasweep",
        slow_params=None, fast_params=None,
        slow_param="mag", fast_param="k_bg_volt",
        slow_setpoints=[0.0, 1.0, 2.0],
        fast_setpoints=[-1.0, 0.0, 1.0],
    )
    (d / "data.tsv").write_text(
        "\n".join(_row(0, n, 5e-7) for n in (-1.0, 0.0, 1.0)) + "\n"
    )
    out = list(digest_once(build_model(d), now=1100.0))
    assert "mag=0" in out[0]
    assert "None=" not in out[0]


def test_digest_no_slow_name_omits_label(tmp_path):
    # Degenerate metadata (2D, setpoints but no slow name anywhere) must not
    # print a "None=" coordinate.
    d = tmp_path / "run"
    d.mkdir()
    _write_meta(d, slow_params=None)
    (d / "data.tsv").write_text(
        "\n".join(_row(0, n, 5e-7) for n in (-1.0, 0.0, 1.0)) + "\n"
    )
    out = list(digest_once(build_model(d), now=1100.0))
    assert "None=" not in out[0]


# --------------------------------------------------------------------------
# read_rows: complete-line discipline
# --------------------------------------------------------------------------


def _write_meta(d: Path, **over):
    meta = {
        "version": 2,
        "comments": ["test-recipe"],
        "columns": ["mag", "k_bg_volt", "sr1_X", "sr1_P"],
        "measurement_config": {
            "sr1": "a-b", "bias_voltage": 0.5, "bias_resistor": 1e8,
        },
        "type": "2D",
        "slow_params": ["mag"],
        "fast_params": ["k_bg_volt"],
        "slow_setpoints": [[0.0, 1.0, 2.0]],
        "fast_setpoints": [[-1.0, 0.0, 1.0]],
        "start_time": 1000.0,
    }
    meta.update(over)
    (d / "metadata.json").write_text(json.dumps(meta))


def _row(mag, n, x):
    return f"{mag}\t{n}\t{x}\t0.0"


def test_read_rows_drops_partial_trailing_line(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    _write_meta(d)
    # Two complete rows + a partial third (no trailing newline).
    (d / "data.tsv").write_text(
        _row(0, -1, 1e-6) + "\n" + _row(0, 0, 2e-6) + "\n" + "0\t1"
    )
    rows = read_rows(d, 4)
    assert rows.shape == (2, 4)


def test_read_rows_prefers_plain_then_gz(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    _write_meta(d)
    with gzip.open(d / "data.tsv.gz", "wt") as f:
        f.write(_row(0, -1, 1e-6) + "\n")
    assert read_rows(d, 4).shape == (1, 4)
    # Plain takes precedence (live file beats the finalized archive).
    (d / "data.tsv").write_text(_row(0, -1, 1e-6) + "\n" + _row(0, 0, 2e-6) + "\n")
    assert read_rows(d, 4).shape == (2, 4)


def test_run_complete_detection(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    _write_meta(d)
    (d / "data.tsv").write_text(_row(0, -1, 1e-6) + "\n")
    assert not run_complete(build_model(d))
    _write_meta(d, end_time=2000.0)
    assert run_complete(build_model(d))


# --------------------------------------------------------------------------
# digest: gain division correctness
# --------------------------------------------------------------------------


def test_digest_applies_gain_division(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    _write_meta(d)
    # One full slow row (3 fast pts) at constant X = 5e-7 V.
    # gain=1 (no sr1_gain), I_bias = 0.5/1e8 = 5 nA -> R = 5e-7 / 5e-9 = 100 Ω.
    lines = "\n".join(_row(0, n, 5e-7) for n in (-1.0, 0.0, 1.0)) + "\n"
    (d / "data.tsv").write_text(lines)
    out = list(digest_once(build_model(d), now=1100.0))
    assert len(out) == 1
    assert "row   0/3" in out[0]
    assert "sr1 R[med 100Ω" in out[0]


def test_digest_raw_skips_division(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    _write_meta(d)
    (d / "data.tsv").write_text("\n".join(_row(0, n, 5e-7) for n in (-1.0, 0.0, 1.0)) + "\n")
    out = list(digest_once(build_model(d), raw=True))
    assert "sr1 X[med 500nV" in out[0]


def test_digest_partial_row_flagged(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    _write_meta(d)
    # 1 full row + 2 of 3 in the next row.
    rows = [_row(0, n, 1e-6) for n in (-1.0, 0.0, 1.0)]
    rows += [_row(1, n, 1e-6) for n in (-1.0, 0.0)]
    (d / "data.tsv").write_text("\n".join(rows) + "\n")
    out = list(digest_once(build_model(d)))
    assert len(out) == 2
    assert "row   1/3 (partial 2/3)" in out[1]


def test_digest_b1c2_2d_smoke(model_117):
    # End-to-end on real archived data: 401 slow rows, current + R channels.
    out = list(digest_once(model_117))
    assert len(out) == 401
    assert "row   0/401" in out[0]
    assert "sr830_1 I[" in out[0]   # transimpedance -> current
    assert "sr830_2 R[" in out[0]   # voltage -> resistance


# --------------------------------------------------------------------------
# Full-scale (soft-clip) + gate-leakage guards
# --------------------------------------------------------------------------

CAPSTONE2_DATA = (
    REPO_ROOT / "hera/docs/notes/2026-07-17-QC0426-capstone-2/data"
)
QC0426_SESSION = (
    REPO_ROOT / "hera/docs/notes/2026-07-14-QC0426-session/data"
)


def _write_meta_fs(d: Path, *, sensitivity, columns=None, mc_extra=None,
                   **over):
    """`_write_meta` variant that carries a lock-in sensitivity in the sr1
    instrument snapshot (the full-scale source). ``sensitivity=None`` writes
    an unpopulated value, the None-care case."""
    meta = {
        "version": 2,
        "comments": ["test-recipe"],
        "columns": columns or ["mag", "k_bg_volt", "sr1_X", "sr1_P"],
        "measurement_config": {
            "sr1": "a-b", "bias_voltage": 0.5, "bias_resistor": 1e8,
            **(mc_extra or {}),
        },
        "instruments": {
            "sr1": {"snapshot": {"parameters": {
                "sensitivity": {"value": sensitivity, "unit": "V"},
            }}},
        },
        "type": "2D",
        "slow_params": ["mag"],
        "fast_params": ["k_bg_volt"],
        "slow_setpoints": [[0.0, 1.0, 2.0]],
        "fast_setpoints": [[-1.0, 0.0, 1.0]],
        "start_time": 1000.0,
    }
    meta.update(over)
    (d / "metadata.json").write_text(json.dumps(meta))


def test_build_model_resolves_full_scale(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    _write_meta_fs(d, sensitivity=5e-4)
    m = build_model(d)
    assert m.full_scale == {"sr1": 5e-4}


def test_full_scale_absent_when_sensitivity_none(tmp_path):
    # Some archives leave sensitivity unpopulated (like time_constant); the
    # check must skip, not fake a value.
    d = tmp_path / "run"
    d.mkdir()
    _write_meta_fs(d, sensitivity=None)
    m = build_model(d)
    assert m.full_scale == {}


def test_fs_token_and_clip_warning(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    # sensitivity 5e-4 V; X reaches 5.2e-4 -> fs 1.04, past the nominal rail.
    _write_meta_fs(d, sensitivity=5e-4)
    (d / "data.tsv").write_text(
        "\n".join(_row(0, n, 5.2e-4) for n in (-1.0, 0.0, 1.0)) + "\n"
    )
    out = list(digest_once(build_model(d), now=1100.0))
    assert "fs 1.04]" in out[0]
    assert "⚠ FS-CLIP sr1=1.04" in out[0]


def test_fs_high_below_rail(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    # fs 0.94: past the 0.90 headroom warn, below the 1.0 rail -> HIGH not CLIP.
    _write_meta_fs(d, sensitivity=5e-4)
    (d / "data.tsv").write_text(
        "\n".join(_row(0, n, 4.7e-4) for n in (-1.0, 0.0, 1.0)) + "\n"
    )
    out = list(digest_once(build_model(d), now=1100.0))
    assert "⚠ FS-HIGH sr1=0.94" in out[0]
    assert "FS-CLIP" not in out[0]


def test_fs_quiet_with_headroom(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    _write_meta_fs(d, sensitivity=5e-4)
    (d / "data.tsv").write_text(
        "\n".join(_row(0, n, 5e-5) for n in (-1.0, 0.0, 1.0)) + "\n"  # fs 0.10
    )
    out = list(digest_once(build_model(d), now=1100.0))
    assert "fs 0.10]" in out[0]
    assert "⚠" not in out[0]


def test_fs_warn_threshold_override(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    _write_meta_fs(d, sensitivity=5e-4)
    (d / "data.tsv").write_text(
        "\n".join(_row(0, n, 3e-4) for n in (-1.0, 0.0, 1.0)) + "\n"  # fs 0.60
    )
    assert "⚠" not in list(digest_once(build_model(d), now=1100.0))[0]
    out = list(digest_once(build_model(d, fs_warn=0.5), now=1100.0))
    assert "⚠ FS-HIGH sr1=0.60" in out[0]


def _leak_run(d, currents, *, columns=None, volt_col="k_bg_volt",
              curr_col="k_bg_curr"):
    """Write a single-leg run: the swept gate `volt_col` ramps 0 -> 2 V over
    len(currents) points, `curr_col` takes the given currents (amps). Baseline
    anchors to the least-biased (near-0 V) rows."""
    cols = columns or ["mag", volt_col, curr_col, "sr1_X", "sr1_P"]
    n = len(currents)
    volts = [round(i * 2.0 / (n - 1), 6) for i in range(n)]
    _write_meta_fs(d, sensitivity=5e-4, columns=cols,
                   fast_params=[volt_col], slow_params=["mag"],
                   fast_setpoints=[volts], slow_setpoints=[[0.0]])
    rows = [f"0\t{v}\t{c}\t5e-5\t0.0" for v, c in zip(volts, currents)]
    (d / "data.tsv").write_text("\n".join(rows) + "\n")


def test_current_cols_detected_and_leak_excess_warning(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    # Parked on a -100 pA Keithley offset floor, then a sustained super-linear
    # onset in the last 3 points: excess 150/250/400 pA over baseline.
    base = -100e-12
    currents = [base] * 17 + [base + 150e-12, base + 250e-12, base + 400e-12]
    _leak_run(d, currents)
    m = build_model(d)
    assert m.current_cols == [(2, "k_bg_curr")]
    out = list(digest_once(build_model(d), now=1100.0))
    joined = "\n".join(out)
    assert "k_bg I[" in joined                    # stats token shown
    assert "⚠ LEAK k_bg=Δ400pA" in joined         # peak excess (Δ), not absolute |I|


def test_offset_floor_does_not_fire(tmp_path):
    # The whole point of excess-over-baseline: a clean leg parked on a -100 pA
    # Keithley offset (|I| ~ 100 pA absolute) must NOT fire.
    d = tmp_path / "run"
    d.mkdir()
    _leak_run(d, [-100e-12] * 20)
    out = list(digest_once(build_model(d), now=1100.0))
    joined = "\n".join(out)
    assert "k_bg I[" in joined      # surfaced regardless
    assert "LEAK" not in joined     # but not flagged


def test_single_point_spike_does_not_fire(tmp_path):
    # One isolated point over threshold (a Keithley glitch) is not sustained:
    # no LEAK. The spike sits inside the baseline anchor window but the median
    # shrugs it off, so the baseline stays clean too.
    d = tmp_path / "run"
    d.mkdir()
    currents = [-100e-12] * 20
    currents[10] = -100e-12 + 2e-9    # lone +2 nA excess spike
    _leak_run(d, currents)
    out = list(digest_once(build_model(d), now=1100.0))
    assert "LEAK" not in "\n".join(out)


@pytest.mark.skipif(not (CAPSTONE2_DATA / "7").is_dir(),
                    reason="capstone-2 archive not present")
def test_archive_run7_flags_soft_clip():
    # The 2026-07-17 capstone fan railed sr1 & sr2 at ~1.09x full scale in its
    # high-B rows; the low-B rows have full headroom.
    m = build_model(CAPSTONE2_DATA / "7")
    assert set(m.full_scale) == {"sr0", "sr1", "sr2", "sr3"}
    out = list(digest_once(m))
    assert "⚠" not in out[0]                         # low-B: quiet
    last = out[-1]                                    # B = 8 T corner
    assert "FS-CLIP" in last and "sr1=1.09" in last and "sr2=1.09" in last
    # sr0 (current) and sr3 never rail.
    assert "sr0=" not in last and "sr3=" not in last
    # gate currents surfaced, no leakage at the 1 nA default.
    assert "k_2400_bg I[" in last and "LEAK" not in last


@pytest.mark.skipif(not (CAPSTONE2_DATA / "0").is_dir(),
                    reason="capstone-2 archive not present")
def test_archive_gateC_surfaces_currents_quietly():
    # A gate-current-sanity-check run: Keithley currents visible, ~100 pA,
    # below the 1 nA leak default -> shown but not flagged.
    out = list(digest_once(build_model(CAPSTONE2_DATA / "0")))
    assert "k_2400_tg I[" in out[0] and "k_2400_bg I[" in out[0]
    assert all("LEAK" not in ln for ln in out)


def _tg_window(line):
    """(lo, hi) of the k_2400_tg_volt fast-window in a digest line."""
    m = re.search(r"k_2400_tg_volt\[([-+0-9.eE]+)→([-+0-9.eE]+)\]", line)
    assert m, f"no tg fast-window in: {line}"
    return float(m.group(1)), float(m.group(2))


@pytest.mark.skipif(not (QC0426_SESSION / "0").is_dir(),
                    reason="2026-07-14 QC0426 session archive not present")
def test_archive_qc0426_leakage_excess_over_baseline():
    # The runs that motivated the excess-over-baseline rework. Gate-C legs:
    # TG (+18 pA baseline) leaks super-linearly; BG sits on a -100 pA offset
    # floor and never truly leaks. Absolute |I| couldn't separate them; excess
    # over baseline at 100 pA (sustained) does.
    #
    # run 0: TG pushed 0 -> +7 V; excess crosses 100 pA near +4.45 V.
    out0 = list(digest_once(build_model(QC0426_SESSION / "0")))
    leaks0 = [l for l in out0 if "LEAK" in l]
    assert leaks0, "run 0 must warn on the TG leak"
    assert "k_2400_tg=" in leaks0[0] and "k_2400_bg=" not in leaks0[0]
    lo, hi = _tg_window(leaks0[0])          # onset chunk brackets +4.45 V
    assert lo <= 4.45 <= hi

    # run 1: TG pushed 0 -> -6 V; excess crosses near -4.27 V.
    out1 = list(digest_once(build_model(QC0426_SESSION / "1")))
    leaks1 = [l for l in out1 if "LEAK" in l]
    assert leaks1, "run 1 must warn on the TG leak"
    assert "k_2400_tg=" in leaks1[0] and "k_2400_bg=" not in leaks1[0]
    lo, hi = _tg_window(leaks1[0])
    assert lo <= -4.27 <= hi

    # runs 2 & 3: BG legs on the offset floor — never warn.
    for r in ("2", "3"):
        out = list(digest_once(build_model(QC0426_SESSION / r)))
        assert all("LEAK" not in l for l in out), f"run {r} must stay quiet"


def test_archive_b1c2_full_scale_unavailable(model_119):
    # b1c2 archive carries sensitivity=None -> header says so, no fs tokens.
    hdr = header_lines(model_119)
    assert any("full-scale: unavailable" in ln for ln in hdr)
    out = list(digest_once(model_119))
    assert all("fs " not in ln for ln in out)


# --------------------------------------------------------------------------
# digest: 1D chunking
# --------------------------------------------------------------------------


def test_digest_1d_chunks(model_119):
    out = list(digest_once(model_119, every=25))
    # 101 rows / 25 -> 4 full chunks + 1 remainder = 5 lines.
    assert len(out) == 5
    assert out[0].startswith("rows 0–24")
    assert out[-1].startswith("rows 100–100")


# --------------------------------------------------------------------------
# watch loop: grows row-by-row with injected clock
# --------------------------------------------------------------------------


class _Clock:
    def __init__(self, start=1000.0):
        self.t = start

    def now(self):
        return self.t


def test_watch_emits_one_line_per_slow_row(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    _write_meta(d)  # 3 slow rows × 3 fast pts

    all_rows = [_row(s, n, 1e-6) for s in (0, 1, 2) for n in (-1.0, 0.0, 1.0)]
    state = {"written": 3}  # start mid-run: 1 slow row already on disk
    (d / "data.tsv").write_text("\n".join(all_rows[:3]) + "\n")

    clock = _Clock()

    def fake_sleep(_):
        # Each tick: advance clock, append the next slow row (or finalize).
        clock.t += 60
        w = state["written"]
        if w < len(all_rows):
            chunk = all_rows[w:w + 3]
            with (d / "data.tsv").open("a") as f:
                f.write("\n".join(chunk) + "\n")
            state["written"] = w + 3
        else:
            _write_meta(d, end_time=clock.t)  # mark complete

    out = []
    rc = watch(build_model(d), poll=0.0, timeout=10_000, emit=out.append,
               now_fn=clock.now, sleep_fn=fake_sleep)
    assert rc == 0
    row_lines = [l for l in out if l.startswith("row ")]
    assert [l.split()[1] for l in row_lines] == ["0/3", "1/3", "2/3"]
    assert any(l.startswith("# complete: 9/9 rows") for l in out)


def test_watch_timeout(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    _write_meta(d)
    (d / "data.tsv").write_text("\n".join(_row(0, n, 1e-6) for n in (-1.0, 0.0, 1.0)) + "\n")

    clock = _Clock()

    def fake_sleep(_):
        clock.t += 100  # never appends, never completes

    out = []
    rc = watch(build_model(d), poll=0.0, timeout=50, emit=out.append,
               now_fn=clock.now, sleep_fn=fake_sleep)
    assert rc == 2
    assert any("timeout" in l for l in out)


def test_header_lines_raw_tag(model_117):
    assert "RAW" not in "\n".join(header_lines(model_117))
    assert "RAW" in "\n".join(header_lines(model_117, raw=True))


def test_watch_follow_no_deadline(tmp_path):
    # timeout=None must never self-exit; it follows the run to completion
    # even past where a 570s deadline would have fired.
    d = tmp_path / "run"
    d.mkdir()
    _write_meta(d)
    (d / "data.tsv").write_text("\n".join(_row(0, n, 1e-6) for n in (-1.0, 0.0, 1.0)) + "\n")

    clock = _Clock()
    state = {"ticks": 0}

    def fake_sleep(_):
        clock.t += 10_000  # each tick blows way past any 570s deadline
        state["ticks"] += 1
        if state["ticks"] >= 3:
            _write_meta(d, end_time=clock.t)  # only completes after a while

    out = []
    rc = watch(build_model(d), poll=0.0, timeout=None, emit=out.append,
               now_fn=clock.now, sleep_fn=fake_sleep)
    assert rc == 0  # completed, did not time out
    assert not any("timeout" in l for l in out)
    assert any(l.startswith("# complete") for l in out)


# --------------------------------------------------------------------------
# arm-before-run: run_dir_ready / wait_for_run / resolve_next_run
# --------------------------------------------------------------------------


def test_run_dir_ready(tmp_path):
    d = tmp_path / "run"
    assert not run_dir_ready(d)        # missing dir
    d.mkdir()
    assert not run_dir_ready(d)        # dir, no metadata yet
    _write_meta(d)
    assert run_dir_ready(d)            # modellable


def test_resolve_next_run(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    assert resolve_next_run(data) == data / "0"   # empty -> 0
    for name in ("117", "118", "119", "notes"):
        (data / name).mkdir()
    # ignores non-integer dirs, picks max(existing)+1
    assert resolve_next_run(data) == data / "120"


def test_resolve_next_run_missing_dir(tmp_path):
    assert resolve_next_run(tmp_path / "nope") == tmp_path / "nope" / "0"


def test_wait_for_run_already_present(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    _write_meta(d)
    slept = []
    assert wait_for_run(d, sleep_fn=slept.append)
    assert slept == []  # returns immediately, no polling


def test_wait_for_run_appears_after_polls(tmp_path):
    d = tmp_path / "run"
    clock = _Clock()
    state = {"ticks": 0}

    def fake_sleep(_):
        clock.t += 5
        state["ticks"] += 1
        if state["ticks"] == 2:        # dir materializes on the 2nd poll
            d.mkdir()
            _write_meta(d)

    assert wait_for_run(d, timeout=1000, poll=5.0,
                        now_fn=clock.now, sleep_fn=fake_sleep)
    assert state["ticks"] == 2


def test_wait_for_run_times_out(tmp_path):
    d = tmp_path / "run"  # never created
    clock = _Clock()

    def fake_sleep(_):
        clock.t += 100

    assert not wait_for_run(d, timeout=50, poll=5.0,
                            now_fn=clock.now, sleep_fn=fake_sleep)


def test_wait_for_run_indefinite_until_appears(tmp_path):
    # timeout<=0 waits indefinitely; still returns once the dir appears.
    d = tmp_path / "run"
    state = {"ticks": 0}

    def fake_sleep(_):
        state["ticks"] += 1
        if state["ticks"] == 4:
            d.mkdir()
            _write_meta(d)

    assert wait_for_run(d, timeout=0, poll=0.0, sleep_fn=fake_sleep)
    assert state["ticks"] == 4


# --------------------------------------------------------------------------
# --next robustness: ready_run_ids / wait_for_next_run
# --------------------------------------------------------------------------


def _make_run(data: Path, fid: int):
    d = data / str(fid)
    d.mkdir(parents=True)
    _write_meta(d)
    return d


def test_ready_run_ids_only_counts_modellable(tmp_path):
    data = tmp_path / "data"
    _make_run(data, 0)
    _make_run(data, 2)
    (data / "1").mkdir()            # dir exists but no metadata yet -> not ready
    (data / "notes").mkdir()       # non-integer -> ignored
    assert ready_run_ids(data) == {0, 2}


def test_wait_for_next_run_missing_data_dir(tmp_path):
    # No data/ dir yet: baseline is empty, the first run to appear is latched.
    data = tmp_path / "data"
    state = {"ticks": 0}

    def fake_sleep(_):
        state["ticks"] += 1
        if state["ticks"] == 2:
            _make_run(data, 0)

    got = wait_for_next_run(data, timeout=1000, poll=0.0, sleep_fn=fake_sleep)
    assert got == data / "0"


def test_wait_for_next_run_latches_second_run(tmp_path):
    # The regression: a prior run (0) already exists; arming must latch the
    # genuinely new run (1), not sit forever. Demonstrates the 2nd+-run case.
    data = tmp_path / "data"
    _make_run(data, 0)             # first run already done
    state = {"ticks": 0}

    def fake_sleep(_):
        state["ticks"] += 1
        if state["ticks"] == 3:
            _make_run(data, 1)     # the operator/agent starts run 1

    got = wait_for_next_run(data, timeout=1000, poll=0.0, sleep_fn=fake_sleep)
    assert got == data / "1"


def test_wait_for_next_run_handles_id_gap(tmp_path):
    # Gap in ids ({0,1,3}, run 2 deleted): sweep allocates the lowest free id
    # (2), which a frozen max+1 prediction (resolve_next_run -> 4) would miss.
    data = tmp_path / "data"
    for fid in (0, 1, 3):
        _make_run(data, fid)
    assert resolve_next_run(data) == data / "4"   # the brittle prediction
    state = {"ticks": 0}

    def fake_sleep(_):
        state["ticks"] += 1
        if state["ticks"] == 2:
            _make_run(data, 2)     # sweep fills the gap

    got = wait_for_next_run(data, timeout=1000, poll=0.0, sleep_fn=fake_sleep)
    assert got == data / "2"       # latched the real run, not the prediction


def test_wait_for_next_run_times_out(tmp_path):
    # No new run ever appears -> None (the CLI turns this into exit 2 + a ping).
    data = tmp_path / "data"
    _make_run(data, 0)
    clock = _Clock()

    def fake_sleep(_):
        clock.t += 100

    assert wait_for_next_run(data, timeout=50, poll=5.0,
                             now_fn=clock.now, sleep_fn=fake_sleep) is None


# --------------------------------------------------------------------------
# dir-or-metadata latch: run_dir_started / existing_run_ids / wait_for_metadata
# --------------------------------------------------------------------------


def test_run_dir_started_on_bare_dir(tmp_path):
    d = tmp_path / "run"
    assert not run_dir_started(d)      # missing
    d.mkdir()
    assert run_dir_started(d)          # dir exists, even without metadata
    assert not run_dir_ready(d)        # ...but not yet modellable


def test_existing_run_ids_counts_dirs_without_metadata(tmp_path):
    # The dir-existence analogue of ready_run_ids: counts a dir the instant it's
    # mkdir'd, before metadata.json lands (run 1 here). ready_run_ids does not.
    data = tmp_path / "data"
    _make_run(data, 0)
    (data / "1").mkdir(parents=True)   # dir created, metadata not written yet
    (data / "notes").mkdir()           # non-integer -> ignored
    assert existing_run_ids(data) == {0, 1}
    assert ready_run_ids(data) == {0}


def test_wait_for_metadata_settles_after_polls(tmp_path):
    d = tmp_path / "run"
    d.mkdir()                          # dir present, metadata not yet
    state = {"ticks": 0}

    def fake_sleep(_):
        state["ticks"] += 1
        if state["ticks"] == 2:
            _write_meta(d)

    assert wait_for_metadata(d, settle=1000, poll=0.0, sleep_fn=fake_sleep)
    assert state["ticks"] == 2


def test_wait_for_metadata_times_out(tmp_path):
    d = tmp_path / "run"
    d.mkdir()                          # dir present but metadata never lands
    clock = _Clock()

    def fake_sleep(_):
        clock.t += 100

    warned = []
    assert not wait_for_metadata(d, settle=50, poll=5.0, now_fn=clock.now,
                                 sleep_fn=fake_sleep, emit=warned.append)
    assert any("metadata.json did not" in m for m in warned)


def test_wait_for_next_run_latches_dir_then_settles_metadata(tmp_path):
    # The new behavior: a new run dir appears (mkdir) one poll before its
    # metadata.json is written. wait_for_next_run latches the dir immediately,
    # then settles for metadata before returning the path.
    data = tmp_path / "data"
    _make_run(data, 0)                 # prior run
    d1 = data / "1"
    state = {"ticks": 0}

    def fake_sleep(_):
        state["ticks"] += 1
        if state["ticks"] == 2:
            d1.mkdir()                 # sweep creates the dir
        elif state["ticks"] == 3:
            _write_meta(d1)            # metadata lands a poll later

    got = wait_for_next_run(data, timeout=1000, poll=0.0, sleep_fn=fake_sleep)
    assert got == d1
    assert run_dir_ready(d1)           # returned only once modellable


def test_wait_for_run_latches_dir_then_settles_metadata(tmp_path):
    d = tmp_path / "run"
    state = {"ticks": 0}

    def fake_sleep(_):
        state["ticks"] += 1
        if state["ticks"] == 1:
            d.mkdir()                  # dir appears first
        elif state["ticks"] == 2:
            _write_meta(d)             # metadata a poll later

    assert wait_for_run(d, timeout=1000, poll=0.0, sleep_fn=fake_sleep)
    assert run_dir_ready(d)
