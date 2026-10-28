"""`hera-replay inspect`: the tactical transcript as a turn list to pick a cut from."""

from __future__ import annotations

import json
import re

from hera.replay.archive import Archive
from hera.replay.derive import _observes_session, resolve_target
from hera.replay.transcript import (
    CELL_ID_IN_RESULT,
    NB_COLLAB_APPEND,
    WAIT_TOOLS,
    Entry,
    Transcript,
    first_line,
    handoff_invocation,
    run_ids_in,
    tool_result_text_of,
)

_CD_PREFIX = re.compile(r"^cd\s+\S+\s*&&\s*")


def _short_path(t: Transcript, path: str, cwd: str) -> str:
    try:
        target = resolve_target(path, cwd, t.layout, t.session_id)
    except Exception:
        return path
    if target.kind == "session":
        return target.rel or "."
    if target.kind == "measurement_env":
        return "~/measurement_env/" + target.rel
    return path


def _call_summary(t: Transcript, e: Entry, b: dict) -> tuple[str, str]:
    name = b.get("name", "")
    inp = b.get("input") or {}
    if name == "Bash":
        return name, first_line(_CD_PREFIX.sub("", inp.get("command", "")))
    path = inp.get("file_path") or inp.get("notebook_path") or inp.get("path")
    if path:
        return name, _short_path(t, str(path), e.cwd or t.cwd)
    return name, first_line(json.dumps(inp, ensure_ascii=False))


def rows(archive: Archive) -> list[dict]:
    t = archive.transcript
    ids = set()
    for name in archive.notebooks:
        ids.update(c.get("id") for c in archive.load_notebook(name)["cells"] if c.get("id"))
    seen_runs: set[int] = set()
    out = []
    for e in t.entries:
        if e.type not in ("user", "assistant"):
            continue
        ts = e.timestamp.strftime("%H:%M:%S") if e.timestamp else "--:--:--"
        base = {"index": e.index, "uuid": e.uuid or "", "time": ts}
        if e.type == "assistant":
            calls = e.blocks("tool_use")
            if calls:
                for b in calls:
                    tool, summary = _call_summary(t, e, b)
                    markers = []
                    if tool == "Bash":
                        cmd = b.get("input", {}).get("command", "")
                        handoff = handoff_invocation(cmd)
                        if handoff:
                            markers.append("WAIT" if handoff.startswith("nb-collab wait") else "EXEC")
                        elif NB_COLLAB_APPEND.search(cmd):
                            markers.append("APPEND")
                    if tool in WAIT_TOOLS:
                        markers.append("WAIT")
                    out.append({**base, "role": "assistant", "tool": tool, "summary": summary, "markers": markers})
            else:
                text = e.text.strip()
                if text:
                    out.append({**base, "role": "assistant", "tool": "", "summary": first_line(text), "markers": []})
        elif t.is_tool_result(e):
            tc = t.call_for_result(e)
            text = tool_result_text_of(e)
            markers = []
            if tc is not None and "nb-collab" in tc.input.get("command", ""):
                for m in re.finditer(r"appended \w+ @ (\d+) id=([\w-]+)", text):
                    markers.append(f"+cell {m.group(2)}@{m.group(1)}")
                for tok in CELL_ID_IN_RESULT.findall(text):
                    if tok in ids and not any(tok in m for m in markers):
                        markers.append(f"cell {tok}")
            for rid in run_ids_in(text) if (tc is not None and _observes_session(tc, t.layout, t.session_id)) else []:
                if rid not in seen_runs:
                    seen_runs.add(rid)
                    markers.append(f"RUN data/{rid}")
            summary = first_line(text) if text else "(image)" if e.blocks("tool_result") and any(
                isinstance(x, dict) and x.get("type") == "image"
                for b in e.blocks("tool_result") for x in (b.get("content") if isinstance(b.get("content"), list) else [])
            ) else ""
            out.append({**base, "role": "result", "tool": tc.name if tc else "?", "summary": summary, "markers": markers})
        else:
            text = e.text.strip()
            out.append({**base, "role": "user", "tool": "", "summary": first_line(text), "markers": []})
    return out


def render(archive: Archive, grep: str | None = None, around: int | None = None, context: int = 10) -> str:
    t = archive.transcript
    lines = [
        f"archive:    {archive.root}",
        f"transcript: {t.path.relative_to(archive.root).as_posix()}  session {t.session_id}  {len(t.entries)} entries",
        f"rig cwd:    {t.cwd}  ->  {t.layout.container_session_dir}",
        f"notebooks:  {', '.join(archive.notebooks) or 'none'}   runs: {', '.join(str(r) for r in sorted(archive.run_dirs)) or 'none'}",
        "",
    ]
    pattern = re.compile(grep, re.IGNORECASE) if grep else None
    for r in rows(archive):
        line = f"{r['index']:5d}  {r['uuid'][:8]:8}  {r['time']}  {r['role']:9}  {r['tool']:15} {r['summary']}"
        if r["markers"]:
            line += "   [" + "; ".join(r["markers"]) + "]"
        if around is not None and abs(r["index"] - around) > context:
            continue
        if pattern and not pattern.search(line):
            continue
        lines.append(line)
    return "\n".join(lines)
