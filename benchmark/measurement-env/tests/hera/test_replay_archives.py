"""`hera-replay cut` against real in-repo archives: the QC0426 06-19 session at
the fan-design point, and the vti-02 08-21 session for the Windows path rewrite."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from hera.replay.archive import open_archive
from hera.replay.case import load_case
from hera.replay.derive import derive
from hera.replay.errors import CutError
from hera.replay.mask import load_mask
from hera.replay.materialize import materialize

REPO = Path(__file__).resolve().parents[2]
QC0426 = REPO / "hera/docs/notes/2026-06-19-QC0426-session-3"
# Line 841: the result of the agent's read of multimegasweep's signature, after
# the electron spot check (run 3) landed and before the fan design (line 848).
FAN_DESIGN_CUT = "9e2f2705-fd95-4c6b-acad-33b27d01bcfc"
VTI02 = REPO / "hera/docs/notes/2026-08-21-vti-02-session"
VTI02_CUT = "4adf8635-40af-4929-98f9-a07734f564b2"  # line 328, gate C leg 0 read
VTI02_CUT_AFTER_SCRIPT_REWRITE = "94fec429-cc13-4244-92ca-6675820a9084"  # line 448


@pytest.fixture(scope="module")
def qc0426_episode(tmp_path_factory):
    dest = tmp_path_factory.mktemp("qc0426") / "episode"
    archive = open_archive(QC0426)
    ep = materialize(archive, derive(archive, FAN_DESIGN_CUT), dest)
    return dest, ep


def test_qc0426_fan_design_notebook_cut(qc0426_episode):
    dest, ep = qc0426_episode
    measure = ep["notebooks"]["20260619_measure.ipynb"]
    assert measure["cut_cell"] == {"index": 45, "id": "86e1ec89"}
    assert measure["cells_kept"] == 46
    cells = json.loads((dest / "session/20260619_measure.ipynb").read_text())["cells"]
    assert cells[-1]["id"] == "86e1ec89" and cells[-1]["outputs"]
    assert not any(c["id"] == "82868871" for c in cells)
    counts = [c["execution_count"] for c in cells if c["cell_type"] == "code" and c["execution_count"] is not None]
    assert counts == list(range(1, measure["code_cells_renumbered"] + 1))
    # aff3decf ran before the cut and again eight hours after it; only the later outputs are archived
    stripped = next(c for c in cells if c["id"] == "aff3decf")
    assert stripped["outputs"] == [] and stripped["execution_count"] is None
    assert measure["outputs_stripped"] == ["aff3decf"]
    ana = ep["notebooks"]["20260619_ana.ipynb"]
    assert ana["cut_cell"] == {"index": 16, "id": "f2414db7"}


def test_qc0426_fan_design_runs(qc0426_episode):
    dest, ep = qc0426_episode
    assert ep["runs"]["kept"] == [0, 1, 2, 3]
    assert ep["runs"]["unobserved"] == [4] and ep["runs"]["in_flight_dropped"] == []
    assert (dest / "session/data/3/metadata.json").exists() and not (dest / "session/data/4").exists()


def test_qc0426_fan_design_device_card(qc0426_episode):
    dest, ep = qc0426_episode
    card = (dest / "session/device_card.md").read_text()
    sections = re.findall(r"^## .*$", card, re.M)
    assert any(s.startswith("## (n, D) calibration — ESTABLISHED 2026-06-19") for s in sections)
    assert not any("Stacking result" in s for s in sections)
    archived = (QC0426 / "device_card.md").read_text()
    assert "## Stacking result" in archived
    ops = ep["files"]["reconstructed"]["device_card.md"]["ops"]
    assert [o["kind"] for o in ops] == ["read", "read", "edit"] and ops[-1]["index"] < ep["cut"]["index"]


def test_qc0426_fan_design_notes_and_scratch(qc0426_episode):
    dest, ep = qc0426_episode
    notes = (dest / "session/session_notes.md").read_text()
    assert "MODEL TEMPLATE" in notes and "STEP 4/5" not in notes
    assert not (dest / "session/hera_scratch/fan_electron.py").exists()
    assert (dest / "session/hera_scratch/ana_sdh_elec.py").exists()
    assert ep["not_materialized"]["hera_scratch/sdh_elec_run3.png"].startswith("the Read returned a downscaled rendering")


def test_qc0426_transcript_placement_and_rewrite(qc0426_episode):
    dest, ep = qc0426_episode
    jsonl = dest / "claude-projects/-home-hera-measurements-zack-20260619-3-QC0426/226a2e70-8449-42b4-800c-7fee0e907e29.jsonl"
    lines = jsonl.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 842 and json.loads(lines[-1])["uuid"] == FAN_DESIGN_CUT
    text = jsonl.read_text(encoding="utf-8")
    assert "/c/Users/DGG" not in text and "C:\\\\Users\\\\DGG" not in text
    assert "/home/hera/measurements/zack/20260619.3-QC0426" in text
    assert "~/measurement_env/hera/recipes/measurements/landau-fan.md" in text
    assert ep["transcript"]["targets"]["measurement_env"]


def test_vti02_cut_rewrites_windows_paths(tmp_path):
    archive = open_archive(VTI02)
    ep = materialize(archive, derive(archive, VTI02_CUT), tmp_path / "vti")
    assert ep["rig"]["cwd"] == r"C:\Users\DGG\VTI_local_data\zack\20260821-vti-02"
    assert ep["runs"]["kept"] == [0]
    assert ep["files"]["reconstructed"]["session_notes.md"]["basis"] == "appends only; head unseen by the agent"
    jsonl = next((tmp_path / "vti/claude-projects").rglob("*.jsonl"))
    text = jsonl.read_text(encoding="utf-8")
    assert "C:\\\\Users\\\\DGG\\\\VTI_local_data" not in text and "/home/hera/measurements/zack/20260821-vti-02/hera_scratch" in text


def test_vti02_cut_after_inline_script_rewrite_replays_the_placeholder_fill():
    st = derive(open_archive(VTI02), VTI02_CUT_AFTER_SCRIPT_REWRITE).files["hera_scratch/gatemap_cell.py"]
    assert st.corroborated_by == "archived" and [o["kind"] for o in st.ops] == ["write", "script"]
    assert "__RMIN__" not in st.content and "60" in st.content


ZF1_0622 = REPO / "hera/docs/notes/2026-06-22-zf1-session"
ZF1_0622_CUT = "90d747ac-293d-42fb-8abb-42460d31f5c1"  # line 219, the run-1 recon read; the survey is designed next
ZF1_0625 = REPO / "hera/docs/notes/2026-06-25-zf1-session"
ZF1_0625_CUT = "ee647de8-70ec-4ff5-93ad-fffa565b087a"  # line 160, before the gatemap recipe Read


def test_zf1_cut_reads_task_files_under_the_short_name_home(tmp_path):
    # The toploader agents read the CLI's task files as C:\Users\TOPLOA~1\AppData\…
    archive = open_archive(ZF1_0622)
    ep = materialize(archive, derive(archive, ZF1_0622_CUT), tmp_path / "zf1")
    assert ep["rig"]["cwd"] == r"C:\Users\toploader\measurements\aaron\20260622-zf1"
    assert ep["runs"]["kept"] == [0, 1]
    assert ep["notebooks"]["20260622_measure.ipynb"]["cut_cell"]["index"] == 28
    # the agent executed `setup` and `nd-geometry` by id; the template's Run-block cells after them were on the page
    assert ep["notebooks"]["20260622_ana.ipynb"]["cells_kept"] == 10
    assert all(p.startswith("claude/C--Users-toploader-measurements-aaron-20260622-zf1/") for p in ep["transcript"]["targets"]["cli_task_outputs"])
    text = next((tmp_path / "zf1/claude-projects").rglob("*.jsonl")).read_text(encoding="utf-8")
    assert "TOPLOA~1" not in text and "/home/hera/AppData/Local/Temp/claude/" in text


def test_zf1_cut_skips_tmp_heredocs(tmp_path):
    archive = open_archive(ZF1_0625)
    ep = materialize(archive, derive(archive, ZF1_0625_CUT), tmp_path / "zf1")
    assert ep["runs"]["kept"] == [0, 1, 2, 3]
    assert "tmp/gateC_md.txt" in ep["transcript"]["targets"]["volatile"]
    assert not (tmp_path / "zf1/session/tmp").exists()


VTI02_FRONTIERS = ("vti02-probe-first", "vti02-fan-design", "vti02-pre-fan-0822", "vti02-pre-fan-0824",
                   "vti02-fan-request-0822")


@pytest.mark.parametrize("frontier", VTI02_FRONTIERS)
def test_vti02_arms_share_one_origin(frontier):
    # One arm file per (model, condition), one cut: the matrix is only a matrix if
    # every cell starts from the same session state. All but the development
    # 08-24 frontier also carry the Codex models.
    arms = sorted((REPO / "hera/replay/cases").glob(f"{frontier}-*.yaml"))
    runners = {"claude"} if frontier == "vti02-probe-first" else {"claude", "codex"}
    models = {p.stem[len(frontier) + 1:].rsplit("-", 1)[0] for p in arms}
    assert sorted(p.stem for p in arms) == sorted(f"{frontier}-{m}-{a}" for m in models for a in ("corpus", "none"))
    assert {load_case(p).runner for p in arms} == runners
    raws = {p.name: yaml.safe_load(p.read_text(encoding="utf-8")) for p in arms}
    origins = {(r["source"], r["cut"]["transcript"], r["cut"]["at"], r.get("mask")) for r in raws.values()}
    assert len(origins) == 1
    for p in arms:
        case = load_case(p)
        arm = p.stem.rsplit("-", 1)[1]
        assert case.brief_path.name == f"{arm}.md" and case.brief_path.parent.name == frontier
        assert case.condition == {"corpus": "full", "none": "none"}[arm]
        assert case.n == 10 and case.grader == "fan-design" and case.start == "fresh"
        assert "## Session state — in progress" in case.brief_text and "\r" not in case.brief_text


def state_texts(session):
    """Every agent-readable text in a materialized session: files, and notebook
    sources with their outputs."""
    for p in sorted(session.rglob("*")):
        rel = p.relative_to(session).as_posix()
        if not p.is_file() or rel.startswith(".claude/") or p.suffix in (".png", ".gz"):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if p.suffix == ".ipynb":
            cells = json.loads(text)["cells"]
            text = "".join("".join(c["source"]) + "".join("".join(o.get("text", "")) for o in c.get("outputs", [])) for c in cells)
        yield rel, text


READ_TEXT = re.compile(r"29\.3 T|0\.886|onset_b = 0\.50|pair sum check")
RULE_TEXT = re.compile(r"Nyquist|1/\(3|1/\(2 F_L|per period|Δ\(1/B\)|Delta\(1/B\)|1/B span|1/B record|δF ≤|Handed to the fan", re.I)


def test_vti02_pre_fan_0824_state_carries_its_device_card_and_no_fan_design(tmp_path):
    # The 08-24 agent never touched its device card before the cut; the card was
    # deployed before the session, so the state carries it as archived. The mask
    # takes the fan's axes and start out of plan.md and leaves its steps.
    case = load_case(REPO / "hera/replay/cases/vti02-pre-fan-0824-opus55-none.yaml")
    archive = open_archive(case.source)
    ep = materialize(archive, derive(archive, case.cut_at), tmp_path / "ep", stage_transcript=False,
                     mask=load_mask(case.mask_path))
    session = tmp_path / "ep" / "session"
    card = (session / "device_card.md").read_text(encoding="utf-8")
    assert card.startswith("# Device card — vti-02") and "device_card.md" not in ep["not_materialized"]
    plan = (session / "hera_scratch/plan.md").read_text(encoding="utf-8")
    assert "field_invB" not in plan and "start where the magnet sits" not in plan
    assert "**P3 — CNP-line cut" in plan and "**P4 — Landau fan** at base T (~2–3 h). Reads:" in plan
    assert len(ep["mask"]["edits"]) == 2


def test_vti02_pre_fan_0822_state_carries_no_fan_rule(tmp_path):
    # The masked 08-22 state: the hole spot check complete and nothing the agent did
    # while it ran (electron read, notes, fan draft, run-7 interim read), the
    # field-step and resolution rules and the fan's B_lo and direction gone; the
    # executed grids and the calibration read stay; neither spot check is read.
    case = load_case(REPO / "hera/replay/cases/vti02-pre-fan-0822-fable-none.yaml")
    archive = open_archive(case.source)
    ep = materialize(archive, derive(archive, case.cut_at), tmp_path / "ep", stage_transcript=False,
                     mask=load_mask(case.mask_path))
    assert ep["mask"]["dropped"] == ["hera_scratch/cell_fan.py", "hera_scratch/md_fan.md", "hera_scratch/fan_read.py",
                                     "hera_scratch/ana_spot6_md.md", "hera_scratch/ana_spot6.py", "hera_scratch/spot_run6.png",
                                     "hera_scratch/spot_fft.py", "hera_scratch/spot_run7.png",
                                     "20260822_ana.ipynb#a1d41a69", "20260822_ana.ipynb#c056c015"]
    assert len(ep["mask"]["edits"]) == 17
    assert ep["runs"]["kept"] == [0, 1, 2, 3, 4, 5, 6, 7]
    session = tmp_path / "ep" / "session"
    hits = [f"{rel}: {m.group(0)}" for rel, text in state_texts(session) for m in RULE_TEXT.finditer(text)]
    assert hits == []
    # The scratch inventory at the cut, every file ruled kept by name: a file that
    # rides along with the archive fails here instead of leaking into an arm.
    assert sorted(p.name for p in (session / "hera_scratch").iterdir()) == [
        "ana_cal.py", "ana_cal_md.md", "ana_gatec.py", "ana_gatec_md.md", "cal_run5.json", "cell_gatec.py",
        "cell_gatemap.py", "cell_probe.py", "cell_spot_e.py", "cell_spot_h.py", "cell_verify.py", "cnp_cal_run5.png",
        "cnp_calibration.py", "gatec_analysis.py", "gatec_legs.png", "gatemap_cnp.py", "gatemap_run5.png", "md_gatec.md",
        "md_gatemap.md", "md_gatemap2.md", "md_spot_e.md", "md_spot_h.md", "md_verify.md"]
    # Files a script or a shell redirect wrote before the cut are in the state as the rig
    # left them: the calibration the fan's gate voltages come from, and each plot's last
    # rendering before the cut, not the half-finished one the agent read first.
    for rel in ("hera_scratch/cal_run5.json", "hera_scratch/gatemap_run5.png", "hera_scratch/cnp_cal_run5.png"):
        assert (session / rel).read_bytes().replace(b"\r\n", b"\n") == (archive.root / rel).read_bytes().replace(b"\r\n", b"\n"), rel
    notes = (session / "session_notes.md").read_text(encoding="utf-8")
    assert notes.rstrip().endswith("would price it right.") and "admixture" not in notes and "per-point cost" not in notes
    # Neither spot check is read: the ana notebook ends on the calibration read, and
    # the electron read's numbers appear nowhere in the state.
    ana = json.loads((session / "20260822_ana.ipynb").read_text(encoding="utf-8"))
    assert ana["cells"][-1]["id"] == "5a904a2c" and ana["cells"][-1]["execution_count"] == 7
    for rel, text in state_texts(session):
        assert not READ_TEXT.search(text), f"{rel}: {READ_TEXT.search(text).group(0)}"
    # The operator's handoff: the hole ride-down is the last agent cell (magnet at
    # 0.303 T), then the executed return to the bring-up state, field at 0 T, then
    # the archived probe cell re-run in the same kernel as the last cell; the
    # episode clock starts after all of them.
    measure = json.loads((session / "20260822_measure.ipynb").read_text(encoding="utf-8"))
    hole, readback, probe = measure["cells"][-5], measure["cells"][-3], measure["cells"][-1]
    hole_out = "".join("".join(o.get("text", "")) for o in hole["outputs"])
    assert hole["id"] == "5bfd8912" and hole["execution_count"] == 22 and "done: B = +0.303 T" in hole_out
    assert "the fan starts" not in "".join(hole["source"])
    out = "".join(readback["outputs"][0]["text"])
    assert readback["cell_type"] == "code" and "hera" not in readback["metadata"] and readback["execution_count"] == 23
    assert "restore=state0" in "".join(readback["source"]) and "field : 0.0027" in out and "V_tg : 0.0" in out
    archived = next(c for c in json.loads(archive.notebooks["20260822_measure.ipynb"].read_text(encoding="utf-8"))["cells"] if c.get("id") == "e8c83505")
    assert "".join(probe["source"]) == "".join(archived["source"]).rstrip("\n") and "hera" not in probe["metadata"]
    assert probe["execution_count"] == 24 and "".join(probe["outputs"][0]["text"]).rstrip().endswith("KERNEL PROBE: BOUND")
    assert [a["cell_type"] for a in ep["mask"]["appended"]] == ["markdown", "code", "markdown", "code"]
    # The hera-watch stub's baseline is the masked notebook: the mask's appended cells are history.
    baseline = json.loads((session / ".claude" / "measure_cells.json").read_text(encoding="utf-8"))
    assert baseline == {"20260822_measure.ipynb": [c["id"] for c in measure["cells"]]}
    assert probe["id"] in baseline["20260822_measure.ipynb"]
    assert ep["clock"]["after_cut_s"] == 6 * 60 + 2 and ep["mtimes"]["20260822_measure.ipynb"] == ep["clock"]["start"]
    assert (session / "20260822_measure.ipynb").stat().st_mtime == pytest.approx(datetime.fromisoformat(ep["clock"]["start"]).timestamp())
