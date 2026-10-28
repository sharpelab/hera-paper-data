"""Unit tests for the replay tools' pure pieces: the path rewrite, the project
slug, handoff detection, heredoc parsing, run-id extraction, and the stop hook."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from hera.replay.errors import CutError
from hera.replay.rewrite import PathRewriter, corpus_rel
from hera.replay.transcript import RigLayout, handoff_invocation, parse_heredocs, project_slug, run_ids_in

HOOK = Path(__file__).resolve().parents[2] / "src/hera/replay/episode_stop.py"


@pytest.fixture
def layout() -> RigLayout:
    return RigLayout.from_cwd(r"C:\Users\DGG\VTI_local_data\zack\20260619.3-QC0426")


def test_layout_from_windows_cwd(layout):
    assert layout.style == "windows"
    assert layout.home == r"C:\Users\DGG"
    assert layout.user == "zack" and layout.session == "20260619.3-QC0426"
    assert layout.container_session_dir == "/home/hera/measurements/zack/20260619.3-QC0426"
    assert layout.container_projects_slug == "-home-hera-measurements-zack-20260619-3-QC0426"


def test_layout_from_posix_cwd():
    l = RigLayout.from_cwd("/home/toploader/measurements/Isaac/b1c2_toploader")
    assert l.style == "posix" and l.home == "/home/toploader"
    assert l.user == "Isaac" and l.session == "b1c2_toploader"


def test_layout_rejects_shallow_cwd():
    with pytest.raises(CutError):
        RigLayout.from_cwd(r"C:\Users\DGG\solo")


def test_project_slug_replaces_every_non_alphanumeric():
    assert project_slug("/home/zack/measurements/Isaac/b1c2_toploader") == "-home-zack-measurements-Isaac-b1c2-toploader"


@pytest.mark.parametrize("src, expected", [
    (r"C:\Users\DGG\VTI_local_data\zack\20260619.3-QC0426\hera_scratch\a.py", "/home/hera/measurements/zack/20260619.3-QC0426/hera_scratch/a.py"),
    ("/c/Users/DGG/VTI_local_data/zack/20260619.3-QC0426/device_card.md", "/home/hera/measurements/zack/20260619.3-QC0426/device_card.md"),
    ("C:/Users/DGG/VTI_local_data/zack/20260619.3-QC0426", "/home/hera/measurements/zack/20260619.3-QC0426"),
    ("cd ~/VTI_local_data/zack/20260619.3-QC0426 && ls", "cd ~/measurements/zack/20260619.3-QC0426 && ls"),
    ("cd ~/measurement_env/../VTI_local_data/zack/20260619.3-QC0426 && ls", "cd ~/measurements/zack/20260619.3-QC0426 && ls"),
    ("cat ~/measurement_env/hera/recipes/x.md", "cat ~/measurement_env/hera/recipes/x.md"),
    (r"C:\Users\DGG\measurement_env\hera\recipes\x.md", "/home/hera/measurement_env/hera/recipes/x.md"),
    (r"written to: C:\Users\DGG\AppData\Local\Temp\claude\t.output. You will", "written to: /home/hera/AppData/Local/Temp/claude/t.output. You will"),
    (r"C:\Users\DGG~1\AppData\Local\Temp\claude\C--x\s\tasks\t.output", "/home/hera/AppData/Local/Temp/claude/C--x/s/tasks/t.output"),
    (r"C:\Users\DGG~1\Documents\x", r"C:\Users\DGG~1\Documents\x"),
    ("~/.bashrc", "~/.bashrc"),
    ("http://localhost:8899/api", "http://localhost:8899/api"),
])
def test_rewrite(layout, src, expected):
    assert PathRewriter(layout)(src) == expected


def test_rewrite_tally_classes(layout):
    rw = PathRewriter(layout)
    rw(r"C:\Users\DGG\VTI_local_data\zack\20260619.3-QC0426\x C:\Users\DGG\measurement_env\y C:\Users\DGG\AppData\z. ~/VTI_local_data/zack/20260619.3-QC0426/w")
    tally = rw.tally.as_json()
    assert (tally["session_dir"], tally["measurement_env"], tally["home_other"], tally["tilde_session_dir"]) == (1, 1, 1, 1)
    assert tally["home_other_paths"] == ["/home/hera/AppData/z"]


def test_rewrite_ignores_base64_lookalikes(layout):
    s = "iVBORw0K/c/Users/DGG/VTI_local_data/zack/20260619.3-QC0426/abc"
    assert PathRewriter(layout)(s) == s


@pytest.mark.parametrize("path, expected", [
    (r"C:\Users\DGG\measurement_env\hera\recipes\measurements\gatemap.md", "hera/recipes/measurements/gatemap.md"),
    ("/c/Users/DGG/measurement_env/hera/recipes/measurements/gatemap.md", "hera/recipes/measurements/gatemap.md"),
    ("~/measurement_env/hera/crops/gatemap/qc0426.md", "hera/crops/gatemap/qc0426.md"),
    ("hera/models/trilayer_fs_count/fs_count_b0.py", "hera/models/trilayer_fs_count/fs_count_b0.py"),
    ("'~/measurement_env/hera/recipes/STYLE.md'", "hera/recipes/STYLE.md"),
    ("~/measurement_env/hera/rig-cards/VTI.md", None),
    ("~/VTI_local_data/zack/20260619.3-QC0426/hera_scratch/recipes.md", None),
])
def test_corpus_rel_matches_on_the_tail(path, expected):
    assert corpus_rel(path) == expected


@pytest.mark.parametrize("command, expected", [
    ("nb-collab execute-cell x_measure.ipynb aaaa0001 --timeout 60", "nb-collab execute-cell x_measure.ipynb aaaa0001 --timeout 60"),
    ("cd ~/x && nb-collab wait x_measure.ipynb aaaa0001 2>/dev/null | tail -3", "nb-collab wait x_measure.ipynb aaaa0001"),
    ("nb-collab exec-all x_measure.ipynb", "nb-collab exec-all x_measure.ipynb"),
    ("nb-collab execute-cell --help", None),
    ("nb-collab append x_measure.ipynb --code-file a.py", None),
    ('nb-collab append x_measure.ipynb --summary "a; b | c" --code-file a.py --execute --timeout 10', 'nb-collab append x_measure.ipynb --summary a; b | c --code-file a.py --execute --timeout 10'),
    ("cat > n.md <<'EOF'\nuse nb-collab execute-cell x_measure.ipynb later\nEOF", None),
    ("for c in a b; do nb-collab execute-cell x_measure.ipynb $c; done", "nb-collab execute-cell x_measure.ipynb $c"),
    ("nb-collab execute-cell x_ana.ipynb bbbb0001 --timeout 120 | tail -8", None),
    ("nb-collab --help | head", None),
    ("nb-collab append x_ana.ipynb --code-file a.py --execute\nnb-collab append x_measure.ipynb --code-file b.py", None),
    ("nb-collab append x_measure.ipynb \\\n  --code-file a.py \\\n  --execute", "nb-collab append x_measure.ipynb --code-file a.py --execute"),
])
def test_handoff_invocation(command, expected):
    assert handoff_invocation(command) == expected


def test_parse_sed_in_place():
    from hera.replay.transcript import parse_sed_in_place
    one = parse_sed_in_place("cd hera_scratch && sed -i 's/a/b/' x.py && python x.py")
    assert len(one) == 1 and one[0].files == ["x.py"] and one[0].argv == ["s/a/b/"] and one[0].cd == "hera_scratch"
    two = parse_sed_in_place("sed -i.bak -E -e 's/a/b/' -e '7,9d' a.py b.py")
    assert two[0].files == ["a.py", "b.py"] and two[0].argv == ["-E", "-e", "s/a/b/", "-e", "7,9d"]
    assert parse_sed_in_place("sed 's/a/b/' x.py > y.py") == []
    assert parse_sed_in_place("sed -n '1,3p' x.py") == []
    nl = parse_sed_in_place('menv python -c "\nimport x\n" 2>&1 | grep -v W\nsed -i "s/a/b/; s/c/d/" f.py; grep -n CAL f.py')
    assert len(nl) == 1 and nl[0].files == ["f.py"] and nl[0].argv == ["s/a/b/; s/c/d/"]
    cont = parse_sed_in_place("sed -i 's/a/b/' \\\n  x.py")
    assert len(cont) == 1 and cont[0].files == ["x.py"]


def test_never_read_session_notes_are_appends_only(tmp_path):
    from hera.replay.derive import FileOp, reconstruct
    from hera.replay.errors import CutError
    head = "# Session notes — dev / VTI\n\nOperational log.\n"
    ops = [FileOp(index=5, kind="heredoc", rel="session_notes.md", content="- a\n", append=True),
           FileOp(index=9, kind="heredoc", rel="session_notes.md", content="- b\n", append=True)]
    archived = tmp_path / "session_notes.md"
    archived.write_text(head + "- a\n- b\n")
    st = reconstruct("session_notes.md", ops, 6, archived)
    assert st.content == "- a\n" and st.basis.startswith("appends only") and st.corroborated_by == "archived"
    archived.write_text(head + "- a\n- b\n\n## added after the session\n")
    with pytest.raises(CutError, match="content at archive differs"):
        reconstruct("session_notes.md", ops, 6, archived)
    # Any other file appended before the harness saw it created is unknown at the
    # cut: blank without a dated archive, the archived text when its mtime
    # precedes the cut.
    other = [FileOp(index=5, kind="heredoc", rel="hera_scratch/log.md", content="- a\n", append=True)]
    log = tmp_path / "log.md"
    log.write_text("# made by a redirect\n- a\n")
    st = reconstruct("hera_scratch/log.md", other, 6, log)
    assert st.content == "" and "before any baseline" in st.blanked
    from datetime import datetime, timedelta, timezone
    later = datetime.now(timezone.utc) + timedelta(hours=1)
    st = reconstruct("hera_scratch/log.md", other, 6, log, cut_ts=later, snapshot=later)
    assert st.content == "# made by a redirect\n- a\n" and st.corroborated_by == "archived" and st.blanked is None
    st = reconstruct("hera_scratch/log.md", other, 6, log, cut_ts=later - timedelta(hours=2), snapshot=later)
    assert st.content == "" and st.blanked


def test_parse_heredocs():
    hds = parse_heredocs("cd ~/s && cat >> notes.md <<'EOF'\n- a\n- b\nEOF\necho done")
    assert len(hds) == 1
    assert (hds[0].path, hds[0].append, hds[0].body, hds[0].cd) == ("notes.md", True, "- a\n- b\n", "~/s")
    assert parse_heredocs("cat > a.md <<EOF\nplain\nEOF")[0].body == "plain\n"
    assert parse_heredocs("menv python - <<'EOF'\nprint(1)\nEOF") == []
    unknown = parse_heredocs("cat > a.md <<EOF\n$HOME\nEOF")[0]
    assert unknown.body is None and "shell expansions" in unknown.reason
    assert parse_heredocs("cat > a.md <<-'EOF'\n\tx\nEOF")[0].body is None


def test_run_ids_in():
    text = ("Starting sweep with ID 7\nData saved in C:\\x\\data\\7\\data.tsv.gz\n# armed on data — waiting (known runs: 0, 1, 2) …\n"
            "# 3  1D  sdh-spot-check\nrun 4\n  type: 1D\nrun 5: axis=x")
    assert run_ids_in(text) == [7, 0, 1, 2, 3, 4]


def _run_hook(payload: dict, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True, text=True,
                          cwd=cwd, env={"CLAUDE_PROJECT_DIR": str(cwd), "PATH": ""})


def test_hook_leaves_nb_collab_to_the_stub(tmp_path):
    p = _run_hook({"tool_name": "Bash", "tool_input": {"command": "cd x && nb-collab execute-cell m_measure.ipynb aaaa0001 --timeout 5 2>/dev/null"}, "tool_use_id": "toolu_1"}, tmp_path)
    assert p.returncode == 0 and p.stdout == ""
    assert not (tmp_path / "episode-stop.json").exists()


def test_hook_passes_one_measure_append_after_a_watch(tmp_path):
    marker = tmp_path / "episode-stop.json"
    marker.write_text('{"tool": "hera-watch", "invocation": "hera-watch"}')
    append = {"tool_name": "Bash", "tool_input": {"command": "nb-collab append m_measure.ipynb \\\n  --code-file fan.py --execute --timeout 9000"}, "tool_use_id": "toolu_a"}
    p = _run_hook({"tool_name": "Bash", "tool_input": {"command": "nb-collab append m_ana.ipynb --code-file a.py"}}, tmp_path)
    assert json.loads(p.stdout)["continue"] is False
    marker.write_text('{"tool": "hera-watch", "invocation": "hera-watch"}')
    p = _run_hook(append, tmp_path)
    assert p.returncode == 0 and p.stdout == ""
    assert json.loads(marker.read_text())["append_pass"] == "toolu_a"
    p = _run_hook(append, tmp_path)
    assert json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
    marker.write_text('{"tool": "nb-collab", "invocation": "nb-collab execute-cell m_measure.ipynb x"}')
    assert json.loads(_run_hook(append, tmp_path).stdout)["continue"] is False


def test_hook_ends_every_call_once_the_marker_exists(tmp_path):
    (tmp_path / "episode-stop.json").write_text('{"invocation": "hera-watch"}')
    p = _run_hook({"tool_name": "Bash", "tool_input": {"command": "ls data/"}}, tmp_path)
    out = json.loads(p.stdout)
    assert out["continue"] is False and out["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert (tmp_path / "episode-stop.json").read_text() == '{"invocation": "hera-watch"}'


def test_hook_stops_on_wait_tools(tmp_path):
    p = _run_hook({"tool_name": "ScheduleWakeup", "tool_input": {"delaySeconds": 240, "reason": "confirm start"}, "tool_use_id": "toolu_w"}, tmp_path)
    assert json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
    marker = json.loads((tmp_path / "episode-stop.json").read_text())
    assert marker["tool"] == "ScheduleWakeup" and marker["invocation"] == "ScheduleWakeup" and marker["cell_ids"] == []
    p = _run_hook({"tool_name": "Monitor", "tool_input": {"command": "tail -f x"}}, tmp_path)
    assert json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_hook_passes_other_commands(tmp_path):
    p = _run_hook({"tool_name": "Bash", "tool_input": {"command": "nb-collab append m_measure.ipynb --code-file a.py"}}, tmp_path)
    assert p.returncode == 0 and p.stdout == ""
    assert not (tmp_path / "episode-stop.json").exists()
    p = _run_hook({"tool_name": "Read", "tool_input": {"file_path": "x"}}, tmp_path)
    assert p.returncode == 0 and p.stdout == ""


NB_STUB = Path(__file__).resolve().parents[2] / "src/hera/replay/stubs/nb-collab"


def _run_nb_stub(args: list[str], tmp_path: Path) -> subprocess.CompletedProcess:
    """The stub with a fake `uv` on PATH that echoes the argv the real tool would get."""
    bindir = tmp_path / "bin"
    bindir.mkdir(exist_ok=True)
    fake = bindir / "uv"
    fake.write_text("#!/bin/sh\necho \"REAL: $*\"\necho \"  appended code @ 4 id=cafe0001\"\n")
    fake.chmod(0o755)
    return subprocess.run([sys.executable, str(NB_STUB), *args], capture_output=True, text=True, cwd=tmp_path,
                          env={"HERA_EPISODE_DIR": str(tmp_path), "PATH": f"{bindir}:/usr/bin:/bin", "HOME": str(tmp_path)})


def test_nb_stub_lands_the_append_without_the_execute(tmp_path):
    p = _run_nb_stub(["append", "m_measure.ipynb", "--markdown", "## fan; a | b", "--code-file", "fan.py", "--execute", "--timeout", "9000"], tmp_path)
    assert p.returncode == 0
    real = p.stdout.splitlines()[0]
    assert real.endswith("nb-collab append m_measure.ipynb --markdown ## fan; a | b --code-file fan.py")
    marker = json.loads((tmp_path / "episode-stop.json").read_text())
    assert marker["tool"] == "nb-collab" and "--execute" in marker["invocation"]
    assert marker["append_landed"]["cell_ids"] == ["cafe0001"]


def test_nb_stub_never_executes_on_the_measure_notebook(tmp_path):
    p = _run_nb_stub(["execute-cell", "m_measure.ipynb", "aaaa0001", "--timeout", "60"], tmp_path)
    assert p.stdout == "episode complete\n"
    marker = json.loads((tmp_path / "episode-stop.json").read_text())
    assert marker["cell_ids"] == ["aaaa0001"] and "append_landed" not in marker


def test_nb_stub_passes_everything_else_through(tmp_path):
    for args in (["append", "m_measure.ipynb", "--code-file", "a.py"], ["execute-cell", "m_ana.ipynb", "bbbb0001", "--timeout", "120"],
                 ["append", "m_ana.ipynb", "--code-file", "a.py", "--execute"], ["execute-cell", "--help"]):
        p = _run_nb_stub(args, tmp_path)
        assert p.stdout.splitlines()[0] == "REAL: run --no-sync --project " + str(tmp_path / "measurement_env") + " nb-collab " + " ".join(args)
    assert not (tmp_path / "episode-stop.json").exists()


def test_two_watches_armed_before_the_append_leave_the_handoff_to_nb_collab(tmp_path):
    # vti02-fan-design-fable-corpus e23jh3/00: a --follow watch and a checkpoint
    # watch backgrounded before the fan's `append --execute`.
    _watch_episode(tmp_path, cells=BASE_CELLS)
    env = dict(os.environ, HERA_EPISODE_DIR=str(tmp_path))
    watches = [subprocess.Popen([sys.executable, str(_HERA_WATCH_STUB), *argv], cwd=tmp_path, env=env,
                                stdout=subprocess.PIPE, text=True)
               for argv in (["data", "--next", "--follow"], ["data", "--next", "--timeout", "1500", "--wait-start", "1500"])]
    try:
        for w in watches:
            assert w.stdout.readline().startswith("# armed on data")
        second = _run_hook({"tool_name": "Bash", "tool_input": {"command": "hera-watch data --next --timeout 1500 --wait-start 1500"}}, tmp_path)
        assert second.stdout == "" and not (tmp_path / "episode-stop.json").exists()
        p = _run_nb_stub(["append", "m_measure.ipynb", "--markdown-file", "md_fan.md", "--code-file", "cell_fan.py", "--execute"], tmp_path)
        assert p.returncode == 0
        time.sleep(3)  # past the watches' poll
        marker = json.loads((tmp_path / "episode-stop.json").read_text())
        assert marker["tool"] == "nb-collab" and marker["append_landed"]["cell_ids"] == ["cafe0001"]
        assert all(w.poll() is None for w in watches)
    finally:
        for w in watches:
            w.kill()
            w.wait()


def test_nb_stub_logs_each_landed_measure_append_for_the_watch_stub(tmp_path):
    _run_nb_stub(["append", "m_measure.ipynb", "--code-file", "a.py"], tmp_path)
    assert not (tmp_path / ".claude").exists()  # no session harness, no log
    (tmp_path / ".claude").mkdir()
    _run_nb_stub(["append", "m_measure.ipynb", "--code-file", "a.py"], tmp_path)
    _run_nb_stub(["append", "m_ana.ipynb", "--code-file", "a.py"], tmp_path)
    (line,) = (tmp_path / ".claude" / "measure_appends.jsonl").read_text().splitlines()
    assert json.loads(line)["cells"] == [{"kind": "code", "id": "cafe0001"}]


def test_nb_stub_after_a_watch_keeps_the_watch_marker(tmp_path):
    (tmp_path / "episode-stop.json").write_text('{"tool": "hera-watch", "invocation": "hera-watch"}')
    _run_nb_stub(["append", "m_measure.ipynb", "--code-file", "fan.py", "--execute"], tmp_path)
    marker = json.loads((tmp_path / "episode-stop.json").read_text())
    assert marker["tool"] == "hera-watch" and marker["append_landed"]["cell_ids"] == ["cafe0001"]


SCRIPT = """python - <<'PYEOF'
import io
p='hera_scratch/plan.md'
s=io.open(p,encoding='utf-8').read()
s=s.replace("old text","new text")
s += \"\"\"
## Live update
\"\"\"
io.open(p,'w',encoding='utf-8').write(s)
print('plan updated')
PYEOF
tail -2 hera_scratch/plan.md"""


def test_parse_python_scripts_reads_the_literal_edit_idiom():
    from hera.replay.transcript import parse_python_scripts
    (sc,) = parse_python_scripts(SCRIPT)
    assert sc.path == "hera_scratch/plan.md" and sc.pos == 0
    assert sc.edits == (("replace", "old text", "new text"), ("append", "\n## Live update\n"))
    (sc,) = parse_python_scripts("cd hera_scratch && menv " + SCRIPT.replace("hera_scratch/plan.md", "plan.md"))
    assert sc.cd == "hera_scratch" and sc.path == "plan.md"
    two = parse_python_scripts(SCRIPT + "\n" + SCRIPT.replace("plan.md", "notes.md"))
    assert [s.path for s in two] == ["hera_scratch/plan.md", "hera_scratch/notes.md"] and two[0].pos < two[1].pos


def test_parse_python_scripts_ignores_every_other_script():
    from hera.replay.transcript import parse_python_scripts
    assert parse_python_scripts(SCRIPT.replace("s=s.replace(\"old text\",\"new text\")", "s=re.sub('a','b',s)")) == []
    loop = "menv python - <<'EOF'\np='hera_scratch/cell.py'; s=open(p,encoding='utf-8').read()\nfor k,v in {'__A__':'1','__B__':'2'}.items(): s=s.replace(k,v)\nopen(p,'w',encoding='utf-8').write(s); print('left:', s.count('__'))\nEOF"
    (sc,) = parse_python_scripts(loop)
    assert sc.edits == (("replace", "__A__", "1"), ("replace", "__B__", "2"))
    assert parse_python_scripts(loop.replace("'2'", "str(2)")) == []
    assert parse_python_scripts(loop.replace("s=s.replace(k,v)", "s=s.replace(v,k)")) == []
    assert parse_python_scripts(SCRIPT.replace("<<'PYEOF'", "<<PYEOF")) == []
    assert parse_python_scripts(SCRIPT.replace("encoding='utf-8').write(s)", "encoding='utf-8').write(s + 'x')")) == []
    assert parse_python_scripts(SCRIPT.replace("io.open(p,'w',encoding='utf-8')", "io.open(p,'wb')")) == []


STUB_WATCH = Path(__file__).resolve().parents[2] / "src/hera/replay/stubs/hera-watch"


def _run_stub(tmp_path, argv, fake_real: bool = True):
    import os, subprocess
    home = tmp_path / "home"
    real = home / "measurement_env/.venv/bin/hera-watch"
    if fake_real:
        real.parent.mkdir(parents=True, exist_ok=True)
        real.write_text("#!/bin/sh\necho \"real hera-watch $@\"\n")
        real.chmod(0o755)
    episode = tmp_path / "episode"
    episode.mkdir(exist_ok=True)
    env = {**os.environ, "HOME": str(home), "HERA_EPISODE_DIR": str(episode)}
    try:
        r = subprocess.run([sys.executable, str(STUB_WATCH), *argv], cwd=tmp_path, env=env,
                           capture_output=True, text=True, timeout=3)
        return r.stdout + r.stderr, (episode / "episode-stop.json").exists()
    except subprocess.TimeoutExpired as ex:
        return (ex.stdout or b"").decode(), (episode / "episode-stop.json").exists()


def test_hera_watch_stub_reads_a_landed_run_through_the_real_tool(tmp_path):
    (tmp_path / "data" / "6").mkdir(parents=True)
    (tmp_path / "data" / "6" / "metadata.json").write_text("{}")
    out, stopped = _run_stub(tmp_path, ["data/6", "--once"])
    assert "real hera-watch data/6 --once" in out and not stopped
    out, stopped = _run_stub(tmp_path, ["--poll", "2", "data/6"])
    assert "real hera-watch --poll 2 data/6" in out and not stopped


def test_hera_watch_stub_without_a_baseline_arms_at_once(tmp_path):
    (tmp_path / "data").mkdir()
    out, stopped = _run_stub(tmp_path, ["data", "--next", "--follow"])
    assert "armed on data" in out and stopped
    out, stopped = _run_stub(tmp_path / "b", ["data/9", "--once"])
    assert "armed on data" in out and stopped


# --- mask: appended operator cells ------------------------------------------------
from datetime import datetime, timedelta, timezone

import nbformat

from hera.replay.mask import apply_mask, load_mask, parse_duration

CUT_TS = datetime(2026, 8, 22, 6, 55, 27, 619000, tzinfo=timezone.utc)


def _toy_session(tmp_path: Path) -> Path:
    session = tmp_path / "session"
    session.mkdir(parents=True)
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_markdown_cell("# Measure", id="aaaaaaaa"),
                nbformat.v4.new_code_cell("x = 1", id="bbbbbbbb", execution_count=7),
                nbformat.v4.new_code_cell("y = 2", id="cccccccc", execution_count=None)]
    nb.cells[1]["metadata"]["hera"] = {"appended_at": "2026-08-22T06:50:04+00:00", "v": "v0"}
    (session / "x_measure.ipynb").write_text(nbformat.writes(nb), encoding="utf-8")
    return session


def _mask(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "mask.yaml"
    p.write_text(text, encoding="utf-8")
    return p


def test_mask_drops_a_notebook_cell(tmp_path):
    session = _toy_session(tmp_path)
    mask = load_mask(_mask(tmp_path, "drop:\n  - x_measure.ipynb#cccccccc\n"))
    record = apply_mask(mask, session, CUT_TS)
    nb = json.loads((session / "x_measure.ipynb").read_text(encoding="utf-8"))
    nbformat.validate(nbformat.from_dict(nb))
    assert [c["id"] for c in nb["cells"]] == ["aaaaaaaa", "bbbbbbbb"] and record["dropped"] == ["x_measure.ipynb#cccccccc"]
    with pytest.raises(CutError, match="0 such cells"):
        apply_mask(load_mask(_mask(tmp_path, "drop:\n  - x_measure.ipynb#dddddddd\n")), session, CUT_TS)
    with pytest.raises(CutError, match="cell drop is"):
        load_mask(_mask(tmp_path, "drop:\n  - hera_scratch/x.md#abc\n"))


def test_mask_append_lands_operator_cells_and_moves_the_clock(tmp_path):
    session = _toy_session(tmp_path)
    mask = load_mask(_mask(tmp_path, """
