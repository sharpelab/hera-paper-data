"""A synthetic HERA archive with a small tactical transcript, for the replay tests.

The transcript walks the shapes the derivation rules key on: a relative Read
baseline, an Edit with the CLI's structuredPatch, a Write, a heredoc append
via `cd … && cat >>`, nb-collab append/execute results with cell ids, a run id
in a sweep line, an image Read, and post-cut ops on the same files.
"""

from __future__ import annotations

import base64
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

SID = "11111111-2222-3333-4444-555555555555"
INIT_SID = "99999999-8888-7777-6666-555555555555"
CWD = r"C:\Users\rig\measurements\zack\20260101-dev"
MENV = r"C:\Users\rig\measurement_env"
T0 = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")

CARD_V0 = "# Device card\n\n## Identity\nQC-test\n"
CARD_V1 = "# Device card\n\n## Identity\nQC-test\n\n## Calibration — ESTABLISHED\nslope 1\n"
CARD_FINAL = CARD_V1 + "\n## Stacking result — ESTABLISHED\nABA\n"
NOTES_V0 = "# Session notes\n\n- start\n"
NOTE_A = "- note A (pre-cut)\n"
NOTE_B = "- note B (post-cut)\n"
PROBE = "print('probe')\n"
FAN = "print('fan')\n"


class Builder:
    def __init__(self):
        self.lines: list[dict] = []
        self.n = 0
        self.uuids: dict[str, str] = {}

    def index(self, label: str) -> int:
        return int(self.uuids[label][:8], 16)

    def _ts(self) -> str:
        return (T0 + timedelta(seconds=self.n)).isoformat().replace("+00:00", "Z")

    def _uuid(self, label: str | None) -> str:
        u = f"{self.n:08x}-0000-0000-0000-000000000000"
        if label:
            self.uuids[label] = u
        return u

    def _entry(self, type_: str, message: dict, label: str | None = None, **extra) -> dict:
        e = {
            "parentUuid": None,
            "isSidechain": False,
            "type": type_,
            "message": message,
            "uuid": self._uuid(label),
            "timestamp": self._ts(),
            "cwd": CWD,
            "sessionId": SID,
            "version": "2.1.183",
            **extra,
        }
        self.lines.append(e)
        self.n += 1
        return e

    def user(self, text: str, label: str | None = None) -> None:
        self._entry("user", {"role": "user", "content": text}, label)

    def text(self, text: str, label: str | None = None) -> None:
        self._entry("assistant", {"role": "assistant", "content": [{"type": "text", "text": text}]}, label)

    def call(self, tool: str, inp: dict, label: str | None = None) -> str:
        tid = f"toolu_{self.n:06d}"
        self._entry("assistant", {"role": "assistant", "content": [{"type": "tool_use", "id": tid, "name": tool, "input": inp}]}, label)
        return tid

    def result(self, tid: str, content, tur=None, label: str | None = None, is_error: bool = False) -> None:
        block = {"type": "tool_result", "tool_use_id": tid, "content": content}
        if is_error:
            block["is_error"] = True
        self._entry("user", {"role": "user", "content": [block]}, label, toolUseResult=tur)

    def read(self, path: str, content: str, label: str | None = None) -> None:
        tid = self.call("Read", {"file_path": path})
        n = content.count("\n") + (0 if content.endswith("\n") else 1)
        self.result(tid, content, {"type": "text", "file": {"filePath": path, "content": content, "numLines": n, "startLine": 1, "totalLines": n}}, label)

    def read_image(self, path: str, data: bytes, label: str | None = None) -> None:
        tid = self.call("Read", {"file_path": path})
        b64 = base64.b64encode(data).decode()
        self.result(tid, [{"type": "image", "source": {"type": "base64", "data": b64, "media_type": "image/png"}}],
                    {"type": "image", "file": {"base64": b64, "type": "image/png", "originalSize": len(data)}}, label)

    def write(self, path: str, content: str, label: str | None = None) -> None:
        tid = self.call("Write", {"file_path": path, "content": content})
        self.result(tid, f"File created successfully at: {path}", {"type": "create", "filePath": path, "content": content, "structuredPatch": [], "originalFile": None}, label)

    def edit(self, path: str, original: str, old: str, new: str, label: str | None = None) -> None:
        tid = self.call("Edit", {"file_path": path, "old_string": old, "new_string": new, "replace_all": False})
        self.result(tid, f"The file {path} has been updated.", {
            "filePath": path, "oldString": old, "newString": new, "originalFile": original,
            "structuredPatch": structured_patch(original, original.replace(old, new, 1)), "userModified": False, "replaceAll": False,
        }, label)

    def bash(self, command: str, output: str, label: str | None = None, is_error: bool = False) -> None:
        tid = self.call("Bash", {"command": command})
        self.result(tid, output, {"stdout": output, "stderr": "", "interrupted": False}, label, is_error=is_error)


