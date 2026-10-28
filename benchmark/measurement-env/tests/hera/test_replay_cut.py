"""`hera-replay inspect` / `cut` on the synthetic archive: the derivation rules,
the materialized layout, and the reject cases."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timedelta

import pytest
import yaml

from hera.replay import main
from hera.replay.archive import open_archive
from hera.replay.derive import derive
from hera.replay.errors import CutError
from hera.replay.inspect_cmd import render
from hera.replay.materialize import materialize
from hera.replay.rewrite import Corpus
from tests.hera.replay_fixture import (
    CARD_V0,
    CARD_V1,
    CWD,
    INIT_SID,
    MENV,
    NOTE_A,
    NOTES_V0,
    PNG,
    PROBE,
    SID,
    T0,
    Builder,
    build_transcript,
    cell,
    make_archive,
)


def ep_cut_epoch(ep: dict) -> float:
    return datetime.fromisoformat(ep["cut"]["timestamp"]).timestamp()


@pytest.fixture
def archive(tmp_path):
    root, b = make_archive(tmp_path / "2026-01-01-dev-session")
    return root, b


def test_inspect_lists_turns_and_markers(archive):
    root, b = archive
    out = render(open_archive(root))
    assert f"transcripts/{SID}.jsonl" in out
    assert INIT_SID not in out
    assert "[APPEND]" in out and "[EXEC]" in out
    assert "+cell aaaa0001@3" in out and "RUN data/0" in out
    assert "device_card.md" in out and "~/measurement_env/hera/recipes/measurements/gatemap.md" in out
    grep = render(open_archive(root), grep="execute-cell")
    assert grep.count("\n") < out.count("\n") and "execute-cell" in grep
    around = render(open_archive(root), around=int(b.uuids["cut"][:8], 16), context=1)
    assert around.count("\n") - 5 <= 3


def test_derivation_at_the_cut(archive):
    root, b = archive
    d = derive(open_archive(root), b.uuids["cut"])
    _, measure = d.notebooks["x_measure.ipynb"]
    assert (measure.keep, measure.cut_cell) == (4, {"index": 3, "id": "aaaa0001"})
    assert measure.code_cells_renumbered == 3
    _, ana = d.notebooks["x_ana.ipynb"]
    assert (ana.keep, ana.cut_cell["id"]) == (3, "bbbb0001")
    assert ana.code_cells_renumbered == 0 and ana.outputs_stripped == ["setup"]
    assert d.runs.kept == [0] and d.runs.unobserved == [1] and d.runs.in_flight == []
    files = d.files
    assert files["device_card.md"].content == CARD_V1
    assert files["device_card.md"].corroborated_by == f"edit@{b.index('edit-card-2')}"
    assert files["session_notes.md"].content == NOTES_V0 + NOTE_A
    assert files["session_notes.md"].corroborated_by == "archived"
    assert files["hera_scratch/probe.py"].content == PROBE
    assert files["hera_scratch/plot.png"].content == PNG
    assert "hera_scratch/fan.py" not in files
    assert d.targets.measurement_env == {"hera/recipes/measurements/gatemap.md", "hera/recipes/STYLE.md"}


def test_materialized_episode(archive, tmp_path):
    root, b = archive
    dest = tmp_path / "episode"
    ep = materialize(open_archive(root), derive(open_archive(root), b.uuids["cut"]), dest)
    session = dest / "session"
    assert (session / "device_card.md").read_text() == CARD_V1
    assert (session / "session_notes.md").read_text() == NOTES_V0 + NOTE_A
    assert (session / "hera_scratch/probe.py").read_text() == PROBE
    assert (session / "hera_scratch/plot.png").read_bytes() == PNG
    assert not (session / "hera_scratch/fan.py").exists() and not (session / "hera_scratch/extra.md").exists()
    assert (session / "data/0/metadata.json").exists() and not (session / "data/1").exists() and not (session / "data/log.log").exists()
    assert (session / "hera_session.md").exists() and (session / "rig_card.md").exists()
    measure = json.loads((session / "x_measure.ipynb").read_text())
    assert [c["id"] for c in measure["cells"]] == ["t1", "t2", "s1", "aaaa0001"]
    assert measure["cells"][3]["outputs"]
    ana = json.loads((session / "x_ana.ipynb").read_text())
    assert [c["id"] for c in ana["cells"]] == ["hdr", "setup", "bbbb0001"]
    # executed after the cut: the archive holds only its later outputs
    assert ana["cells"][1]["outputs"] == [] and ana["cells"][1]["execution_count"] is None
    assert ep["notebooks"]["x_ana.ipynb"]["outputs_stripped"] == ["setup"]
    assert [c["execution_count"] for c in measure["cells"] if c["cell_type"] == "code"] == [1, 2, 3]
    assert (dest / "stubs/hera-notify").exists() and (dest / "stubs/hera-watch").exists()
    assert (session / "device_card.md").stat().st_mtime == pytest.approx(ep_cut_epoch(ep))
    settings = json.loads((session / ".claude/settings.json").read_text())
    assert settings["hooks"]["PreToolUse"][0]["matcher"] == "Bash|ScheduleWakeup|Monitor"
    assert "episode_stop.py" in settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    assert (session / ".claude/episode_stop.py").exists()
    jsonl = dest / "claude-projects" / "-home-hera-measurements-zack-20260101-dev" / f"{SID}.jsonl"
    lines = jsonl.read_text().splitlines()
    cut_index = int(b.uuids["cut"][:8], 16)
    assert len(lines) == cut_index + 1
    assert json.loads(lines[-1])["uuid"] == b.uuids["cut"]
    text = jsonl.read_text()
    assert "Users\\\\rig" not in text and "C:\\\\Users" not in text and "/c/Users/rig" not in text
    assert "/home/hera/measurements/zack/20260101-dev/hera_scratch/probe.py" in text
    assert "~/measurements/zack/20260101-dev" in text
    assert "~/measurement_env/hera/recipes/measurements/gatemap.md" in text
    assert json.loads(lines[0])["cwd"] == "/home/hera/measurements/zack/20260101-dev"
    assert ep["cut"]["uuid"] == b.uuids["cut"] and ep["cut"]["index"] == cut_index and ep["cut"]["tool"] == "Read"
    assert ep["notebooks"]["x_measure.ipynb"]["cut_cell"] == {"index": 3, "id": "aaaa0001"}
    assert ep["runs"]["kept"] == [0] and ep["runs"]["unobserved"] == [1]
    assert ep["files"]["as_archived"] == ["hera_session.md", "rig_card.md"]
    assert ep["files"]["reconstructed"]["device_card.md"]["ops"] == [{"index": 2, "kind": "read"}, {"index": b.index("edit-card-1"), "kind": "edit"}]
    assert ep["not_materialized"]["hera_scratch/extra.md"] == "written after the cut, and no op before the cut"
    assert ep["not_materialized"]["data/log.log"] == "not a run dir"
    assert ep["transcript"]["rewrites"]["session_dir"] > 0 and ep["transcript"]["rewrites"]["measurement_env"] > 0
    assert ep["transcript"]["entries_kept"] == cut_index + 1
    assert (dest / "episode.json").exists()


def test_a_file_the_rig_wrote_before_the_cut_is_in_the_state_whatever_wrote_it(archive):
    # No op on extra.md: its rig mtime alone says whether it existed at the cut. Before
    # the cut it is there as archived; after the cut (or stamped after the transcript
    # ends, an edit to the archive) it is not.
    root, b = archive
    d0 = derive(open_archive(root), b.uuids["cut"])
    extra = root / "hera_scratch/extra.md"
    cut = d0.cut_ts.timestamp()
    os.utime(extra, (cut - 60, cut - 60))
    st = derive(open_archive(root), b.uuids["cut"]).files["hera_scratch/extra.md"]
    assert st.content == extra.read_text() and st.basis.startswith("archived: last written")
    os.utime(extra, (cut + 60, cut + 60))
    assert "hera_scratch/extra.md" not in derive(open_archive(root), b.uuids["cut"]).files


def test_a_state_without_its_device_card_is_refused(archive, tmp_path):
    root, b = archive
    d = derive(open_archive(root), b.uuids["cut"])
    del d.files["device_card.md"]
    with pytest.raises(CutError, match="device_card.md is not in the state"):
        materialize(open_archive(root), d, tmp_path / "episode")


def test_cli_cut_and_stubs(archive, tmp_path, capsys):
    root, b = archive
    dest = tmp_path / "cli-episode"
    assert main(["cut", str(root), "--at", b.uuids["cut"], "--dest", str(dest)]) == 0
    out = capsys.readouterr().out
    assert "cut at cell aaaa0001 @ 3" in out and "kept [0]" in out
    with pytest.raises(SystemExit, match="case file not found"):
        main(["run", str(tmp_path / "missing.yaml")])


def test_reject_cut_on_non_tool_result(archive):
    root, b = archive
    with pytest.raises(CutError, match="not a tool_result"):
        derive(open_archive(root), b.uuids["post-cut-call"])


def test_reject_unknown_uuid(archive):
    root, _ = archive
    with pytest.raises(CutError, match="no entry with uuid"):
        derive(open_archive(root), "nope")


def test_reject_two_tactical_transcripts(tmp_path):
    root, _ = make_archive(tmp_path / "a", second_tactical=True)
    with pytest.raises(CutError, match="expected exactly one tactical transcript, found 2"):
        open_archive(root)


def test_reject_rig_session_dir(tmp_path):
    root, _ = make_archive(tmp_path / "a", transcripts_dir=".transcripts")
    with pytest.raises(CutError, match="no transcripts/ dir"):
        open_archive(root)


def test_reject_dest_exists(archive, tmp_path):
    root, b = archive
    dest = tmp_path / "taken"
    dest.mkdir()
    with pytest.raises(CutError, match="dest exists"):
        materialize(open_archive(root), derive(open_archive(root), b.uuids["cut"]), dest)


def test_reject_file_changed_outside_the_visible_ops(tmp_path):
    # The post-cut Edit saw a file the forward replay cannot produce: something
    # else wrote device_card.md, and the tool cannot tell on which side of the cut.
    root, b = make_archive(tmp_path / "a", builder=build_transcript(post_cut_card_original=CARD_V1 + "# added by a script\n"))
    with pytest.raises(CutError, match="device_card.md: content at edit@.* differs from the forward reconstruction"):
        derive(open_archive(root), b.uuids["cut"])


def test_post_cut_divergence_after_a_corroboration_point_is_fine(tmp_path):
    root, b = make_archive(tmp_path / "a", card_final="# rewritten by a script after the last Edit\n")
    assert derive(open_archive(root), b.uuids["cut"]).files["device_card.md"].content == CARD_V1


def test_reject_unplaceable_cell_id(tmp_path):
    b = build_transcript()
    b.bash("nb-collab append x_measure.ipynb --markdown x", "  appended markdown @ 9 id=deadbeef\ndone.", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    with pytest.raises(CutError, match="cell id deadbeef is in no archived notebook"):
        derive(open_archive(root), b.uuids["late"])


def test_reject_observed_run_missing_from_archive(tmp_path):
    b = build_transcript()
    b.bash("ls -d data/*", "data/0 data/1 data/7", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    with pytest.raises(CutError, match="run 7 was observed at line"):
        derive(open_archive(root), b.uuids["late"])


def _add_output(root, name, cell_id, text):
    nb = json.loads((root / name).read_text())
    cell = next(c for c in nb["cells"] if c["id"] == cell_id)
    cell["outputs"].append({"output_type": "stream", "name": "stdout", "text": text})
    (root / name).write_text(json.dumps(nb))


def test_template_cells_after_the_last_referenced_cell_are_kept(tmp_path):
    # The 06-22 zf1 ana notebook: the agent executed `setup` by id while the
    # template's Run-block cells sat after it, never named.
    b = Builder()
    b.user("# dev / rig — session brief")
    b.read("./device_card.md", CARD_V0)
    b.bash("nb-collab execute-cell x_ana.ipynb setup", "connected: path=x_ana.ipynb cells=6   [cell setup]", label="late")
    b.bash("ls", "ok", label="cut")  # the fixture's archive stamps its runs from these two labels
    b.bash("ls", "ok", label="append-fan")
    root, _ = make_archive(tmp_path / "a", builder=b, card_final=CARD_V0)
    nb = json.loads((root / "x_ana.ipynb").read_text())
    nb["cells"][2:2] = [cell("tmpl-run", "markdown", "## Run <id>"), cell("tmpl-read", "markdown", "**Read:**")]
    (root / "x_ana.ipynb").write_text(json.dumps(nb))
    d = derive(open_archive(root), b.uuids["late"])
    _, ana = d.notebooks["x_ana.ipynb"]
    assert ana.cut_cell["id"] == "setup" and ana.keep == 4
    assert [c["id"] for c in nb["cells"][:4]] == ["hdr", "setup", "tmpl-run", "tmpl-read"]


def test_run_named_only_in_a_kept_cell_output_is_observed(tmp_path):
    root, b = make_archive(tmp_path / "a")
    _add_output(root, "x_measure.ipynb", "aaaa0001", "Starting sweep with ID 1\n")
    d = derive(open_archive(root), b.uuids["cut"])
    assert d.runs.first_seen_in_notebook == {1: "x_measure.ipynb:aaaa0001"}
    assert d.runs.kept == [0] and [r["id"] for r in d.runs.in_flight] == [1] and d.runs.unobserved == []


def test_run_named_only_in_agent_text_is_observed(tmp_path):
    b = build_transcript()
    b.text("Run 1 is landing; I will read it on the wake.")
    b.bash("ls", "ok", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    d = derive(open_archive(root), b.uuids["late"])
    assert 1 in d.runs.first_seen_in_text and [r["id"] for r in d.runs.in_flight] == [1]


def test_run_named_only_by_a_corpus_cat_is_not_observed(tmp_path):
    b = build_transcript()
    b.bash("cat ~/measurement_env/docs/api/hera-analysis.md", "Open a run directory (e.g. `<notebook>/data/119`).", label="doc")
    b.bash("cat ~/measurement_env/docs/api/x.md | head -3; ls data/", "data/7\n", label="mixed")
    root, _ = make_archive(tmp_path / "a", builder=b)
    assert 119 not in derive(open_archive(root), b.uuids["doc"]).runs.first_seen
    with pytest.raises(CutError, match="run 7 was observed at line"):
        derive(open_archive(root), b.uuids["mixed"])


def test_run_named_in_a_cell_executed_after_the_cut_is_not_observed(tmp_path):
    root, b = make_archive(tmp_path / "a")
    _add_output(root, "x_ana.ipynb", "setup", "Data saved in " + CWD + r"\data\1\data.tsv.gz")
    d = derive(open_archive(root), b.uuids["cut"])
    assert d.runs.first_seen_in_notebook == {} and d.runs.unobserved == [1]


def test_materialize_close_and_background_task_ids(tmp_path):
    b = build_transcript()
    tid = b.call("Bash", {"command": "hera-watch data --next --follow", "run_in_background": True})
    b.result(tid, "Command running in background with ID: bxyz. Output is being written to: /tmp/x",
             {"stdout": "", "stderr": "", "interrupted": False, "backgroundTaskId": "bxyz"})
    b.bash("ls", "ok", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    d = derive(open_archive(root), b.uuids["late"])
    ep = materialize(open_archive(root), d, tmp_path / "ep", close="Got it. Reading run 0 now.")
    lines = (tmp_path / "ep" / ep["container"]["transcript"]).read_text().splitlines()
    last, cut = json.loads(lines[-1]), json.loads(lines[-2])
    assert cut["uuid"] == b.uuids["late"] and last["parentUuid"] == b.uuids["late"]
    assert last["type"] == "assistant" and last["message"]["model"] == "<synthetic>"
    assert last["message"]["content"] == [{"type": "text", "text": "Got it. Reading run 0 now."}]
    assert last["uuid"] == ep["resume"]["close_uuid"] and ep["resume"]["background_task_ids_stripped"] == 1
    started = next(json.loads(l) for l in lines if "bxyz" in l and '"toolUseResult"' in l)
    assert "backgroundTaskId" not in started["toolUseResult"] and "bxyz" in started["message"]["content"][0]["content"]
    ep2 = materialize(open_archive(root), d, tmp_path / "ep2")
    assert ep2["resume"] == {"close": None, "close_uuid": None, "background_task_ids_stripped": 1}
    assert json.loads((tmp_path / "ep2" / ep2["container"]["transcript"]).read_text().splitlines()[-1])["uuid"] == b.uuids["late"]


def test_heredoc_in_failed_bash_blanks_the_file(tmp_path):
    b = build_transcript()
    b.bash("cat > hera_scratch/take.md <<'EOF'\nx\nEOF\nnb-collab edit-cell x_ana.ipynb c1", "usage: nb-collab edit-cell", is_error=True)
    b.bash("ls", "ok", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    (root / "hera_scratch" / "take.md").write_text("x\n")
    d = derive(open_archive(root), b.uuids["late"])
    st = d.files["hera_scratch/take.md"]
    assert st.materialized and st.content == "" and "exited nonzero" in st.blanked and st.ops[-1]["unknown"]
    ep = materialize(open_archive(root), d, tmp_path / "ep")
    assert (tmp_path / "ep/session/hera_scratch/take.md").read_text() == ""
    assert [x["path"] for x in ep["transcript"]["targets"]["blanked"]] == ["hera_scratch/take.md"]


def test_unquoted_heredoc_with_expanding_path_is_logged(tmp_path):
    b = build_transcript()
    b.bash("for n in 1 2; do\ncat > hera_scratch/leg$n.py <<EOF\nprint($n)\nEOF\ndone", "")
    b.bash("ls", "ok", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    d = derive(open_archive(root), b.uuids["late"])
    assert "hera_scratch/leg$n.py" not in d.files
    assert d.targets.blanked == [{"line": d.targets.blanked[0]["line"], "path": "hera_scratch/leg$n.py",
                                  "reason": "the path has shell expansions; no file to attribute it to"}]


def test_sed_in_place_is_modelled(tmp_path):
    b = build_transcript()
    b.bash("cd hera_scratch && sed -i 's/import os/import sys/' probe.py && echo ok", "ok")
    b.bash("ls", "ok", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    (root / "hera_scratch" / "probe.py").write_text(PROBE.replace("import os", "import sys"))
    st = derive(open_archive(root), b.uuids["late"]).files["hera_scratch/probe.py"]
    assert st.content == PROBE.replace("import os", "import sys") and st.corroborated_by == "archived"
    assert st.ops[-1]["kind"] == "sed"


def test_sed_in_place_in_failed_bash_blanks_the_file(tmp_path):
    b = build_transcript()
    b.bash("sed -i 's/x/y/' hera_scratch/probe.py", "sed: -e expression #1, char 5: unterminated", is_error=True)
    b.bash("ls", "ok", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    st = derive(open_archive(root), b.uuids["late"]).files["hera_scratch/probe.py"]
    assert st.content == "" and st.blanked


def test_blanked_heredoc_recovers_at_a_later_full_read(tmp_path):
    b = build_transcript()
    b.bash("cat > hera_scratch/take.md <<EOF\n$HOME\nEOF", "")
    b.read(CWD + r"\hera_scratch\take.md", "/home/rig\n", label="reread")
    b.bash("ls", "ok", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    (root / "hera_scratch" / "take.md").write_text("/home/rig\n")
    st = derive(open_archive(root), b.uuids["late"]).files["hera_scratch/take.md"]
    assert st.materialized and st.content == "/home/rig\n"


def test_in_flight_run_is_dropped(tmp_path):
    b = build_transcript()
    b.bash("ls -d data/*", "data/0 data/1", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    d = derive(open_archive(root), b.uuids["late"])
    assert d.runs.kept == [0] and [r["id"] for r in d.runs.in_flight] == [1]


def test_reject_target_outside_session_and_corpus(tmp_path):
    b = build_transcript()
    b.read(r"C:\Users\rig\Documents\secret.md", "x", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    with pytest.raises(CutError, match=r"Read targets C:\\Users\\rig\\Documents\\secret.md, outside"):
        derive(open_archive(root), b.uuids["late"])


def test_cli_task_read_under_a_short_name_home(tmp_path):
    # The toploader's %TEMP% spells the home as C:\Users\TOPLOA~1; the task file
    # is known by its claude/<slug>/<session-id>/tasks tail, not the prefix.
    b = build_transcript()
    path = rf"C:\Users\RIG~1\AppData\Local\Temp\claude\C--Users-rig-x\{SID}\tasks\b1.output"
    b.read(path, "# armed on data", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    d = derive(open_archive(root), b.uuids["late"])
    assert d.targets.cli_task_outputs == {f"claude/C--Users-rig-x/{SID}/tasks/b1.output"}


def test_tmp_heredoc_is_volatile_and_skipped(tmp_path):
    b = build_transcript()
    b.bash("cat > /tmp/map_md.txt <<'EOF'\n# map\nEOF", "")
    b.bash("sed -i 's/a/b/' /tmp/map_md.txt", "")
    b.bash("ls", "ok", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    d = derive(open_archive(root), b.uuids["late"])
    assert d.targets.volatile == {"tmp/map_md.txt"}
    assert not [f for f in d.files if "map_md" in f]
    ep = materialize(open_archive(root), d, tmp_path / "ep")
    assert ep["transcript"]["targets"]["volatile"] == ["tmp/map_md.txt"]
    assert not (tmp_path / "ep/session/tmp").exists()


def test_tmp_write_tool_still_aborts(tmp_path):
    b = build_transcript()
    b.write("/tmp/x.md", "x", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    with pytest.raises(CutError, match="Write targets /tmp/x.md, outside"):
        derive(open_archive(root), b.uuids["late"])


def test_reject_write_into_corpus(tmp_path):
    b = build_transcript()
    b.write(r"C:\Users\rig\measurement_env\hera\recipes\x.md", "x", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    with pytest.raises(CutError, match="writes into ~/measurement_env"):
        derive(open_archive(root), b.uuids["late"])


def test_reject_write_to_as_archived_file(tmp_path):
    b = build_transcript()
    b.bash("cat >> hera_session.md <<'EOF'\nmore\nEOF", "ok", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    with pytest.raises(CutError, match="hera_session.md is archived as-is, but the agent wrote it"):
        derive(open_archive(root), b.uuids["late"])


def test_failed_edit_is_not_an_op(tmp_path):
    b = build_transcript()
    tid = b.call("Edit", {"file_path": CWD + r"\device_card.md", "old_string": "zzz", "new_string": "y"})
    b.result(tid, "String to replace not found in file.", None, label="late", is_error=True)
    root, _ = make_archive(tmp_path / "a", builder=b)
    d = derive(open_archive(root), b.uuids["late"])
    assert d.files["device_card.md"].content.endswith("ABA\n")


def test_downscaled_image_is_listed_not_written(tmp_path):
    b = build_transcript()
    tid = b.call("Read", {"file_path": CWD + r"\hera_scratch\big.png"})
    b.result(tid, [{"type": "image"}], {"type": "image", "file": {"base64": "AAAA", "type": "image/png", "originalSize": 999}}, label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    d = derive(open_archive(root), b.uuids["late"])
    st = d.files["hera_scratch/big.png"]
    assert not st.materialized and "downscaled" in st.reason


def test_cli_reports_cut_errors(archive, tmp_path):
    root, b = archive
    with pytest.raises(SystemExit, match="hera-replay cut: cut .* not a tool_result"):
        main(["cut", str(root), "--at", b.uuids["post-cut-call"], "--dest", str(tmp_path / "x")])


# --- corpus reads -------------------------------------------------------------

NDMAP_V0 = "# nD map\n\n## Recipe\n1. Sweep both gates.\n2. Fit the CNP line.\n"
NDMAP_V1 = "# nD map\n\n## Recipe\n1. Sweep both gates, slow axis first.\n2. Fit the CNP line.\n"
SPOT_V0 = "# SdH spot check\n\nNyquist at the high-field end.\n"
FS_MODEL = "# fs count\n\nF_L = (h/4e) n\n"
ND_MAP = "hera/recipes/measurements/nD-map.md"


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def write(repo, rel, text):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


@pytest.fixture
def corpus_repo(tmp_path):
    """Two corpus shas: the one the session read, and a later one that edits the
    nD-map recipe and drops the spot check."""
    repo = tmp_path / "corpus"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "t")
    write(repo, "hera/recipes/measurements/gatemap.md", "# Gatemap\n")
    write(repo, "hera/recipes/STYLE.md", "# Style\n")
    write(repo, ND_MAP, NDMAP_V0)
    write(repo, "hera/recipes/measurements/sdh-spot-check.md", SPOT_V0)
    write(repo, "hera/models/trilayer/README.md", FS_MODEL)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "session corpus")
    old = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    write(repo, ND_MAP, NDMAP_V1)
    (repo / "hera/recipes/measurements/sdh-spot-check.md").unlink()
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "later corpus")
    new = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    return repo, old, new


def crlf(text: str) -> str:
    """A rig `cat`: CRLF from the checkout, trailing newline trimmed by the CLI."""
    return text.replace("\n", "\r\n").rstrip("\r\n")


def corpus_transcript():
    """The read shapes the rule has to place, on top of the fixture's own two
    recipe Reads: a whole Read, a Read of one window through a Windows path, a
    `cat` behind a `cd` with CRLF output, and a `head`."""
    b = build_transcript()
    b.read("~/measurement_env/" + ND_MAP, NDMAP_V0, label="read-full")
    win_path = MENV + r"\hera\recipes\measurements\nD-map.md"
    tid = b.call("Read", {"file_path": win_path, "offset": 3, "limit": 2})
    window = NDMAP_V0.split("\n")[2:4]
    b.result(tid, "\n".join(f"{n}\t{l}" for n, l in enumerate(window, 3)),
             {"type": "text", "file": {"filePath": win_path, "content": "\n".join(window),
                                       "numLines": 2, "startLine": 3, "totalLines": 6}},
             label="read-window")
    b.bash("cd ~/measurements/zack/20260101-dev && cat ~/measurement_env/hera/recipes/measurements/sdh-spot-check.md",
           crlf(SPOT_V0), label="cat-spot")
    b.bash("cat /c/Users/rig/measurement_env/hera/models/trilayer/README.md", crlf(FS_MODEL), label="cat-model")
    b.bash("head -3 ~/measurement_env/hera/recipes/measurements/nD-map.md", "# nD map", label="head")
    b.bash("ls", "ok", label="late")
    return b


def corpus_episode(tmp_path, repo, sha, condition="full"):
    b = corpus_transcript()
    root, _ = make_archive(tmp_path / "a", builder=b)
    archive = open_archive(root)
    ep = materialize(archive, derive(archive, b.uuids["late"]), tmp_path / "ep",
                     corpus=None if sha is None else Corpus(sha, condition, repo))
    entries = {e["uuid"]: e for e in
               (json.loads(l) for l in (tmp_path / "ep" / ep["container"]["transcript"]).read_text().splitlines())}
    return b, ep, entries


def test_corpus_reads_serve_the_pinned_sha(tmp_path, corpus_repo):
    repo, _old, new = corpus_repo
    b, ep, entries = corpus_episode(tmp_path, repo, new)
    full = entries[b.uuids["read-full"]]
    assert full["toolUseResult"]["file"]["content"] == NDMAP_V1
    assert full["message"]["content"][0]["content"].splitlines()[3] == "4\t1. Sweep both gates, slow axis first."
    assert (full["toolUseResult"]["file"]["numLines"], full["toolUseResult"]["file"]["totalLines"]) == (6, 6)
    window = entries[b.uuids["read-window"]]
    assert window["toolUseResult"]["file"]["content"] == "## Recipe\n1. Sweep both gates, slow axis first."
    assert window["message"]["content"][0]["content"] == "3\t## Recipe\n4\t1. Sweep both gates, slow axis first."
    assert (window["toolUseResult"]["file"]["startLine"], window["toolUseResult"]["file"]["numLines"]) == (3, 2)
    assert entries[b.uuids["cat-model"]]["toolUseResult"]["stdout"] == crlf(FS_MODEL)
    reads = ep["transcript"]["corpus_reads"]
    assert (reads["mode"], reads["sha"], reads["condition"]) == ("corpus", new, "full")
    by_path = {(r["path"], r["tool"]): r for r in reads["rewritten"]}
    assert by_path[(ND_MAP, "Read")]["identical"] is False
    assert by_path[("hera/models/trilayer/README.md", "Bash")]["identical"] is True
    assert by_path[("hera/recipes/STYLE.md", "Read")]["identical"] is True
    assert [(r["tool"], r["paths"], "head" in r["reason"]) for r in reads["unrewritten"]] == \
        [("Bash", [ND_MAP], True)]


def test_corpus_reads_at_the_sessions_own_sha_are_identical(tmp_path, corpus_repo):
    repo, old, _new = corpus_repo
    b, ep, entries = corpus_episode(tmp_path, repo, old)
    assert all(r["identical"] for r in ep["transcript"]["corpus_reads"]["rewritten"])
    assert entries[b.uuids["read-full"]]["toolUseResult"]["file"]["content"] == NDMAP_V0
    assert entries[b.uuids["cat-spot"]]["toolUseResult"]["stdout"] == crlf(SPOT_V0)


def test_corpus_read_of_a_file_absent_at_the_sha_errors(tmp_path, corpus_repo):
    repo, _old, new = corpus_repo
    b, ep, entries = corpus_episode(tmp_path, repo, new)
    spot = entries[b.uuids["cat-spot"]]
    block = spot["message"]["content"][0]
    assert block["is_error"] and block["content"] == (
        "Exit code 1\ncat: /home/hera/measurement_env/hera/recipes/measurements/sdh-spot-check.md: "
        "No such file or directory")
    assert spot["toolUseResult"] == "Error: " + block["content"]
    record = next(r for r in ep["transcript"]["corpus_reads"]["rewritten"] if r["path"].endswith("sdh-spot-check.md"))
    assert record["missing_at_sha"] and record["substituted_sha256"] is None


def test_condition_none_empties_the_recipes_and_keeps_the_models(tmp_path, corpus_repo):
    repo, old, _new = corpus_repo
    b, ep, entries = corpus_episode(tmp_path, repo, old, condition="none")
    block = entries[b.uuids["read-full"]]["message"]["content"][0]
    assert block["is_error"] and block["content"] == (
        "File does not exist. Note: your current working directory is /home/hera/measurements/zack/20260101-dev.")
    assert entries[b.uuids["cat-model"]]["toolUseResult"]["stdout"] == crlf(FS_MODEL)
    missing = {r["path"] for r in ep["transcript"]["corpus_reads"]["rewritten"] if r.get("missing_at_sha")}
    assert missing == {ND_MAP, "hera/recipes/measurements/sdh-spot-check.md", "hera/recipes/STYLE.md",
                       "hera/recipes/measurements/gatemap.md"}


def test_archived_reads_are_the_default(tmp_path, corpus_repo):
    repo, _old, _new = corpus_repo
    b, ep, entries = corpus_episode(tmp_path, repo, None)
    assert ep["transcript"]["corpus_reads"] == {"mode": "archived"}
    assert entries[b.uuids["read-full"]]["toolUseResult"]["file"]["content"] == NDMAP_V0
    assert entries[b.uuids["cat-spot"]]["toolUseResult"]["stdout"] == crlf(SPOT_V0)


def test_cut_takes_the_corpus_from_the_case(tmp_path, corpus_repo, capsys, monkeypatch):
    repo, _old, new = corpus_repo
    b = corpus_transcript()
    root, _ = make_archive(tmp_path / "a", builder=b)
    case = tmp_path / "c.yaml"
    case.write_text(yaml.safe_dump({
        "case": "x", "source": str(root), "cut": {"transcript": f"{SID}.jsonl", "at": b.uuids["late"]},
        "corpus": {"sha": new, "condition": "full", "reads": "corpus"},
        "run": {"model": "claude-sonnet-5", "effort": "medium", "n": 1, "timeout_s": 60, "stall_s": 60, "max_turns": 5},
        "allowed_tools": ["Bash"], "grader": None,
        "resume": {"close": "Recipes read.", "prompt": "Carry on."},
    }))
    monkeypatch.setattr("hera.replay.rewrite.REPO_ROOT", repo)
    assert main(["cut", "--case", str(case), "--dest", str(tmp_path / "ep")]) == 0
    out = capsys.readouterr().out
    assert f"corpus:  reads at {new} (full): 6 substituted (3 identical), 1 left archived" in out
    ep = json.loads((tmp_path / "ep" / "episode.json").read_text())
    assert ep["resume"]["close"] == "Recipes read."


def _strip_end_time(root, rid: int, mtime):
    """A run the sweep never closed: no end_time, files last written at `mtime`."""
    d = root / "data" / str(rid)
    meta = json.loads((d / "metadata.json").read_text())
    del meta["end_time"]
    (d / "metadata.json").write_text(json.dumps(meta))
    for p in d.iterdir():
        os.utime(p, (mtime.timestamp(), mtime.timestamp()))


def test_run_without_end_time_is_kept_when_its_last_write_precedes_the_cut(tmp_path):
    b = build_transcript()
    b.bash("ls -d data/*", "data/0 data/1", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    last_write = T0 + timedelta(seconds=b.index("late") - 1)
    _strip_end_time(root, 1, last_write)
    d = derive(open_archive(root), b.uuids["late"])
    assert d.runs.kept == [0, 1] and d.runs.in_flight == []
    assert d.runs.end_from_mtime == {1: last_write.isoformat()}
    ep = materialize(open_archive(root), d, tmp_path / "ep")
    assert ep["runs"]["end_from_mtime"] == {"1": last_write.isoformat()}
    assert (tmp_path / "ep" / "session" / "data" / "1" / "metadata.json").is_file()


def test_run_without_end_time_still_writing_at_the_cut_is_in_flight(tmp_path):
    b = build_transcript()
    b.bash("ls -d data/*", "data/0 data/1", label="seen")
    b.bash("ls", "ok", label="tail")
    root, _ = make_archive(tmp_path / "a", builder=b)
    _strip_end_time(root, 1, T0 + timedelta(seconds=b.index("seen") + 1))
    d = derive(open_archive(root), b.uuids["seen"])
    assert d.runs.kept == [0] and [r["id"] for r in d.runs.in_flight] == [1] and 1 in d.runs.end_from_mtime


def test_run_without_end_time_refuses_checkout_mtimes(tmp_path):
    b = build_transcript()
    b.bash("ls -d data/*", "data/0 data/1", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    _strip_end_time(root, 1, T0 + timedelta(seconds=len(b.lines) + 1000))
    with pytest.raises(CutError, match=r"data/1/metadata.json has no end_time and every file in data/1/ is newer than the transcript"):
        derive(open_archive(root), b.uuids["late"])




_SCRIPT = ("python - <<'PYEOF'\nimport io\np='hera_scratch/probe.py'\ns=io.open(p,encoding='utf-8').read()\n"
           "s=s.replace(\"print('probe')\",\"print('probe2')\")\ns += \"# patched\\n\"\nio.open(p,'w',encoding='utf-8').write(s)\nprint('ok')\nPYEOF")


def test_python_script_edits_are_replayed_like_sed(tmp_path):
    b = build_transcript()
    b.bash(_SCRIPT + "\ncat >> hera_scratch/probe.py <<'EOF'\n# after\nEOF", "ok")
    b.bash("ls", "ok", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    final = PROBE.replace("print('probe')", "print('probe2')") + "# patched\n# after\n"
    (root / "hera_scratch" / "probe.py").write_text(final)
    st = derive(open_archive(root), b.uuids["late"]).files["hera_scratch/probe.py"]
    assert st.content == final and st.corroborated_by == "archived"
    assert [o["kind"] for o in st.ops][-2:] == ["script", "heredoc"]


def test_python_script_replace_has_str_replace_semantics(tmp_path):
    # Absent old text is a no-op; present text is replaced everywhere, as the script did.
    b = build_transcript()
    b.bash(_SCRIPT.replace("print('probe')", "no such text"), "ok")
    b.bash("ls", "ok", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    (root / "hera_scratch" / "probe.py").write_text(PROBE + "# patched\n")
    st = derive(open_archive(root), b.uuids["late"]).files["hera_scratch/probe.py"]
    assert st.content == PROBE + "# patched\n" and st.blanked is None


def test_truth_point_after_the_cut_supersedes_an_unmodelled_change_before_it(tmp_path):
    b = build_transcript()
    b.bash("ls", "ok", label="inside")
    b.edit(r"C:\Users\rig\measurements\zack\20260101-dev\hera_scratch\probe.py", PROBE + "# by a script\n", "probe", "probe2", label="edit")
    b.bash("ls", "ok", label="after")
    root, _ = make_archive(tmp_path / "a", builder=b)
    final = PROBE.replace("probe", "probe2") + "# by a script\n"
    (root / "hera_scratch" / "probe.py").write_text(final)
    st = derive(open_archive(root), b.uuids["after"]).files["hera_scratch/probe.py"]
    assert st.content == final and (st.ops[-1]["kind"], st.ops[-1]["supersedes"]) == ("edit", "start")
    with pytest.raises(CutError, match="hera_scratch/probe.py: content at edit@.* differs from the forward reconstruction"):
        derive(open_archive(root), b.uuids["inside"])


def _set_mtime(path, when):
    os.utime(path, (when.timestamp(), when.timestamp()))


def test_archived_file_stands_in_for_an_unmodelled_change_before_the_cut(tmp_path):
    b = build_transcript()
    b.bash("ls", "ok", label="late")
    root, _ = make_archive(tmp_path / "a", builder=b)
    probe = root / "hera_scratch" / "probe.py"
    probe.write_text(PROBE + "# spliced by a script\n")
    _set_mtime(probe, T0 + timedelta(seconds=b.index("late") - 1))
    st = derive(open_archive(root), b.uuids["late"]).files["hera_scratch/probe.py"]
    assert st.content == PROBE + "# spliced by a script\n" and st.corroborated_by == "archived"
    assert st.basis.startswith("archived: an unmodelled change after ")


def test_archived_file_changed_after_the_cut_by_unmodelled_means_is_refused(tmp_path):
    b = build_transcript()
    b.bash("ls", "ok", label="late")
    b.bash("ls", "ok", label="tail")
    root, _ = make_archive(tmp_path / "a", builder=b)
    probe = root / "hera_scratch" / "probe.py"
    probe.write_text(PROBE + "# spliced by a script\n")
    for when in (T0 + timedelta(seconds=b.index("late") + 1), T0 + timedelta(seconds=len(b.lines) + 1000)):
        _set_mtime(probe, when)
        with pytest.raises(CutError, match="hera_scratch/probe.py: content at archive differs from the forward reconstruction"):
            derive(open_archive(root), b.uuids["late"])