append:
  - notebook: x_measure.ipynb
    cells:
      - markdown: |
          ## Operator
        duration: 2m
      - code: |
          close_out((magnet.field, 0.0), restore=state0)
        output: |
          -- restore (19 params)
          field : 0.0034 T
        duration: 73m
"""))
    assert mask.duration_s == 75 * 60
    record = apply_mask(mask, session, CUT_TS)
    nb = json.loads((session / "x_measure.ipynb").read_text(encoding="utf-8"))
    nbformat.validate(nbformat.from_dict(nb))
    md, code = nb["cells"][-2], nb["cells"][-1]
    # As JupyterLab leaves an operator's cells: 8-hex ids, no hera stamps, the
    # markdown bare, the code cell executed once after the last count.
    assert md["cell_type"] == "markdown" and md["source"] == "## Operator" and md["metadata"] == {}
    assert code["cell_type"] == "code" and code["execution_count"] == 8 and "hera" not in code["metadata"]
    assert code["outputs"] == [{"output_type": "stream", "name": "stdout", "text": "-- restore (19 params)\nfield : 0.0034 T\n"}]
    assert all(len(c["id"]) == 8 and c["id"] != "aaaaaaaa" for c in (md, code))
    ex = code["metadata"]["execution"]
    assert ex["iopub.execute_input"] == ex["iopub.status.busy"] == ex["shell.execute_reply.started"] == "2026-08-22T06:57:27.619000Z"
    assert ex["iopub.status.idle"] == ex["shell.execute_reply"] == "2026-08-22T08:10:27.619000Z"
    # The record: each cell's window, and the clock at the end of the last one.
    assert [(a["id"], a["cell_type"], a["index"]) for a in record["appended"]] == [(md["id"], "markdown", 3), (code["id"], "code", 4)]
    assert record["appended"][0]["start"] == CUT_TS.isoformat()
    assert record["appended"][1]["start"] == (CUT_TS + timedelta(minutes=2)).isoformat()
    assert record["clock"] == record["appended"][1]["end"] == (CUT_TS + timedelta(minutes=75)).isoformat()
    # Deterministic: the same mask on the same notebook gives the same ids.
    again = apply_mask(mask, _toy_session(tmp_path / "again"), CUT_TS)
    assert [a["id"] for a in again["appended"]] == [a["id"] for a in record["appended"]]


def test_mask_without_appends_keeps_the_clock_at_the_cut(tmp_path):
    session = _toy_session(tmp_path)
    record = apply_mask(load_mask(_mask(tmp_path, "drop: []\n")), session, CUT_TS)
    assert record["appended"] == [] and record["clock"] == CUT_TS.isoformat()


@pytest.mark.parametrize("text, message", [
    ("append:\n  - notebook: x_measure.ipynb\n    cells:\n      - code: |\n          x\n", "needs its `output`"),
    ("append:\n  - notebook: x_measure.ipynb\n    cells:\n      - code: x\n        output: y\n        duration: 5 min\n", "duration must be"),
    ("append:\n  - notebook: x_measure.ipynb\n    cells:\n      - markdown: x\n        output: y\n", "unknown keys"),
    ("append:\n  - notebook: x_measure.ipynb\n    cells: []\n", "non-empty"),
])
def test_mask_append_refuses_malformed_cells(tmp_path, text, message):
    with pytest.raises(CutError, match=message):
        load_mask(_mask(tmp_path, text))


def test_mask_append_refuses_a_missing_notebook(tmp_path):
    session = _toy_session(tmp_path)
    mask = load_mask(_mask(tmp_path, "append:\n  - notebook: y_measure.ipynb\n    cells:\n      - markdown: x\n"))
    with pytest.raises(CutError, match="does not have"):
        apply_mask(mask, session, CUT_TS)


def test_parse_duration():
    assert parse_duration(None, "x") == 0
    assert parse_duration("90s", "x") == 90 and parse_duration("2m", "x") == 120 and parse_duration("1h", "x") == 3600


# --- hera-watch stub: only arming ends the episode ---------------------------

_HERA_WATCH_STUB = Path(__file__).resolve().parents[2] / "src" / "hera" / "replay" / "stubs" / "hera-watch"


def _run_watch_stub(tmp_path, *argv, timeout=3.0):
    env = dict(os.environ, HERA_EPISODE_DIR=str(tmp_path))
    try:
        return subprocess.run([sys.executable, str(_HERA_WATCH_STUB), *argv], cwd=tmp_path, env=env,
                              capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None  # the stub blocked: it armed


@pytest.mark.parametrize("argv", [("--help",), ("-h",), (), ("data", "--help")])
def test_hera_watch_stub_help_and_bare_call_do_not_arm(tmp_path, argv):
    proc = _run_watch_stub(tmp_path, *argv)
    assert proc is not None, "the stub blocked on a read"
    assert not (tmp_path / "episode-stop.json").exists()
    # off the image the real tool is absent; the stub reports that instead of arming
    assert "not in this image" in proc.stderr


def _watch_episode(tmp_path, cells=(("aaaa0001", "code"), ("aaaa0002", "markdown"))) -> Path:
    """A session dir as materialize leaves it: the measure notebook and its baseline."""
    (tmp_path / ".claude").mkdir()
    _write_measure(tmp_path, cells)
    (tmp_path / ".claude" / "measure_cells.json").write_text(json.dumps({"m_measure.ipynb": [i for i, _ in cells]}))
    return tmp_path / "m_measure.ipynb"


def _write_measure(tmp_path, cells) -> None:
    nb = {"cells": [{"id": i, "cell_type": k, "source": "", "metadata": {}} for i, k in cells], "metadata": {},
          "nbformat": 4, "nbformat_minor": 5}
    (tmp_path / "m_measure.ipynb").write_text(json.dumps(nb))


BASE_CELLS = (("aaaa0001", "code"), ("aaaa0002", "markdown"))


@pytest.mark.parametrize("argv,error", [(("data", "--next", "--follow"), "no new run appeared under data within 1s"),
                                        (("data/9",), "run dir data/9 did not appear within 1s")])
def test_hera_watch_stub_waits_for_a_code_cell_and_times_out_like_the_real_tool(tmp_path, argv, error):
    _watch_episode(tmp_path)
    _write_measure(tmp_path, BASE_CELLS + (("bbbb0001", "markdown"),))  # a markdown append does not arm
    proc = _run_watch_stub(tmp_path, *argv, "--wait-start", "1", timeout=10.0)
    assert proc is not None and proc.returncode == 2
    assert "armed on data" in proc.stdout and error in proc.stderr
    assert not (tmp_path / "episode-stop.json").exists()


def test_hera_watch_stub_arms_on_a_code_cell_appended_since_the_cut(tmp_path):
    _watch_episode(tmp_path)
    _write_measure(tmp_path, BASE_CELLS + (("bbbb0001", "markdown"), ("bbbb0002", "code")))
    assert _run_watch_stub(tmp_path, "data", "--next", "--follow", timeout=2.0) is None
    marker = json.loads((tmp_path / "episode-stop.json").read_text())
    assert marker["tool"] == "hera-watch" and marker["command"] == "hera-watch data --next --follow"
    assert marker["cell_ids"] == ["bbbb0002"]


def test_hera_watch_stub_arms_on_an_append_not_yet_saved(tmp_path):
    _watch_episode(tmp_path)
    (tmp_path / ".claude" / "measure_appends.jsonl").write_text(
        json.dumps({"cells": [{"kind": "markdown", "id": "cccc0001"}, {"kind": "code", "id": "cccc0002"}]}) + "\n")
    assert _run_watch_stub(tmp_path, "data", "--next", timeout=2.0) is None
    assert json.loads((tmp_path / "episode-stop.json").read_text())["cell_ids"] == ["cccc0002"]


def test_hera_watch_stub_armed_first_ends_the_episode_when_the_cell_lands(tmp_path):
    _watch_episode(tmp_path)
    proc = subprocess.Popen([sys.executable, str(_HERA_WATCH_STUB), "data", "--next", "--follow"], cwd=tmp_path,
                            env=dict(os.environ, HERA_EPISODE_DIR=str(tmp_path)), stdout=subprocess.PIPE, text=True)
    try:
        assert proc.stdout.readline().startswith("# armed on data")
        assert not (tmp_path / "episode-stop.json").exists() and proc.poll() is None
        _write_measure(tmp_path, BASE_CELLS + (("dddd0001", "code"),))
        deadline = time.monotonic() + 10
        while not (tmp_path / "episode-stop.json").exists() and time.monotonic() < deadline:
            time.sleep(0.2)
        assert json.loads((tmp_path / "episode-stop.json").read_text())["cell_ids"] == ["dddd0001"]
        assert proc.poll() is None  # armed: it blocks until the harness ends the session
    finally:
        proc.kill()
        proc.wait()