def structured_patch(old: str, new: str) -> list[dict]:
    """One hunk spanning the whole file, in the CLI's structuredPatch shape."""
    o = old.split("\n")
    n = new.split("\n")
    lines = [f"-{l}" for l in o] + [f"+{l}" for l in n]
    return [{"oldStart": 1, "oldLines": len(o), "newStart": 1, "newLines": len(n), "lines": lines}]


def cell(id_: str, kind: str, source: str, appended: datetime | None = None, executed: datetime | None = None, outputs=None) -> dict:
    c = {"id": id_, "cell_type": kind, "metadata": {}, "source": source}
    if appended or executed:
        c["metadata"]["hera"] = {"v": "v0"}
        if appended:
            c["metadata"]["hera"]["appended_at"] = appended.isoformat()
        if executed:
            c["metadata"]["hera"]["executed_at"] = executed.isoformat()
    if kind == "code":
        c["outputs"] = outputs or []
        c["execution_count"] = 1 if outputs else None
    return c


def notebook(cells: list[dict]) -> str:
    return json.dumps({"cells": cells, "metadata": {}, "nbformat": 4, "nbformat_minor": 5}, indent=1)


def build_transcript(post_cut_card_original: str = CARD_V1) -> Builder:
    b = Builder()
    b.user("# dev / rig — session brief\n\nGoal: test.")
    b.read("./device_card.md", CARD_V0)
    b.read("./rig_card.md", "# Rig card\n")
    b.read(CWD + r"\session_notes.md", NOTES_V0)
    b.read("~/measurement_env/hera/recipes/measurements/gatemap.md", "# Gatemap\n")
    b.read(MENV + r"\hera\recipes\STYLE.md", "# Style\n")
    b.write(CWD + r"\hera_scratch\probe.py", PROBE)
    b.bash("nb-collab append x_measure.ipynb --code-file hera_scratch/probe.py",
           "connected: http://localhost:8899 path=zack/20260101-dev/x_measure.ipynb cells=3\n  appended code @ 3 id=aaaa0001\ndone. cells now = 4")
    b.bash("nb-collab execute-cell x_measure.ipynb aaaa0001 --timeout 60",
           "  executing code @ 3 id=aaaa0001 kernel=k1\nstatus: done\n--- output ---\nStarting sweep with ID 0\nData saved in " + CWD + r"\data\0\data.tsv.gz",
           label="exec-probe")
    b.edit(CWD + r"\device_card.md", CARD_V0, "QC-test\n", "QC-test\n\n## Calibration — ESTABLISHED\nslope 1\n", label="edit-card-1")
    b.bash("cd ~/measurements/zack/20260101-dev && cat >> session_notes.md <<'EOF'\n" + NOTE_A.rstrip("\n") + "\nEOF", "ok")
    b.bash("nb-collab append x_ana.ipynb --markdown \"## Run 0\"",
           "connected: http://localhost:8899 path=zack/20260101-dev/x_ana.ipynb cells=2\n  appended markdown @ 2 id=bbbb0001\ndone. cells now = 3")
    b.bash("ls data/", "0/")
    b.read_image(CWD + r"\hera_scratch\plot.png", PNG, label="cut")
    b.call("Bash", {"command": "echo thinking"}, label="post-cut-call")
    b.result("toolu_x", "thinking")
    b.write(CWD + r"\hera_scratch\fan.py", FAN)
    b.bash("nb-collab append x_measure.ipynb --code-file hera_scratch/fan.py",
           "connected: http://localhost:8899 path=zack/20260101-dev/x_measure.ipynb cells=4\n  appended code @ 4 id=aaaa0002\ndone. cells now = 5",
           label="append-fan")
    b.bash("nb-collab execute-cell x_measure.ipynb aaaa0002 --timeout 60",
           "  executing code @ 4 id=aaaa0002 kernel=k1\nstatus: done\n--- output ---\nData saved in " + CWD + r"\data\1\data.tsv.gz")
    b.edit(CWD + r"\device_card.md", post_cut_card_original, "slope 1\n", "slope 1\n\n## Stacking result — ESTABLISHED\nABA\n", label="edit-card-2")
    b.bash("cd ~/measurements/zack/20260101-dev && cat >> session_notes.md <<'EOF'\n" + NOTE_B.rstrip("\n") + "\nEOF", "ok")
    return b


