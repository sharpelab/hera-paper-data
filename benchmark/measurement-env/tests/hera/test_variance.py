"""Tests for the HERA replay-variance experiment runner (hera.variance).

Synthetic campaigns + a scripted fake harness cover the R8 surface:
cutoff/allowlist enforcement, source immutability, leak-check fail-closed
behavior, sanitization, independent workspace hashes, robust parsing,
statistics, resume behavior, deterministic summaries, and CLI smoke paths.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import pytest

from hera import variance
from hera.variance import (
    LeakError,
    ManifestError,
    VarianceError,
    categorical_stats,
    canonical_tool_signature,
    cmd_inspect,
    crop_nb,
    load_manifest,
    main,
    materialize,
    numeric_stats,
    parse_tool_call,
    parse_verdict,
    run_experiments,
    sanitize_nb,
    scan_leaks,
    summarize,
    truth_metrics,
    validate_manifest,
    workspace_hash,
)

# ---------------------------------------------------------------------------
# Synthetic campaign fixtures
# ---------------------------------------------------------------------------


def _nb(cells: list[dict]) -> dict:
    return {"cells": cells, "metadata": {}, "nbformat": 4, "nbformat_minor": 5}


def _code(src: str, streams: list[str] | None = None) -> dict:
    out = []
    for s in streams or []:
        out.append({"output_type": "stream", "name": "stdout", "text": [s]})
    return {"cell_type": "code", "source": [src], "outputs": out}


def _md(src: str) -> dict:
    return {"cell_type": "markdown", "source": [src]}


def make_synthetic_campaign(tmp_path: Path) -> Path:
    root = tmp_path / "20260620-QC0426"
    root.mkdir(parents=True)

    measure = _nb(
        [
            _md("# setup"),
            _code("import os\n"),
            _md("## run 0 gatemap"),
            _code("s.megasweep(k_2400(0, 3, 101), sr0_X)", ["done: map 101x101"]),
            _md("## run 1 spot check"),
            _code("s.megasweep(mag.field(0.1, 2.0, 501), sr0_X)",
                  ["done: spot check"]),
            _md("## run 2 fan (POST-FRONTIER — must be cut)"),
            _code("s.megasweep(mag.field(8.0, 0.77, 141), k_2400(-3.5, -0.5, 101))",
                  ["fan done"]),
            _md("# STACKING CALL — verdict (must never be visible)"),
        ]
    )
    (root / "20260620_measure.ipynb").write_text(json.dumps(measure))

    ana = _nb(
        [
            _md("## runs 0-1 read"),
            _code("fft = sdh_fft(run(1))", ["peak 35.2 T"]),
            _md("**Read — clean single-tone ABC is disfavored.**"),
            _md("## run 2 fan read (POST-FRONTIER)"),
            _code("fan_fft = sdh_fft(run(2))", ["F_dom/F_L = 0.54  (0.50 => 2 FS / ABA)"]),
            _md("## STACKING CALL — QC0426 is ABA"),
        ]
    )
    (root / "20260620_ana.ipynb").write_text(json.dumps(ana))

    for did, tsv in [(0, "a\tb\n1\t2\n"), (1, "a\tb\n3\t4\n"), (2, "a\tb\n5\t6\n")]:
        d = root / "data" / str(did)
        d.mkdir(parents=True)
        (d / "metadata.json").write_text(json.dumps({"run": did, "fn": "megasweep"}))
        (d / "plot.png").write_bytes(b"\x89PNG fake")
        (d / "data.tsv").write_text(tsv)

    (root / "device_card.md").write_text("# Device\nTG fast, BG slow.\n")
    (root / "rig_card.md").write_text("# Rig\nVTI, 8 T cap.\n")
    (root / "hera_session.md").write_text(
        "# Brief\nCampaign goal: determine the stacking order of QC0426: "
        "ABA (Bernal) vs ABC (rhombohedral).\n"
    )
    (root / "session_notes.md").write_text(
        "# Session notes\n**STACKING CALL — QC0426 is ABA.**\n"
    )
    (root / "hera_scratch").mkdir()
    (root / "hera_scratch" / "verdict.txt").write_text("ABA ABA ABA\n")
    return root


def make_synthetic_manifest(tmp_path: Path, root: Path) -> Path:
    doc = {
        "version": 1,
        "experiment_id": "test-variance",
        "harness": {"kind": "fake", "script": []},
        "campaigns": [
            {
                "id": "20260620-qc0426",
                "trial": 1,
                "source": str(root),
                "ground_truth": "ABA",
                "original_verdict": "ABA (strong)",
                "fidelity": "filesystem-only",
                "experiments": {
                    "tool-call": {
                        "measure_notebook": "20260620_measure.ipynb",
                        "cut_index": 5,
                        "analysis_notebook": "20260620_ana.ipynb",
                        "analysis_cut_index": 2,
                        "data_runs": [0, 1],
                        "include": ["device_card.md", "rig_card.md",
                                    "hera_session.md"],
                        "leak_terms": ["STACKING CALL", "Primary goal met",
                                       "QC0426 is"],
                        "samples": 2,
                    },
                    "final-analysis": {
                        "measure_notebook": "20260620_measure.ipynb",
                        "analysis_notebook": "20260620_ana.ipynb",
                        "data_runs": [0, 1, 2],
                        "include": ["device_card.md", "rig_card.md",
                                    "hera_session.md"],
                        "sanitize": True,
                        "leak_terms": ["ABA", "ABC", "STACKING CALL"],
                        "allowed_patterns": [r"ABA \(Bernal\) vs ABC \(rhombohedral\)"],
                        "allowed_in": ["hera_session.md"],
                        "samples": 2,
                    },
                },
            }
        ],
    }
    path = tmp_path / "manifest.yaml"
    path.write_text(
        __import__("yaml").safe_dump(doc, sort_keys=False), encoding="utf-8"
    )
    return path


@pytest.fixture
def syn(tmp_path):
    root = make_synthetic_campaign(tmp_path)
    manifest = make_synthetic_manifest(tmp_path, root)
    return root, manifest


# ---------------------------------------------------------------------------
# Manifest validation
# ---------------------------------------------------------------------------


class TestManifestValidation:
    def test_valid_manifest_loads(self, syn):
        root, mpath = syn
        doc = load_manifest(mpath)
        assert doc["experiment_id"] == "test-variance"
        assert doc["campaigns"][0]["id"] == "20260620-qc0426"

    def test_missing_required_key(self, tmp_path):
        with pytest.raises(ManifestError):
            validate_manifest({"version": 1, "experiment_id": "x"})

    def test_bad_ground_truth(self, syn):
        root, mpath = syn
        doc = load_manifest(mpath)
        doc["campaigns"][0]["ground_truth"] = "ABAC"
        with pytest.raises(ManifestError):
            validate_manifest(doc)

    def test_custom_ground_truth_support(self, syn):
        root, mpath = syn
        doc = load_manifest(mpath)
        final = doc["campaigns"][0]["experiments"]["final-analysis"]
        final["verdict_support"] = [
            "SUPERCONDUCTOR", "FAILED_SC", "NOT_SC", "CANNOT_TELL"
        ]
        final["analysis_task"] = "Determine whether the device superconducts."
        doc["campaigns"][0]["ground_truth"] = "SUPERCONDUCTOR"
        validate_manifest(doc)

    def test_bad_experiment_kind(self, syn):
        root, mpath = syn
        doc = load_manifest(mpath)
        doc["campaigns"][0]["experiments"]["bogus"] = {}
        with pytest.raises(ManifestError):
            validate_manifest(doc)

    def test_missing_source_dir(self, syn):
        root, mpath = syn
        doc = load_manifest(mpath)
        doc["campaigns"][0]["source"] = str(root / "nope")
        with pytest.raises(ManifestError):
            validate_manifest(doc)


# ---------------------------------------------------------------------------
# Materialization — cutoffs, allowlist, immutability, leaks
# ---------------------------------------------------------------------------


class TestMaterialization:
    def _exp(self, doc, kind):
        return doc["campaigns"][0], kind, dict(doc["campaigns"][0]["experiments"][kind])

    def test_crop_and_allowlist(self, syn, tmp_path):
        root, mpath = syn
        doc = load_manifest(mpath)
        camp, kind, cfg = self._exp(doc, "tool-call")
        dest = tmp_path / "ws"
        m = materialize(camp, kind, cfg, dest)

        nb = json.loads((dest / "20260620_measure.ipynb").read_text())
        assert len(nb["cells"]) == 6  # cells 0..5 inclusive
        assert "fan" not in json.dumps(nb["cells"]).lower()
        ana = json.loads((dest / "20260620_ana.ipynb").read_text())
        assert len(ana["cells"]) == 3
        assert (dest / "data" / "0").is_dir()
        assert (dest / "data" / "1").is_dir()
        assert not (dest / "data" / "2").exists()  # not in allowlist
        assert not (dest / "session_notes.md").exists()
        assert not (dest / "hera_scratch").exists()
        assert "session_notes.md" in m["excluded_present"]
        assert m["leak_scan"]["status"] == "pass"

    def test_source_immutability(self, syn, tmp_path):
        root, mpath = syn
        doc = load_manifest(mpath)
        camp, kind, cfg = self._exp(doc, "tool-call")
        before = {}
        for p in sorted(root.rglob("*")):
            if p.is_file():
                st = p.stat()
                before[str(p)] = (st.st_size, st.st_mtime_ns)
        materialize(camp, kind, cfg, tmp_path / "ws")
        after = {}
        for p in sorted(root.rglob("*")):
            if p.is_file():
                st = p.stat()
                after[str(p)] = (st.st_size, st.st_mtime_ns)
        assert before == after

    def test_leak_check_fails_closed(self, syn, tmp_path):
        root, mpath = syn
        doc = load_manifest(mpath)
        camp, kind, cfg = self._exp(doc, "tool-call")
        # Extend the crop to swallow the verdict cell (index 8)
        cfg = dict(cfg, cut_index=8)
        dest = tmp_path / "ws"
        with pytest.raises(LeakError):
            materialize(camp, kind, cfg, dest)
        assert (dest.parent / "LEAK-SCAN-FAILED.txt").exists()

    def test_missing_include_fails(self, syn, tmp_path):
        root, mpath = syn
        doc = load_manifest(mpath)
        camp, kind, cfg = self._exp(doc, "tool-call")
        cfg = dict(cfg, include=["nonexistent.md"])
        with pytest.raises(VarianceError):
            materialize(camp, kind, cfg, tmp_path / "ws")

    def test_include_line_sanitization(self, syn, tmp_path):
        root, mpath = syn
        doc = load_manifest(mpath)
        # plant verdict lines in the synthetic device card
        (root / "device_card.md").write_text(
            "# Device\nTG fast.\n## Stacking determination: QC0426 = ABA (Bernal), strong\n"
        )
        camp, kind, cfg = self._exp(doc, "final-analysis")
        dest = tmp_path / "ws"
        m = materialize(camp, kind, cfg, dest)
        card = (dest / "device_card.md").read_text()
        assert "QC0426 = ABA" not in card
        assert "removed by hera-variance sanitizer" in card
        assert "TG fast" in card
        # brief goal line survives via allowed_patterns
        brief = (dest / "hera_session.md").read_text()
        assert "ABA (Bernal) vs ABC (rhombohedral)" in brief
        assert m["include_sanitize_report"]["device_card.md"] == 1
        # tool-call frontier also strips verdict-contract lines from cards
        (root / "device_card.md").write_text(
            "# Device\nTG fast.\n## STACKING CALL — QC0426 is ABA (strong)\n"
        )
        camp2, kind2, cfg2 = self._exp(doc, "tool-call")
        dest2 = tmp_path / "ws2"
        materialize(camp2, kind2, cfg2, dest2)
        card2 = (dest2 / "device_card.md").read_text()
        assert "STACKING CALL" not in card2
        assert "removed by hera-variance sanitizer" in card2

    def test_final_analysis_sanitizes_data_metadata_strings(self, syn, tmp_path):
        root, mpath = syn
        source_metadata = root / "data" / "1" / "metadata.json"
        source_metadata.write_text(json.dumps({
            "run": 1,
            "comment": "firming fan for ABA chain region",
            "nested": ["clean acquisition note", "ABC excluded by final fit"],
            "calibration": {"scale": 1.25},
        }))
        doc = load_manifest(mpath)
        camp, kind, cfg = self._exp(doc, "final-analysis")
        dest = tmp_path / "ws"
        manifest = materialize(camp, kind, cfg, dest)

        copied = json.loads((dest / "data" / "1" / "metadata.json").read_text())
        assert copied["run"] == 1
        assert copied["calibration"]["scale"] == 1.25
        assert copied["nested"][0] == "clean acquisition note"
        assert "ABA" not in copied["comment"]
        assert "ABC" not in copied["nested"][1]
        assert manifest["data_sanitize_report"]["data/1/metadata.json"] == 2
        # The immutable source copy is never rewritten.
        assert "ABA chain region" in source_metadata.read_text()

    def test_workspace_hash_byte_identical(self, syn, tmp_path):
        root, mpath = syn
        doc = load_manifest(mpath)
        camp, kind, cfg = self._exp(doc, "tool-call")
        a = materialize(camp, kind, cfg, tmp_path / "a")
        b = materialize(camp, kind, cfg, tmp_path / "b")
        assert a["workspace_sha256"] == b["workspace_sha256"]
        assert (tmp_path / "a") != (tmp_path / "b")
        # Distinct experiments -> distinct hashes
        camp2, kind2, cfg2 = self._exp(doc, "final-analysis")
        c = materialize(camp2, kind2, cfg2, tmp_path / "c")
        assert c["workspace_sha256"] != a["workspace_sha256"]

    def test_final_analysis_sanitize(self, syn, tmp_path):
        root, mpath = syn
        doc = load_manifest(mpath)
        camp, kind, cfg = self._exp(doc, "final-analysis")
        dest = tmp_path / "ws"
        materialize(camp, kind, cfg, dest)

        ana = json.loads((dest / "20260620_ana.ipynb").read_text())
        kinds = [c["cell_type"] for c in ana["cells"]]
        assert "markdown" not in kinds  # narrative dropped
        # code cell whose output leaked ABA -> placeholder output, source kept
        fan_cell = [c for c in ana["cells"]
                    if "fan_fft" in "".join(c.get("source", []))][0]
        out_text = "".join(fan_cell["outputs"][0]["text"])
        assert "removed by hera-variance sanitizer" in out_text
        assert "ABA" not in out_text
        # clean code cell output preserved
        fft_cell = [c for c in ana["cells"]
                    if "sdh_fft(run(1))" in "".join(c.get("source", []))][0]
        assert "35.2" in "".join(fft_cell["outputs"][0]["text"])

        measure = json.loads((dest / "20260620_measure.ipynb").read_text())
        kinds = [c["cell_type"] for c in measure["cells"]]
        assert "markdown" not in kinds
        # brief's question line allowed; no other ABA/ABC anywhere visible
        scan = scan_leaks(dest, ["ABA", "ABC"],
                          allowed_patterns=[r"ABA \(Bernal\) vs ABC \(rhombohedral\)"],
                          allowed_in=["hera_session.md"])
        assert scan["hits"] == [], scan["hits"]

    def test_scan_leaks_bare_terms(self, tmp_path):
        d = tmp_path / "s"
        d.mkdir()
        (d / "x.md").write_text("no leak")
        (d / "y.md").write_text("the verdict is ABA today")
        scan = scan_leaks(d, ["ABA"])
        assert scan["status"] == "FAIL"
        assert len(scan["hits"]) == 1
        assert scan["hits"][0]["file"] == "y.md"
        assert scan["hits"][0]["count"] == 1


# ---------------------------------------------------------------------------
# Sanitizer unit behavior
# ---------------------------------------------------------------------------


class TestSanitizeNb:
    def test_drops_markdown_and_strips_lines(self):
        nb = _nb(
            [
                _md("narrative with ABA inside"),
                _code("x = 1  # ABA conclusion\nprint(x)\n", ["ABA confirmed"]),
                _code("y = 2\nprint(y)\n", ["2"]),
            ]
        )
        out, report = sanitize_nb(nb, ["ABA"])
        assert len(out["cells"]) == 2
        assert all(c["cell_type"] == "code" for c in out["cells"])
        lines = out["cells"][0]["source"]
        assert "removed by hera-variance sanitizer" in lines[0]
        assert "x = 1" not in lines[0]
        assert "print(x)" in lines[1]
        assert "removed by hera-variance sanitizer" in out["cells"][0]["outputs"][0]["text"][0]
        assert out["cells"][1]["outputs"][0]["text"] == ["2"]
        assert report["0"] == {"action": "dropped-markdown"}
        assert report["1"]["lines_removed"] == 1
        assert report["1"]["outputs_removed"] == 1


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


class TestParsers:
    def test_tool_call_envelope(self):
        text = '```json\n{"callable": "s.megasweep", "axes": [{"name": "mag.field", "start": 8.0, "stop": 0.77, "points": 141}], "delays": {"fast": 0.05, "slow": 1.2}, "kwargs": {}, "rationale": "fan"}\n```'
        parsed, err = parse_tool_call(text)
        assert err is None
        assert parsed["callable"] == "s.megasweep"
        assert parsed["parse_mode"] == "envelope"
        assert parsed["axes"][0]["points"] == 141

    def test_tool_call_fallback_single_call(self):
        text = "Next I would land s.megasweep(mag.field(8.0, 0.77, 141), fast=0.05, slow=1.2)."
        parsed, err = parse_tool_call(text)
        assert err is None
        assert parsed["callable"] == "s.megasweep"
        assert parsed["parse_mode"] == "fallback-single-call"
        assert parsed["kwargs"] == {"fast": 0.05, "slow": 1.2}
        assert parsed["positionals"] == ["mag.field(8.0, 0.77, 141)"]

    def test_tool_call_malformed(self):
        parsed, err = parse_tool_call("I do not know what to do next.")
        assert parsed is None
        assert "no JSON envelope" in err

    def test_tool_call_tuple_syntax_normalized(self):
        # Model emitted Python tuple syntax inside the JSON envelope
        text = ('```json\n{"callable": "s.multimegasweep", "axes": '
                '[{"name": "gate_pair", "points": [(-1.5, -4.3), (-1.5, -3.2)]}, '
                '{"name": "magnet.field", "start": 8.0, "stop": 2.0, "points": 81}], '
                '"delays": {}, "kwargs": {}}\n```')
        parsed, err = parse_tool_call(text)
        assert err is None
        assert parsed["parse_mode"] == "envelope"
        assert "normalized" in parsed["parse_note"]
        assert parsed["axes"][0]["points"] == [[-1.5, -4.3], [-1.5, -3.2]]
        assert parsed["callable"] == "s.multimegasweep"

    def test_tool_call_missing_closing_braces_repaired(self):
        text = (
            '```json\n{"callable": "s.multimegasweep", "axes": [], '
            '"delays": {}, "kwargs": {"nested": {"value": 1}\n```'
        )
        parsed, err = parse_tool_call(text)
        assert err is None
        assert parsed["callable"] == "s.multimegasweep"
        assert "closing JSON delimiters" in parsed["parse_note"]

    def test_verdict_envelope(self):
        text = '```json\n{"verdict": "ABA", "confidence": "HIGH", "evidence": ["e1"], "summary": "s"}\n```'
        parsed, err = parse_verdict(text)
        assert err is None
        assert parsed["verdict"] == "ABA"
        assert parsed["confidence"] == "HIGH"

    def test_custom_verdict_support_and_claims(self):
        support = ["SUPERCONDUCTOR", "FAILED_SC", "NOT_SC", "CANNOT_TELL"]
        text = json.dumps({
            "verdict": "SUPERCONDUCTOR",
            "confidence": "HIGH",
            "claims": [{"claim": "finite critical current", "evidence": ["run 5"]}],
        })
        parsed, err = parse_verdict(text, support)
        assert err is None
        assert parsed["verdict"] == "SUPERCONDUCTOR"
        assert parsed["claims"][0]["claim"] == "finite critical current"

    def test_verdict_bad_confidence(self):
        parsed, err = parse_verdict('{"verdict": "ABA", "confidence": "SURE"}')
        assert parsed is None
        assert "confidence" in err

    def test_verdict_fallback_text(self):
        parsed, err = parse_verdict("My verdict: ABA, because of the fan.")
        assert err is None
        assert parsed["verdict"] == "ABA"
        assert parsed["parse_mode"] == "fallback-text"

    def test_verdict_ambiguous(self):
        parsed, err = parse_verdict("verdict ABA or verdict ABC? unclear")
        assert parsed is None
        assert "ambiguous" in err

    def test_verdict_malformed(self):
        parsed, err = parse_verdict("nothing here")
        assert parsed is None


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


class TestStats:
    def test_categorical_entropy(self):
        s = categorical_stats(["a", "a", "b", "b"])
        assert s["n"] == 4 and s["k"] == 2
        assert s["entropy_nats"] == pytest.approx(math.log(2))
        assert s["entropy_normalized"] == pytest.approx(1.0)

    def test_categorical_single_bin(self):
        s = categorical_stats(["x", "x"])
        assert s["entropy_nats"] == 0.0
        assert s["entropy_normalized"] == 0.0
        assert s["k"] == 1

    def test_categorical_empty(self):
        s = categorical_stats([])
        assert s["n"] == 0 and s["entropy_nats"] == 0.0

    def test_numeric_stats(self):
        s = numeric_stats([1.0, 2.0, 3.0, 4.0])
        assert s["n"] == 4
        assert s["variance_ddof1"] == pytest.approx(5 / 3)
        assert s["median"] == pytest.approx(2.5)
        assert s["iqr"] == pytest.approx(1.5)
        assert s["min"] == 1.0 and s["max"] == 4.0

    def test_truth_metrics(self):
        m = truth_metrics({"ABA": 3, "ABC": 1, "UNDERDETERMINED": 1}, "ABA")
        assert m["n"] == 5 and m["k"] == 3
        assert m["p_truth"] == pytest.approx(0.6)
        assert m["nll_unsmoothed"] == pytest.approx(-math.log(0.6))
        assert m["p_truth_jeffreys"] == pytest.approx(3.5 / 6.5)
        assert m["nll_jeffreys_alpha_0_5"] == pytest.approx(-math.log(3.5 / 6.5))

    def test_truth_metrics_zero_count(self):
        m = truth_metrics({"ABC": 3}, "ABA")
        assert m["nll_unsmoothed"] == float("inf")
        assert math.isfinite(m["nll_jeffreys_alpha_0_5"])

    def test_canonical_signature_deterministic(self):
        p1 = {"callable": "s.megasweep",
              "axes": [{"name": "mag.field", "start": 8.0, "stop": 0.77, "points": 141}],
              "delays": {"fast": 0.05, "slow": 1.2}, "kwargs": {}}
        s1 = json.dumps(canonical_tool_signature(p1), sort_keys=True)
        s2 = json.dumps(canonical_tool_signature(p1), sort_keys=True)
        assert s1 == s2

    def test_nested_axis_groups_are_flattened_for_metrics(self):
        parsed = {
            "callable": "s.multimegasweep",
            "axes": [
                [{"name": "mag.field", "start": 0.5, "stop": 3.0, "points": 101}],
                [{"name": "k_tg.volt", "start": -1.8, "stop": -0.9, "points": 151},
                 {"name": "k_bg.volt", "start": -1.8, "stop": -0.6, "points": 151}],
            ],
            "delays": 2.5, "kwargs": {},
        }
        signature = canonical_tool_signature(parsed)
        assert [axis["name"] for axis in signature["axes"]] == [
            "k_bg.volt", "k_tg.volt", "mag.field"
        ]
        metrics = variance.tool_call_metrics([{"sample": 1, "parsed": parsed}])
        assert metrics["axes_names_signature"]["counts"] == {
            "k_bg.volt,k_tg.volt,mag.field": 1
        }
        assert metrics["numeric"]["axis:mag.field"]["points"]["median"] == 101
        assert metrics["delay_keys_signature"]["counts"] == {"delay": 1}
        assert metrics["numeric"]["delay:delay"]["median"] == 2.5

    def test_callable_spelling_is_canonicalized(self):
        bare = canonical_tool_signature({"callable": "megasweep", "axes": []})
        annotated = canonical_tool_signature(
            {"callable": "s.megasweep (gate-loop structure)", "axes": []}
        )
        assert bare["callable"] == "s.megasweep"
        assert annotated["callable"] == "s.megasweep"

    def test_declared_support_normalized_entropy(self):
        # Two observed bins but declared support of 3: normalization uses ln(3)
        s = categorical_stats(["ABA", "ABA", "ABC", "ABC", "ABC"],
                              support=["ABA", "ABC", "UNDERDETERMINED"])
        assert s["k"] == 3
        assert s["k_observed"] == 2
        h = -(2 / 5) * math.log(2 / 5) - (3 / 5) * math.log(3 / 5)
        assert s["entropy_nats"] == pytest.approx(h)
        assert s["entropy_normalized"] == pytest.approx(h / math.log(3))

    def test_declared_support_single_bin_not_certain(self):
        s = categorical_stats(["ABA"] * 5, support=["ABA", "ABC", "UNDERDETERMINED"])
        assert s["k"] == 3 and s["k_observed"] == 1
        assert s["entropy_normalized"] == 0.0

    def test_jeffreys_denominator_uses_declared_support(self):
        # Truth ABA never observed; declared 3-class support must widen the
        # denominator (N + alpha*3), not the observed-bin count.
        m = truth_metrics({"ABC": 5}, "ABA",
                           support=["ABA", "ABC", "UNDERDETERMINED"])
        assert m["k"] == 3 and m["k_observed"] == 1
        assert m["p_truth_jeffreys"] == pytest.approx(0.5 / (5 + 1.5))
        assert m["nll_jeffreys_alpha_0_5"] == pytest.approx(math.log(13))
        assert m["nll_unsmoothed"] == float("inf")

    def test_verdict_metrics_declared_support(self):
        recs = [
            {"sample": 1, "parsed": {"verdict": "ABA"}},
            {"sample": 2, "parsed": {"verdict": "ABC"}},
        ]
        m = variance.verdict_metrics(recs, "ABA")
        assert m["verdict"]["k"] == 3
        assert m["verdict"]["k_observed"] == 2
        assert m["verdict"]["entropy_normalized"] == pytest.approx(
            math.log(2) / math.log(3)
        )
        gt = m["ground_truth"]
        assert gt["p_truth_jeffreys"] == pytest.approx(1.5 / (2 + 1.5))


# ---------------------------------------------------------------------------
# End-to-end run with the fake harness: sampling, resumability, summaries
# ---------------------------------------------------------------------------


def _claude_result(model_text: str) -> str:
    return json.dumps(
        {
            "type": "result",
            "subtype": "success",
            "is_error": False,
            "duration_ms": 10,
            "num_turns": 1,
            "result": model_text,
            "total_cost_usd": 0.0001,
            "usage": {"input_tokens": 5, "output_tokens": 5},
            "modelUsage": {"fake-model-1": {"inputTokens": 5, "outputTokens": 5}},
        }
    )


TOOL_CALL_TEXT = (
    '{"callable": "s.megasweep", "axes": [{"name": "mag.field", "start": 8.0, '
    '"stop": 0.77, "points": 141}], "delays": {"fast": 0.05, "slow": 1.2}, '
    '"kwargs": {}, "rationale": "fan"}'
)
VERDICT_TEXT = '{"verdict": "ABA", "confidence": "HIGH", "evidence": ["e"], "summary": "s"}'


def _set_script(doc, outputs: list[str]):
    doc["harness"]["script"] = [{"stdout": _claude_result(o), "stderr": "", "rc": 0}
                                for o in outputs]


class TestEndToEndRun:
    def test_run_resume_force_and_summary(self, syn, tmp_path):
        root, mpath = syn
        doc = load_manifest(mpath)
        _set_script(doc, [TOOL_CALL_TEXT, TOOL_CALL_TEXT,
                          VERDICT_TEXT, VERDICT_TEXT])
        out = tmp_path / "out"
        rc = run_experiments(doc, out, max_parallel=1)
        assert rc == 0

        # Each sample has its own workspace; within a (campaign, experiment)
        # frontier every sample workspace is byte-identical (one hash per cell)
        hashes: dict[tuple[str, str], set] = {}
        for sj in (out / "samples").glob("*/*/sample-*/sample.json"):
            rec = json.loads(sj.read_text())
            assert rec["status"] == "ok", rec
            assert rec["model_resolved"] == "fake-model-1"
            hashes.setdefault((rec["campaign"], rec["experiment"]), set()).add(
                rec["workspace_hash"]
            )
        assert set(hashes) == {
            ("20260620-qc0426", "tool-call"),
            ("20260620-qc0426", "final-analysis"),
        }
        assert all(len(hs) == 1 for hs in hashes.values())

        summary = summarize(out, doc)
        trials = summary["trials"]
        assert trials[0]["trial"] == 1
        assert trials[0]["original_verdict"] == "ABA (strong)"
        assert "original (historical) verdict: `ABA (strong)`" in (
            out / "report.md"
        ).read_text()
        tc = trials[0]["experiments"]["tool-call"]
        fa = trials[0]["experiments"]["final-analysis"]
        assert tc["samples_total"] == 2 and tc["samples_ok"] == 2
        assert fa["samples_total"] == 2 and fa["samples_ok"] == 2
        assert tc["metrics"]["callable"]["entropy_nats"] == 0.0
        assert fa["metrics"]["verdict"]["counts"] == {"ABA": 2}
        gt = fa["metrics"]["ground_truth"]
        assert gt["p_truth"] == 1.0
        assert gt["nll_unsmoothed"] == pytest.approx(0.0)

        # Resumability: second run with an exhausted harness reuses everything
        doc2 = load_manifest(mpath)
        doc2["harness"]["script"] = []
        rc = run_experiments(doc2, out, max_parallel=1)
        assert rc == 0
        summary2 = summarize(out, doc2)
        for t in summary2["trials"]:
            for exp in t["experiments"].values():
                assert exp["samples_reused"] == exp["samples_total"] > 0

        # --force re-runs against fresh harness output
        doc3 = load_manifest(mpath)
        _set_script(doc3, [TOOL_CALL_TEXT, TOOL_CALL_TEXT,
                           VERDICT_TEXT, VERDICT_TEXT])
        rc = run_experiments(doc3, out, max_parallel=1, force=True)
        assert rc == 0
        summary3 = summarize(out, doc3)
        for t in summary3["trials"]:
            for exp in t["experiments"].values():
                assert exp["samples_reused"] == 0

    def test_numeric_spreads_emitted_in_csv_and_report(self, syn, tmp_path):
        root, mpath = syn
        doc = load_manifest(mpath)
        _set_script(doc, [TOOL_CALL_TEXT, TOOL_CALL_TEXT,
                          VERDICT_TEXT, VERDICT_TEXT])
        out = tmp_path / "out"
        run_experiments(doc, out, max_parallel=1)
        # axis subfields flattened into tidy CSV rows with real values
        rows = list(__import__("csv").DictReader((out / "summary.csv").open()))
        by_metric = {(r["metric"], r["detail"]): r["value"] for r in rows}
        assert float(by_metric[("axis:mag.field.start.mean", "")]) == 8.0
        assert float(by_metric[("axis:mag.field.stop.mean", "")]) == 0.77
        assert float(by_metric[("axis:mag.field.points.mean", "")]) == 141.0
        assert float(by_metric[("axis:mag.field.span.median", "")]) == \
            pytest.approx(0.77 - 8.0)
        assert float(by_metric[("delay:slow.mean", "")]) == 1.2
        report = (out / "report.md").read_text()
        assert "`axis:mag.field.start`" in report
        assert "`delay:slow`" in report

    def test_deterministic_summary(self, syn, tmp_path):
        root, mpath = syn
        doc = load_manifest(mpath)
        _set_script(doc, [TOOL_CALL_TEXT, TOOL_CALL_TEXT,
                          VERDICT_TEXT, VERDICT_TEXT])
        out = tmp_path / "out"
        run_experiments(doc, out, max_parallel=1)
        s1 = (out / "summary.json").read_text()
        summarize(out, doc)
        s2 = (out / "summary.json").read_text()
        assert s1 == s2
        assert (out / "summary.csv").exists()
        assert (out / "samples.csv").exists()
        assert (out / "report.md").exists()
        assert (out / "plots" / "entropy-vs-campaign-trial.png").exists()
        assert (out / "plots" / "entropy-vs-campaign-trial.svg").exists()

    def test_unparseable_sample_retained(self, syn, tmp_path):
        root, mpath = syn
        doc = load_manifest(mpath)
        _set_script(doc, ["no idea what to do", "nothing here"])
        out = tmp_path / "out"
        run_experiments(doc, out, max_parallel=1, samples_override=1)
        summary = summarize(out, doc)
        tc = summary["trials"][0]["experiments"]["tool-call"]
        fa = summary["trials"][0]["experiments"]["final-analysis"]
        assert tc["samples_unparseable"] == 1
        assert fa["samples_unparseable"] == 1
        assert tc["samples_failed"] == 0
        assert fa["samples_failed"] == 0
        # metrics computed from zero parsed records still exist
        assert tc["metrics"]["callable"]["n"] == 0
        assert fa["metrics"]["verdict"]["n"] == 0

    def test_failed_harness_sample_retained(self, syn, tmp_path):
        root, mpath = syn
        doc = load_manifest(mpath)
        doc["harness"]["script"] = [
            {"stdout": "", "stderr": "boom", "rc": 1},
            {"stdout": _claude_result(VERDICT_TEXT), "stderr": "", "rc": 0},
        ]
        out = tmp_path / "out"
        rc = run_experiments(doc, out, max_parallel=1, samples_override=1)
        assert rc == 1  # one failed sample -> nonzero overall
        summary = summarize(out, doc)
        tc = summary["trials"][0]["experiments"]["tool-call"]
        fa = summary["trials"][0]["experiments"]["final-analysis"]
        assert tc["samples_failed"] == 1
        assert tc["samples_total"] == 1
        assert fa["samples_ok"] == 1

    def test_max_tasks_runs_pending_samples_only(self, syn, tmp_path):
        root, mpath = syn
        out = tmp_path / "out"

        first = load_manifest(mpath)
        _set_script(first, [TOOL_CALL_TEXT])
        assert run_experiments(first, out, max_tasks=1) == 0
        records = sorted((out / "samples").glob("*/*/sample-*/sample.json"))
        assert len(records) == 1
        assert records[0].parent.name == "sample-01"

        second = load_manifest(mpath)
        _set_script(second, [TOOL_CALL_TEXT])
        assert run_experiments(second, out, max_tasks=1) == 0
        records = sorted((out / "samples").glob("*/*/sample-*/sample.json"))
        assert len(records) == 2
        assert {path.parent.name for path in records} == {"sample-01", "sample-02"}
        assert {json.loads(path.read_text())["experiment"] for path in records} == {
            "tool-call"
        }

    def test_max_tasks_must_be_positive(self, syn, tmp_path):
        root, mpath = syn
        doc = load_manifest(mpath)
        with pytest.raises(VarianceError, match="max_tasks"):
            run_experiments(doc, tmp_path / "out", max_tasks=0)


class TestSampleLeases:
    def test_live_owner_prevents_duplicate_claim(self, tmp_path):
        lease = tmp_path / "sample.lock"
        first = variance._claim_sample_lease(lease)
        assert first is not None
        assert variance._claim_sample_lease(lease) is None
        variance._release_sample_lease(lease, first)
        second = variance._claim_sample_lease(lease)
        assert second is not None
        variance._release_sample_lease(lease, second)
        assert not lease.exists()

    def test_dead_same_host_owner_is_reclaimed(self, tmp_path):
        lease = tmp_path / "sample.lock"
        lease.write_text(
            json.dumps(
                {
                    "pid": 999_999_999,
                    "host": variance.socket.gethostname(),
                    "token": "dead",
                }
            ),
            encoding="utf-8",
        )
        token = variance._claim_sample_lease(lease)
        assert token is not None
        variance._release_sample_lease(lease, token)
        assert not lease.exists()


# ---------------------------------------------------------------------------
# CLI smoke paths
# ---------------------------------------------------------------------------


class TestCLI:
    def test_inspect(self, syn, capsys):
        root, mpath = syn
        rc = main(["inspect", "--manifest", str(mpath)])
        assert rc == 0
        out = capsys.readouterr().out
        assert "20260620-qc0426" in out
        assert "leak-scan: PASS" in out

    def test_materialize_cli(self, syn, tmp_path, capsys):
        root, mpath = syn
        out = tmp_path / "outroot"
        rc = main(["materialize", "--manifest", str(mpath), "--output", str(out)])
        assert rc == 0
        assert (out / "materializations" / "20260620-qc0426" / "tool-call"
                / "materialization.json").exists()

    def test_run_and_summarize_cli(self, syn, tmp_path):
        root, mpath = syn
        doc = load_manifest(mpath)
        _set_script(doc, [TOOL_CALL_TEXT, TOOL_CALL_TEXT,
                          VERDICT_TEXT, VERDICT_TEXT])
        # Persist scripted harness into the manifest file the CLI will load
        mpath.write_text(
            __import__("yaml").safe_dump(doc, sort_keys=False), encoding="utf-8"
        )
        out = tmp_path / "outroot"
        rc = main(["run", "--manifest", str(mpath), "--output", str(out),
                   "--samples", "1", "--max-tasks", "2"])
        assert rc == 0
        rc = main(["summarize", "--output", str(out), "--manifest", str(mpath)])
        assert rc == 0

    def test_summarize_without_manifest(self, syn, tmp_path):
        root, mpath = syn
        doc = load_manifest(mpath)
        _set_script(doc, [TOOL_CALL_TEXT, TOOL_CALL_TEXT,
                          VERDICT_TEXT, VERDICT_TEXT])
        out = tmp_path / "out"
        run_experiments(doc, out, max_parallel=1)
        rc = main(["summarize", "--output", str(out)])
        assert rc == 0

    def test_bad_manifest_cli(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("version: 1\nexperiment_id: x\n", encoding="utf-8")
        rc = main(["inspect", "--manifest", str(bad)])
        assert rc == 2
