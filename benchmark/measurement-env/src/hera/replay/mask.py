"""A mask: the edits a frontier makes to the materialized session state, for
every arm alike. It removes what the archived agent's own files say about the
decision under test — a rule restated from a recipe, a design pre-announced —
and leaves measurements — a file dropped, a notebook cell dropped
(`<notebook>#<cell id>`), or text edited; it can also append operator cells to a notebook, the
handoff work done between the cut and the new instance, each with the time it
took, and the episode's clock starts after the last of them. Each edit names
one site exactly; a site that no longer matches is a stale mask and refuses,
never a silent no-op."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import nbformat
import yaml
from nbformat.v4 import new_code_cell, new_markdown_cell, new_output

from hera.replay.errors import CutError

DURATION = re.compile(r"^(\d+)([smh])$")
DURATION_UNIT_S = {"s": 1, "m": 60, "h": 3600}


@dataclass(frozen=True)
class Edit:
    target: str  # "<file>" or "<notebook>#<cell id>"
    new: str
    old: str | None = None  # exact text, present once
    span: tuple[str, str] | None = None  # (from, to): from the start of `from` (once) to the next `to`, exclusive


@dataclass(frozen=True)
class AppendCell:
    cell_type: str  # "markdown" | "code"
    source: str
    duration_s: int  # the cell's own run time (a markdown cell: the time before the next one)
    output: str | None = None  # stdout of a code cell


@dataclass(frozen=True)
class Append:
    notebook: str
    cells: tuple[AppendCell, ...]


@dataclass(frozen=True)
class Mask:
    path: Path
    drop: tuple[str, ...]
    edits: tuple[Edit, ...]
    appends: tuple[Append, ...] = ()

    @property
    def duration_s(self) -> int:
        """How long the appended work took: the episode's clock starts this long after the cut."""
        return sum(c.duration_s for a in self.appends for c in a.cells)


def parse_duration(value: object, where: str) -> int:
    if value is None:
        return 0
    m = DURATION.match(str(value).strip())
    if not m:
        raise CutError(f"{where}: duration must be <N>s, <N>m or <N>h, got {value!r}")
    return int(m.group(1)) * DURATION_UNIT_S[m.group(2)]


def _load_appends(raw: list, name: str) -> tuple[Append, ...]:
    appends = []
    for i, a in enumerate(raw):
        where = f"{name}: append[{i}]"
        if not isinstance(a, dict) or a.keys() != {"notebook", "cells"} or not isinstance(a["cells"], list) or not a["cells"]:
            raise CutError(f"{where} takes `notebook` and a non-empty `cells` list")
        if not str(a["notebook"]).endswith(".ipynb"):
            raise CutError(f"{where}: notebook must be an .ipynb name")
        cells = []
        for j, c in enumerate(a["cells"]):
            cwhere = f"{where}.cells[{j}]"
            if not isinstance(c, dict):
                raise CutError(f"{cwhere} must be a mapping")
            c: dict = c
            if ("markdown" in c) == ("code" in c):
                raise CutError(f"{cwhere} is either `markdown` or `code`")
            kind = "markdown" if "markdown" in c else "code"
            allowed = {kind, "duration"} | ({"output"} if kind == "code" else set())
            if c.keys() - allowed:
                raise CutError(f"{cwhere}: unknown keys {sorted(c.keys() - allowed)}")
            source = str(c[kind])
            if not source.strip():
                raise CutError(f"{cwhere}: empty source")
            output = c.get("output") if kind == "code" else None
            if kind == "code" and not (isinstance(output, str) and output.strip()):
                raise CutError(f"{cwhere}: an appended code cell is executed, so it needs its `output`")
            cells.append(AppendCell(cell_type=kind, source=source.rstrip("\n"), duration_s=parse_duration(c.get("duration"), cwhere), output=output))
        appends.append(Append(notebook=str(a["notebook"]), cells=tuple(cells)))
    return tuple(appends)