def make_archive(root: Path, builder: Builder | None = None, transcripts_dir: str = "transcripts",
                 card_final: str = CARD_FINAL, second_tactical: bool = False) -> tuple[Path, Builder]:
    b = builder or build_transcript()
    root.mkdir(parents=True)
    (root / "hera_session.md").write_text("# brief\n")
    (root / "rig_card.md").write_text("# Rig card\n")
    (root / "device_card.md").write_text(card_final)
    (root / "session_notes.md").write_text(NOTES_V0 + NOTE_A + NOTE_B)
    scratch = root / "hera_scratch"
    scratch.mkdir()
    (scratch / "probe.py").write_text(PROBE)
    (scratch / "fan.py").write_text(FAN)
    (scratch / "plot.png").write_bytes(PNG)
    (scratch / "extra.md").write_text("made by a script\n")
    t_cut = T0 + timedelta(seconds=b.index("cut"))
    before = t_cut - timedelta(seconds=1)
    t_fan = T0 + timedelta(seconds=b.index("append-fan"))
    after = T0 + timedelta(seconds=len(b.lines) + 100)  # later than every transcript entry
    for rid, end in ((0, before), (1, after)):
        d = root / "data" / str(rid)
        d.mkdir(parents=True)
        (d / "data.tsv.gz").write_bytes(b"\x1f\x8b")
        (d / "metadata.json").write_text(json.dumps({"start_time": (end - timedelta(seconds=5)).timestamp(), "end_time": end.timestamp()}))
    (root / "data" / "log.log").write_text("lakeshore\n")
    session_start = T0 - timedelta(minutes=5)
    (root / "x_measure.ipynb").write_text(notebook([
        cell("t1", "markdown", "# Measure"),
        cell("t2", "code", "import os", outputs=[{"output_type": "stream", "name": "stdout", "text": "ok\n"}]),
        cell("s1", "code", "print('hera-session bind')", appended=session_start, executed=session_start),
        cell("aaaa0001", "code", PROBE, appended=before, executed=before, outputs=[{"output_type": "stream", "name": "stdout", "text": "probe\n"}]),
        cell("aaaa0002", "code", FAN, appended=t_fan, executed=t_fan, outputs=[{"output_type": "stream", "name": "stdout", "text": "fan\n"}]),
    ]))
    (root / "x_ana.ipynb").write_text(notebook([
        cell("hdr", "markdown", "# Ana"),
        cell("setup", "code", "import numpy", executed=after, outputs=[{"output_type": "stream", "name": "stdout", "text": "late\n"}]),
        cell("bbbb0001", "markdown", "## Run 0", appended=before),
        cell("bbbb0002", "markdown", "## Run 1", appended=t_fan),
    ]))
    tdir = root / transcripts_dir
    tdir.mkdir()
    with (tdir / f"{SID}.jsonl").open("w") as fh:
        for e in b.lines:
            fh.write(json.dumps(e) + "\n")
    init = dict(b.lines[0], cwd=MENV, sessionId=INIT_SID, message={"role": "user", "content": "Begin session setup."})
    (tdir / f"{INIT_SID}.jsonl").write_text(json.dumps(init) + "\n")
    if second_tactical:
        other = dict(b.lines[0], sessionId="22222222-2222-2222-2222-222222222222")
        (tdir / "22222222-2222-2222-2222-222222222222.jsonl").write_text(json.dumps(other) + "\n")
    return root, b