def load_mask(path: Path) -> Mask:
    path = Path(path).resolve()
    if not path.is_file():
        raise CutError(f"mask not found: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict) or raw.keys() - {"drop", "edits", "append"}:
        raise CutError(f"{path.name}: a mask has `drop`, `edits` and/or `append`, got {sorted(raw) if isinstance(raw, dict) else type(raw).__name__}")
    appends = _load_appends(raw.get("append") or [], path.name)
    drop = raw.get("drop") or []
    # Runs are never dropped; a run's agent-written comment can be edited like any
    # other agent text. A `<notebook>#<cell id>` entry drops one cell.
    if not isinstance(drop, list) or not all(isinstance(p, str) and p and not p.startswith(("/", "data/")) for p in drop):
        raise CutError(f"{path.name}: drop must list session-relative paths outside data/")
    for p_ in drop:
        if "#" in p_ and not p_.split("#", 1)[0].endswith(".ipynb"):
            raise CutError(f"{path.name}: a cell drop is <notebook>.ipynb#<cell id>, got {p_!r}")
    edits = []
    for i, e in enumerate(raw.get("edits") or []):
        if not isinstance(e, dict):
            raise CutError(f"{path.name}: edits[{i}] must be a mapping")
        where = ("file" in e) + ("notebook" in e)
        if where != 1 or ("notebook" in e) != ("cell" in e):
            raise CutError(f"{path.name}: edits[{i}] names either file, or notebook + cell")
        target = e["file"] if "file" in e else f"{e['notebook']}#{e['cell']}"
        keys = e.keys() - {"file", "notebook", "cell", "new"}
        if keys == {"old"}:
            edits.append(Edit(target=target, new=str(e.get("new", "")), old=e["old"]))
        elif keys == {"from", "to"}:
            edits.append(Edit(target=target, new=str(e.get("new", "")), span=(e["from"], e["to"])))
        else:
            raise CutError(f"{path.name}: edits[{i}] takes `old` or `from` + `to` (and `new`), got {sorted(keys)}")
        if not (edits[-1].old or (edits[-1].span and all(edits[-1].span))):
            raise CutError(f"{path.name}: edits[{i}]: old / from / to must be non-empty")
    return Mask(path=path, drop=tuple(drop), edits=tuple(edits), appends=appends)


def _jl_stamp(ts: datetime) -> str:
    """A cell-execution stamp as JupyterLab writes it: UTC, microseconds, trailing Z."""
    return ts.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


def _cell_id(notebook: str, position: int, source: str) -> str:
    return hashlib.sha1(f"{notebook}\0{position}\0{source}".encode("utf-8")).hexdigest()[:8]


def _append_cells(nb: dict, notebook: str, cells: tuple[AppendCell, ...], start: datetime) -> tuple[list[dict], datetime]:
    """Append operator cells as JupyterLab would leave them — an 8-hex id, no
    `hera` stamps, a code cell executed once with its stdout and the kernel's
    execution stamps — one after another from `start`. Returns the records and
    when the last cell ended."""
    count = max((c.get("execution_count") or 0 for c in nb["cells"] if c.get("cell_type") == "code"), default=0)
    at = start
    records = []
    for cell in cells:
        position = len(nb["cells"])
        cid = _cell_id(notebook, position, cell.source)
        end = at + timedelta(seconds=cell.duration_s)
        if cell.cell_type == "markdown":
            new = new_markdown_cell(cell.source, id=cid)
        else:
            count += 1
            new = new_code_cell(cell.source, id=cid, execution_count=count,
                                outputs=[new_output("stream", name="stdout", text=cell.output)])
            new["metadata"]["execution"] = {
                "iopub.execute_input": _jl_stamp(at), "iopub.status.busy": _jl_stamp(at),
                "iopub.status.idle": _jl_stamp(end), "shell.execute_reply": _jl_stamp(end),
                "shell.execute_reply.started": _jl_stamp(at),
            }
        nb["cells"].append(dict(new))
        records.append({"notebook": notebook, "id": cid, "cell_type": cell.cell_type, "index": position,
                        "start": at.isoformat(), "end": end.isoformat()})
        at = end
    return records, at


def _edit_text(text: str, edit: Edit) -> tuple[str, str]:
    """The edited text and what the edit removed. Matching is on LF text."""
    if edit.old is not None:
        n = text.count(edit.old)
        if n != 1:
            raise CutError(f"mask edit on {edit.target}: `old` {'is ambiguous' if n else 'not found'} ({edit.old[:60]!r})")
        return text.replace(edit.old, edit.new), edit.old
    start_tok, end_tok = edit.span
    n = text.count(start_tok)
    if n != 1:
        raise CutError(f"mask edit on {edit.target}: `from` {'is ambiguous' if n else 'not found'} ({start_tok[:60]!r})")
    start = text.index(start_tok)
    end = text.find(end_tok, start + len(start_tok))
    if end < 0:
        raise CutError(f"mask edit on {edit.target}: `to` {end_tok[:40]!r} not found after `from`")
    return text[:start] + edit.new + text[end:], text[start:end]


def apply_mask(mask: Mask, session: Path, cut_ts: datetime) -> dict:
    """Apply the mask to a materialized session dir. Returns the record for
    episode.json: what was dropped, per edit the text removed, the cells
    appended with their start and end, and `clock`, when the appended work
    ended — the episode's clock starts there (the cut itself with no appends)."""
    record = {"path": str(mask.path), "dropped": [], "edits": [], "appended": [], "clock": cut_ts.isoformat()}
    for rel in mask.drop:
        if "#" in rel:
            name, cell_id = rel.split("#", 1)
            p = session / name
            if not p.is_file():
                raise CutError(f"mask drops a cell of {name}, which the materialized session does not have")
            nb = json.loads(p.read_text(encoding="utf-8"))
            keep = [c for c in nb["cells"] if c.get("id") != cell_id]
            if len(keep) != len(nb["cells"]) - 1:
                raise CutError(f"mask drops cell {cell_id} of {name}: {len(nb['cells']) - len(keep)} such cells at the cut")
            nb["cells"] = keep
            nbformat.validate(nbformat.from_dict(nb))
            p.write_text(json.dumps(nb, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
            record["dropped"].append(rel)
            continue
        p = session / rel
        if not p.is_file():
            raise CutError(f"mask drops {rel}, which the materialized session does not have")
        p.unlink()
        record["dropped"].append(rel)
    for edit in mask.edits:
        if "#" in edit.target:
            name, cell_id = edit.target.split("#", 1)
            p = session / name
            if not p.is_file():
                raise CutError(f"mask edits {name}, which the materialized session does not have")
            nb = json.loads(p.read_text(encoding="utf-8"))
            cells = [c for c in nb["cells"] if c.get("id") == cell_id]
            if len(cells) != 1:
                raise CutError(f"mask edits cell {cell_id} of {name}: {len(cells)} such cells at the cut")
            src = cells[0]["source"]
            text = "".join(src) if isinstance(src, list) else src
            new_text, removed = _edit_text(text, edit)
            cells[0]["source"] = new_text
            p.write_text(json.dumps(nb, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        else:
            p = session / edit.target
            if not p.is_file():
                raise CutError(f"mask edits {edit.target}, which the materialized session does not have")
            raw = p.read_bytes().decode("utf-8")
            crlf = "\r\n" in raw
            new_text, removed = _edit_text(raw.replace("\r\n", "\n"), edit)
            p.write_text(new_text.replace("\n", "\r\n") if crlf else new_text, encoding="utf-8", newline="")
        record["edits"].append({"target": edit.target, "removed": removed, "new": edit.new})
    at = cut_ts
    for a in mask.appends:
        p = session / a.notebook
        if not p.is_file():
            raise CutError(f"mask appends to {a.notebook}, which the materialized session does not have")
        nb = json.loads(p.read_text(encoding="utf-8"))
        records, at = _append_cells(nb, a.notebook, a.cells, at)
        nbformat.validate(nbformat.from_dict(nb))
        p.write_text(json.dumps(nb, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        record["appended"] += records
    record["clock"] = at.isoformat()
    return record
