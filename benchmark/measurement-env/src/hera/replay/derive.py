"""Derivation of the frontier from the transcript alone.

Everything the episode holds is derived here: which notebook cells the agent
had appended or observed, which data runs it had seen, and the state of every
session-dir file at the cut — a file the rig last wrote before the cut as
archived, one changed after it reconstructed from the transcript's ops. Each
rule is total or raises CutError naming the thing it cannot place.
"""

from __future__ import annotations

import base64
import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from hera.replay.archive import AS_ARCHIVED, Archive
from hera.replay.errors import CutError
from hera.replay.transcript import (
    CELL_ID_IN_RESULT,
    Entry,
    RigLayout,
    ToolCall,
    Transcript,
    command_tokens,
    epoch_ts,
    notebooks_named,
    parse_heredocs,
    parse_python_scripts,
    parse_ts,
    run_ids_in,
    tool_result_text_of,
    _SHELL_EXPANSION,
    parse_sed_in_place,
)

SESSION_NOTES = "session_notes.md"
FILE_TOOLS = {"Read", "Edit", "Write", "MultiEdit", "NotebookEdit", "Glob", "Grep"}
HEX8 = re.compile(r"^[0-9a-f]{8}$")


# --- targets -----------------------------------------------------------------


@dataclass(frozen=True)
class Target:
    kind: str  # session | measurement_env | cli_task | volatile | other
    rel: str  # posix path below the class root ("" for the root itself)
    raw: str


def _drive_token(comp: str, style: str) -> str | None:
    if style != "windows":
        return None
    m = re.match(r"^([A-Za-z]):$", comp)
    if m:
        return m.group(1).lower()
    return None


def _split(path: str) -> list[str]:
    return [c for c in re.split(r"[\\/]+", path) if c]


def _is_absolute(path: str, style: str) -> bool:
    if path.startswith(("/", "\\")):
        return True
    return style == "windows" and re.match(r"^[A-Za-z]:[\\/]", path) is not None


def _normalize(comps: list[str]) -> list[str]:
    out: list[str] = []
    for c in comps:
        if c == ".":
            continue
        if c == "..":
            if not out:
                raise CutError(f"path climbs above the root: {'/'.join(comps)}")
            out.pop()
            continue
        out.append(c)
    return out


def resolve_target(path: str, cwd: str, layout: RigLayout, session_id: str, cd: str | None = None) -> Target:
    """Classify a path the agent named: under the session dir, the corpus, the
    CLI's own task-output dir, or elsewhere."""
    raw = path
    style = layout.style
    if path == "~" or path.startswith(("~/", "~\\")):
        comps = _split(layout.home) + _split(path[1:])
    elif _is_absolute(path, style):
        comps = _split(path)
    else:
        base = cd if cd is not None else cwd
        if base != cwd:
            base_t = resolve_target(base, cwd, layout, session_id)
            if base_t.kind != "session":
                raise CutError(f"`cd {base}` leaves the session dir; cannot resolve {path!r}")
            base_comps = _split(layout.home) + list(layout.session_rel) + _split(base_t.rel)
        else:
            base_comps = _split(cwd)
        comps = base_comps + _split(path)
    comps = _normalize(comps)
    # Git Bash spells C:\Users as /c/Users; fold both to a lowercase drive token.
    if style == "windows" and comps:
        d = _drive_token(comps[0], style)
        if d is None and len(comps[0]) == 1 and comps[0].isalpha():
            d = comps[0].lower()
        if d is not None:
            comps[0] = d + ":"
    # The CLI's task-output files are known by claude/<slug>/<session-id>/tasks,
    # whatever spelling of the home precedes them (the toploader's %TEMP% is the
    # 8.3 form `C:\Users\TOPLOA~1`).
    if session_id in comps:
        k = comps.index(session_id)
        if "claude" in comps[:k] and "tasks" in comps[k:]:
            c = max(i for i in range(k) if comps[i] == "claude")
            return Target("cli_task", "/".join(comps[c:]), raw)
    # Git Bash's /tmp is volatile: a file staged there is gone by the next
    # session, so a shell write to it is nothing the episode needs to hold.
    if comps[:1] == ["tmp"]:
        return Target("volatile", "/".join(comps), raw)
    home = _normalize(_split(layout.home))
    if style == "windows":
        home[0] = home[0].lower()
    fold = (lambda s: s.lower()) if style == "windows" else (lambda s: s)
    if [fold(c) for c in comps[: len(home)]] != [fold(c) for c in home]:
        return Target("other", "/".join(comps), raw)
    rel = comps[len(home):]
    srel = list(layout.session_rel)
    if [fold(c) for c in rel[: len(srel)]] == [fold(c) for c in srel]:
        return Target("session", "/".join(rel[len(srel):]), raw)
    if rel[:1] == ["measurement_env"]:
        return Target("measurement_env", "/".join(rel[1:]), raw)
    return Target("other", "/".join(rel), raw)


# --- file ops ----------------------------------------------------------------


@dataclass
class FileOp:
    index: int  # entry index of the result (the moment the op landed)
    kind: str  # read | read-image | edit | write | heredoc
    rel: str
    content: str | bytes | None = None
    old: str | None = None
    new: str | None = None
    replace_all: bool = False
    original: str | None = None
    append: bool = False
    start_line: int | None = None
    num_lines: int | None = None
    total_lines: int | None = None
    exact: bool = True
    patch: list[dict] | None = None
    reason: str | None = None  # heredoc / sed / script whose result is unknown: why
    argv: list[str] | None = None  # sed: the argv applied to the content
    edits: tuple[tuple, ...] | None = None  # script: the literal edits applied to the content
    pos: int = 0  # order among ops of one Bash call

    @property
    def full_read(self) -> bool:
        return self.kind == "read" and self.start_line == 1 and self.num_lines == self.total_lines


@dataclass
class TargetLog:
    measurement_env: set[str] = field(default_factory=set)
    cli_task_outputs: set[str] = field(default_factory=set)
    volatile: set[str] = field(default_factory=set)  # /tmp paths shell writes went to; not materialized
    blanked: list[dict] = field(default_factory=list)  # {line, path, reason}: ops whose result is unknown


def _target_of(tc: ToolCall, layout: RigLayout, session_id: str) -> Target | None:
    inp = tc.input
    path = inp.get("file_path") or inp.get("notebook_path") or inp.get("path")
    if path is None:
        if tc.name in ("Glob", "Grep"):
            path = "."
        else:
            raise CutError(f"line {tc.call.index}: {tc.name} call has no path")
    return resolve_target(str(path), tc.call.cwd or layout.cwd, layout, session_id)


def collect_file_ops(t: Transcript) -> tuple[dict[str, list[FileOp]], TargetLog]:
    """Every file op in the whole transcript, keyed by session-relative path,
    plus the corpus / CLI paths the agent read. Aborts on a target the episode
    cannot hold."""
    ops: dict[str, list[FileOp]] = {}
    log = TargetLog()
    layout = t.layout
    for tc in t.tool_calls:
        if tc.result is None:
            continue
        idx = tc.result_index
        if tc.is_error and tc.name in FILE_TOOLS:
            continue
        if tc.name in FILE_TOOLS:
            target = _target_of(tc, layout, t.session_id)
            if tc.name in ("MultiEdit", "NotebookEdit"):
                raise CutError(f"line {tc.call.index}: {tc.name} on {target.raw}; not reconstructable")
            if target.kind == "measurement_env":
                if tc.name in ("Edit", "Write"):
                    raise CutError(f"line {tc.call.index}: {tc.name} writes into ~/measurement_env ({target.raw})")
                log.measurement_env.add(target.rel)
                continue
            if target.kind == "cli_task":
                if tc.name != "Read":
                    raise CutError(f"line {tc.call.index}: {tc.name} on CLI task file {target.raw}")
                log.cli_task_outputs.add(target.rel)
                continue
            if target.kind in ("other", "volatile"):
                raise CutError(f"line {tc.call.index}: {tc.name} targets {target.raw}, outside the session dir and ~/measurement_env")
            if tc.name in ("Glob", "Grep"):
                continue
            op = _file_op(tc, target.rel)
            if op is not None:
                ops.setdefault(target.rel, []).append(op)
        elif tc.name == "Bash":
            # A shell write whose result is not knowable (a non-literal heredoc,
            # a failed command) leaves the file's state unknown until a later
            # truth point; a file still unknown at the cut is materialized blank
            # and logged. Never guessed. `sed -i` is modelled by running sed.
            command = tc.input.get("command", "")
            failed = "the Bash command exited nonzero; whether the write ran is unknown" if tc.is_error else None
            for hd in parse_heredocs(command):
                reason = hd.reason or failed
                if _SHELL_EXPANSION.search(hd.path):
                    log.blanked.append({"line": tc.call.index, "path": hd.path, "reason": "the path has shell expansions; no file to attribute it to"})
                    continue
                target = resolve_target(hd.path, tc.call.cwd or layout.cwd, layout, t.session_id, cd=hd.cd)
                if target.kind == "volatile":
                    log.volatile.add(target.rel)
                    continue
                if target.kind != "session":
                    raise CutError(f"line {tc.call.index}: heredoc writes {target.raw}, outside the session dir")
                ops.setdefault(target.rel, []).append(
                    FileOp(index=idx, kind="heredoc", rel=target.rel, content=None if reason else hd.body, append=hd.append, reason=reason, pos=hd.pos)
                )
            # A `python -` heredoc of literal edits is the agent's sed: replayed on the
            # reconstructed content. Any other script is not an op.
            for sc in parse_python_scripts(command):
                target = resolve_target(sc.path, tc.call.cwd or layout.cwd, layout, t.session_id, cd=sc.cd)
                if target.kind == "volatile":
                    log.volatile.add(target.rel)
                    continue
                if target.kind != "session":
                    raise CutError(f"line {tc.call.index}: python script rewrites {target.raw}, outside the session dir")
                ops.setdefault(target.rel, []).append(FileOp(index=idx, kind="script", rel=target.rel, edits=sc.edits, reason=failed, pos=sc.pos))
            for sd in parse_sed_in_place(command):
                for f in sd.files:
                    if _SHELL_EXPANSION.search(f):
                        log.blanked.append({"line": tc.call.index, "path": f, "reason": "the path has shell expansions; no file to attribute it to"})
                        continue
                    target = resolve_target(f, tc.call.cwd or layout.cwd, layout, t.session_id, cd=sd.cd)
                    if target.kind == "volatile":
                        log.volatile.add(target.rel)
                        continue
                    if target.kind != "session":
                        raise CutError(f"line {tc.call.index}: sed -i edits {target.raw}, outside the session dir")
                    ops.setdefault(target.rel, []).append(FileOp(index=idx, kind="sed", rel=target.rel, argv=sd.argv, reason=failed))
    for rel in ops:
        ops[rel].sort(key=lambda o: (o.index, o.pos))
    return ops, log


def _file_op(tc: ToolCall, rel: str) -> FileOp | None:
    tur = tc.tool_use_result
    idx = tc.result_index
    if tc.name == "Read":
        if isinstance(tur, dict) and tur.get("type") == "file_unchanged":
            return None
        if not isinstance(tur, dict) or "file" not in tur:
            if "does not exist" in tc.result_text or "File does not exist" in tc.result_text:
                return None
            raise CutError(f"line {tc.call.index}: Read of {rel} has no file payload in toolUseResult")
        f = tur["file"]
        if tur.get("type") == "image":
            data = base64.b64decode(f["base64"])
            exact = f.get("originalSize") == len(data)
            return FileOp(index=idx, kind="read-image", rel=rel, content=data, exact=exact,
                          total_lines=f.get("originalSize"), num_lines=len(data))
        return FileOp(index=idx, kind="read", rel=rel, content=f["content"], start_line=f.get("startLine"),
                      num_lines=f.get("numLines"), total_lines=f.get("totalLines"))
    if tc.name == "Edit":
        if not isinstance(tur, dict) or "originalFile" not in tur:
            raise CutError(f"line {tc.call.index}: Edit of {rel} has no originalFile in toolUseResult")
        if not tur.get("structuredPatch"):
            raise CutError(f"line {tc.call.index}: Edit of {rel} has no structuredPatch in toolUseResult")
        return FileOp(index=idx, kind="edit", rel=rel, old=tur["oldString"], new=tur["newString"],
                      replace_all=bool(tur.get("replaceAll")), original=tur["originalFile"],
                      patch=tur["structuredPatch"])
    if tc.name == "Write":
        if not isinstance(tur, dict) or "content" not in tur:
            raise CutError(f"line {tc.call.index}: Write of {rel} has no content in toolUseResult")
        return FileOp(index=idx, kind="write", rel=rel, content=tur["content"], original=tur.get("originalFile"))
    raise CutError(f"line {tc.call.index}: unhandled file tool {tc.name}")


@dataclass
class FileState:
    rel: str
    content: str | bytes | None
    basis: str
    ops: list[dict]
    corroborated_by: str | None
    reason: str | None = None  # set when the file is not materialized
    blanked: str | None = None  # set when the file is materialized empty because its content is unknown

    @property
    def materialized(self) -> bool:
        return self.reason is None


def _nl(s: str) -> str:
    """Comparison form: line endings and the end-of-file newline count are not
    content (the rig's CRLF and the CLI's trailing-newline handling differ from
    the archived bytes)."""
    return s.replace("\r\n", "\n").rstrip("\n")


def _agrees(state: str, truth: str, headless: bool) -> bool:
    return _nl(truth).endswith(_nl(state)) if headless else _nl(state) == _nl(truth)


def _check(rel: str, state: str, truth: str, where: str, since: str, headless: bool = False) -> None:
    if not _agrees(state, truth, headless):
        raise CutError(
            f"{rel}: content at {where} differs from the forward reconstruction "
            f"(last known-good point {since}); the file changed by means outside Read/Edit/Write/heredoc"
        )


def reconstruct(rel: str, ops: list[FileOp], cut_index: int, archived: Path | None,
                cut_ts: datetime | None = None, snapshot: datetime | None = None) -> FileState | None:
    """Forward-replay a file's ops; the state at the cut, corroborated by the
    first truth point after it. None when the file had no op before the cut.
    Session notes the agent appended to before ever reading start empty: the
    head it never saw is not materialized, and truth points must end with the
    reconstruction. A file the archive holds in a state the ops do not reach
    (a script the harness does not model rewrote it) is taken as archived when
    its mtime says it was last written before the cut; `snapshot` bounds the
    mtimes the archive kept, as for runs (`_last_write`)."""
    if not any(o.index <= cut_index for o in ops):
        return None
    if any(o.kind == "read-image" for o in ops):
        return _reconstruct_image(rel, ops, cut_index)
    state: str | None = None
    basis = ""
    headless = rel == SESSION_NOTES and ops[0].kind == "heredoc" and ops[0].append
    if headless:
        state, basis = "", "appends only; head unseen by the agent"
    since, since_index = "start", 0
    cut_state: str | None = None
    corroborated: str | None = None
    applied: list[dict] = []
    unknown: str | None = None  # why the state is unknown, until a truth point
    cut_unknown: str | None = None
    for op in ops:
        where = f"{op.kind}@{op.index}"
        truth: str | None = None
        supersedes: dict = {}
        if (op.kind == "heredoc" and op.content is None) or (op.kind in ("sed", "script") and (op.reason or state is None)):
            state = None
            unknown = f"{where}: {op.reason or 'applied to an unknown state'}"
            since, since_index = where, op.index
            if op.index <= cut_index:
                cut_unknown = unknown
                applied.append({"index": op.index, "kind": op.kind, "unknown": True})
            continue
        if op.kind in ("sed", "script"):
            if op.kind == "sed" and headless:
                raise CutError(f"{rel}: sed at {where} on session notes whose head the agent never read")
            new_state, why = (_run_sed(op.argv, state), f"sed {op.argv!r} failed") if op.kind == "sed" else _apply_edits(op.edits, state)
            if new_state is None:
                state = None
                unknown = f"{where}: {why} on the reconstructed content"
                since, since_index = where, op.index
                if op.index <= cut_index:
                    cut_unknown = unknown
                    applied.append({"index": op.index, "kind": op.kind, "unknown": True})
                continue
            state = new_state
            if op.index <= cut_index:
                cut_state = state
                cut_unknown = None
                applied.append({"index": op.index, "kind": op.kind})
            continue
        if op.kind == "read":
            if op.full_read:
                truth = op.content
            elif state is None:
                raise CutError(f"{rel}: first Read ({where}) was partial (lines {op.start_line}-{op.start_line + op.num_lines - 1} of {op.total_lines}); no baseline")
            else:
                lines = _nl(state).split("\n")
                got = "\n".join(lines[op.start_line - 1 : op.start_line - 1 + op.num_lines])
                if got != _nl(op.content).rstrip("\n") and got.rstrip("\n") != _nl(op.content).rstrip("\n"):
                    raise CutError(f"{rel}: partial Read at {where} differs from the forward reconstruction (last known-good point {since})")
                truth = None
                since, since_index = where, op.index
        elif op.kind == "edit":
            truth = op.original
        elif op.kind == "write" and op.original is not None:
            truth = op.original
        if truth is not None:
            if state is None:
                state = truth
                basis = f"{op.kind}-baseline@{op.index}"
                unknown = None
            elif not _agrees(state, truth, headless):
                # An unmodelled change sits between the last known-good point and
                # this truth point. It matters only if the cut is in that span;
                # a truth point after the cut supersedes it.
                if since_index < cut_index < op.index:
                    _check(rel, state, truth, where, since, headless)
                state, headless = truth, False
                supersedes = {"supersedes": since}
            elif headless:
                state, headless = truth, False
            since, since_index = where, op.index
            if op.index > cut_index and corroborated is None:
                corroborated = where
        if op.kind == "edit":
            state = apply_patch(rel, state, op.patch, where)
        elif op.kind == "write":
            state = op.content
            basis = basis or f"write@{op.index}"
        elif op.kind == "heredoc":
            if op.append:
                if state is None:
                    # Appended to a file the harness never saw created (a shell
                    # redirect made it): unknown until a truth point or the archive.
                    unknown = f"{where}: append before any baseline"
                    since, since_index = where, op.index
                    if op.index <= cut_index:
                        cut_unknown = unknown
                        applied.append({"index": op.index, "kind": op.kind, "unknown": True})
                    continue
                state = state + op.content
            else:
                state = op.content
                basis = basis or f"heredoc@{op.index}"
        if op.index <= cut_index:
            cut_state = state
            cut_unknown = unknown
            applied.append({"index": op.index, "kind": op.kind, **supersedes})
        if corroborated is not None:
            break
    if cut_unknown is not None:
        if archived is not None and archived.is_file() and cut_ts is not None and snapshot is not None:
            written = epoch_ts(archived.stat().st_mtime)
            if written <= cut_ts and written <= snapshot:
                return FileState(rel=rel, content=archived.read_text(encoding="utf-8"), ops=applied, corroborated_by="archived",
                                 basis=f"archived: content unknown at the cut ({cut_unknown}); its mtime {written.isoformat()} precedes the cut")
        return FileState(rel=rel, content="", basis=f"blank: content unknown at the cut ({cut_unknown}); no truth point before the cut",
                         ops=applied, corroborated_by=None, blanked=cut_unknown)
    if cut_state is None:
        raise CutError(f"{rel}: no content derivable at the cut")
    if corroborated is None:
        if archived is None or not archived.is_file():
            raise CutError(f"{rel}: not in the archive, and no truth point after the cut corroborates the reconstruction")
        text = archived.read_text(encoding="utf-8")
        if state is None or not _agrees(state, text, headless):
            written = epoch_ts(archived.stat().st_mtime)
            if cut_ts is None or snapshot is None or written > snapshot or written > cut_ts:
                if state is None:
                    raise CutError(f"{rel}: content unknown after {since} ({unknown}); the archive cannot corroborate the cut")
                _check(rel, state, text, "archive", since, headless)
            return FileState(rel=rel, content=text, ops=applied, corroborated_by="archived",
                             basis=f"archived: an unmodelled change after {since} left the file as archived; "
                                   f"its mtime {written.isoformat()} precedes the cut")
        corroborated = "archived"
    return FileState(rel=rel, content=cut_state, basis=basis, ops=applied, corroborated_by=corroborated)


def apply_patch(rel: str, text: str, hunks: list[dict], where: str) -> str:
    """Apply the CLI's own structuredPatch (unified-diff hunks over lines): what
    the Edit tool wrote, rather than a re-derivation from old/new strings."""
    lines = text.split("\n")
    for h in sorted(hunks, key=lambda h: h["oldStart"], reverse=True):
        body = [l for l in h["lines"] if not l.startswith("\\")]
        old = [l[1:] for l in body if l[:1] in (" ", "-")]
        new = [l[1:] for l in body if l[:1] in (" ", "+")]
        start = h["oldStart"] - 1
        if lines[start : start + len(old)] != old:
            raise CutError(f"{rel}: Edit at {where}: patch context at line {h['oldStart']} does not match the reconstruction")
        lines[start : start + len(old)] = new
    return "\n".join(lines)


def _apply_edits(edits: tuple[tuple, ...], content: str) -> tuple[str, str]:
    """A script's literal edits on the reconstructed content, with `str.replace`
    semantics: every occurrence, a no-op when the old text is absent."""
    for edit in edits:
        content = content + edit[1] if edit[0] == "append" else content.replace(edit[1], edit[2])
    return content, ""


def _run_sed(argv: list[str], content: str) -> str | None:
    """GNU sed on the reconstructed content, the same script the agent ran."""
    try:
        r = subprocess.run(["sed", *argv], input=content, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout if r.returncode == 0 else None


def _reconstruct_image(rel: str, ops: list[FileOp], cut_index: int) -> FileState:
    kinds = {o.kind for o in ops}
    if kinds != {"read-image"}:
        raise CutError(f"{rel}: image with non-image ops {sorted(kinds - {'read-image'})}")
    last = [o for o in ops if o.index <= cut_index][-1]  # a plot re-rendered before the cut is its last rendering
    applied = [{"index": o.index, "kind": o.kind} for o in ops if o.index <= cut_index]
    if not last.exact:
        return FileState(rel=rel, content=None, basis=f"read-image@{last.index}", ops=applied, corroborated_by=None,
                         reason=f"the Read returned a downscaled rendering ({last.num_lines} of {last.total_lines} bytes)")
    return FileState(rel=rel, content=last.content, basis=f"read-image@{last.index}", ops=applied, corroborated_by="byte-exact Read")


def _written_before_the_cut(archive: Archive, files: dict[str, FileState], cut_ts: datetime,
                            snapshot: datetime) -> dict[str, FileState]:
    """Every session file the rig last wrote before the cut exists at the cut as archived,
    whatever wrote it (a tool, a shell redirect, a script). The mtime is the rig's only if it
    precedes the transcript's end (`snapshot`); a later stamp is an edit after the archive.
    A text file the ops reconstructed keeps its reconstruction; an image, a blanked file or
    one the ops never reached takes the archived bytes."""
    out = {}
    for path in sorted(archive.root.rglob("*")):
        rel = path.relative_to(archive.root).as_posix()
        if not path.is_file() or rel in AS_ARCHIVED or rel.endswith(".ipynb") \
                or rel.startswith(("data/", ".claude/", archive.transcript.path.parent.name + "/")):
            continue
        st = files.get(rel)
        image = st is not None and any(o.get("kind") == "read-image" for o in st.ops)
        if st is not None and st.materialized and not st.blanked and not image:
            continue
        written = epoch_ts(path.stat().st_mtime)
        if written > cut_ts or written > snapshot:
            continue
        data = path.read_bytes()
        try:
            content: str | bytes = data.decode("utf-8").replace("\r\n", "\n")
        except UnicodeDecodeError:
            content = data
        out[rel] = FileState(rel=rel, content=content, ops=st.ops if st is not None else [], corroborated_by="archived",
                             basis=f"archived: last written {written.isoformat()}, before the cut")
    return out


# --- notebooks ---------------------------------------------------------------


@dataclass
class NotebookCut:
    name: str
    cells_total: int
    keep: int  # number of leading cells kept
    cut_cell: dict | None
    basis: str
    referenced: list[str]
    code_cells_renumbered: int
    outputs_stripped: list[str] = field(default_factory=list)


def _hera(cell: dict) -> dict:
    h = cell.get("metadata", {}).get("hera")
    return h if isinstance(h, dict) else {}


def _stamp(cell: dict, key: str) -> datetime | None:
    v = _hera(cell).get(key)
    return parse_ts(v) if isinstance(v, str) else None


def cell_references(t: Transcript, ids: dict[str, dict[str, int]], cut_index: int) -> dict[str, set[str]]:
    """Cell ids each nb / nb-collab call or result named, per notebook, up to the cut."""
    refs: dict[str, set[str]] = {n: set() for n in ids}
    names = set(ids)
    for tc in t.calls_before(cut_index):
        if tc.name != "Bash":
            continue
        cmd = tc.input.get("command", "")
        if not re.search(r"\bnb(-collab)?\b", cmd):
            continue
        if re.search(r"\bnb-collab\s+delete\b", cmd):
            raise CutError(f"line {tc.call.index}: nb-collab delete; a deleted cell cannot be placed")
        named = notebooks_named(cmd, names)
        for tok in command_tokens(cmd):
            for n in named:
                if tok in ids[n]:
                    refs[n].add(tok)
        if "nb-collab" not in cmd:
            continue
        candidates = named or names
        for tok in CELL_ID_IN_RESULT.findall(tc.result_text):
            holders = [n for n in candidates if tok in ids[n]]
            if len(holders) == 1:
                refs[holders[0]].add(tok)
            elif len(holders) > 1:
                raise CutError(f"line {tc.result_index}: cell id {tok} is in several notebooks {holders}")
            elif HEX8.match(tok) and not any(tok in ids[n] for n in names):
                raise CutError(f"line {tc.result_index}: cell id {tok} is in no archived notebook (deleted?)")
    return refs


def cut_notebook(name: str, nb: dict, refs: set[str], start: datetime, cut_ts: datetime) -> NotebookCut:
    cells = nb["cells"]
    ids = {c.get("id"): i for i, c in enumerate(cells)}
    # hera.appended_at inside the transcript window is the agent's own append,
    # whether or not its result came back before the cut (background appends).
    stamped = [i for i, c in enumerate(cells) if (ts := _stamp(c, "appended_at")) is not None and start <= ts <= cut_ts]
    # Every cell before the first append of the session predates the transcript
    # (the template and hera-session's cells); it was on the page whether or not
    # the agent ever named it.
    predate = len(cells)
    for i, c in enumerate(cells):
        ts = _stamp(c, "appended_at")
        if ts is not None and ts >= start:
            predate = i
            break
    ref_idx = [ids[r] for r in refs]
    if ref_idx or stamped:
        idx = max(ref_idx + stamped)
        keep = max(idx + 1, predate)
        how = "referenced" if idx in ref_idx else "appended (hera.appended_at) but its append result is not in the transcript"
        basis = f"last agent cell {cells[idx].get('id')} @ {idx}, {how}"
        cut_cell = {"index": idx, "id": cells[idx].get("id")}
    else:
        keep = predate
        basis = "no agent cell before the cut; kept the cells that predate the transcript"
        cut_cell = None
    for i, c in enumerate(cells[:keep]):
        ts = _stamp(c, "appended_at")
        if ts is not None and ts > cut_ts:
            raise CutError(f"{name}: kept cell {c.get('id')} @ {i} was appended at {ts.isoformat()}, after the cut")
    # A kept cell executed after the cut (its last execution, per hera.executed_at)
    # was unexecuted or re-executed at the cut; the archive holds only the later
    # outputs, so it reads as unexecuted. The rest keep their outputs as archived
    # and read as executed once, in order, so a torn-down kernel is not what the
    # agent infers from the counts.
    kept = []
    count = 0
    unexecuted = []
    for i, c in enumerate(cells[:keep]):
        ed = _stamp(c, "edited_at")
        if ed is not None and ed > cut_ts:
            raise CutError(f"{name}: kept cell {c.get('id')} @ {i} was edited at {ed.isoformat()}, after the cut; its source at the cut is not in the archive")
        if c.get("cell_type") == "code":
            ex = _stamp(c, "executed_at")
            if ex is not None and ex > cut_ts:
                c = dict(c, execution_count=None, outputs=[])
                unexecuted.append(c.get("id"))
            else:
                count += 1
                c = dict(c, execution_count=count)
        kept.append(c)
    nb["cells"] = kept
    return NotebookCut(name=name, cells_total=len(cells), keep=keep, cut_cell=cut_cell, basis=basis,
                       referenced=sorted(refs, key=lambda r: ids[r]), code_cells_renumbered=count,
                       outputs_stripped=unexecuted)


# --- runs --------------------------------------------------------------------


@dataclass
class RunsCut:
    kept: list[int]
    in_flight: list[dict]
    unobserved: list[int]
    first_seen: dict[int, int]
    first_seen_in_notebook: dict[int, str] = field(default_factory=dict)
    first_seen_in_text: dict[int, int] = field(default_factory=dict)
    end_from_mtime: dict[int, str] = field(default_factory=dict)


def _last_write(rel: str, run_dir: Path, snapshot: datetime) -> datetime:
    """A run that dies stops writing, so its last file mtime bounds its end.
    The mtimes are the rig's only if the archive kept them (a git checkout stamps
    its own time): files that all postdate the transcript are refused."""
    stamps = [epoch_ts(p.stat().st_mtime) for p in run_dir.rglob("*") if p.is_file()]
    if min(stamps) > snapshot:
        raise CutError(f"{rel}/metadata.json has no end_time and every file in {rel}/ is newer than the transcript "
                       f"({min(stamps).isoformat()} > {snapshot.isoformat()}): the mtimes are the checkout's, not the rig's")
    return max(stamps)


_PATH_TOKEN = re.compile(r"[\\/]|^~")


def _observes_session(tc: ToolCall, layout: RigLayout, session_id: str) -> bool:
    """Bash output and Reads of session / CLI-task files report the session's own
    state; a Read of a corpus doc does not, whatever paths it mentions, and nor
    does a shell command whose every path lies under ~/measurement_env (an API
    doc's example run id is not a run)."""
    if tc.name == "Bash":
        cwd = tc.call.cwd or layout.cwd
        kinds = {resolve_target(tok, cwd, layout, session_id).kind
                 for tok in command_tokens(tc.input.get("command", "")) if _PATH_TOKEN.search(tok)}
        return kinds != {"measurement_env"}
    if tc.name != "Read":
        return False
    return _target_of(tc, layout, session_id).kind in ("session", "cli_task")


_RUN_IN_TEXT = re.compile(r"\b[Rr]un (\d+)\b|\bdata/(\d+)\b")


def _run_ids_in_text(text: str):
    for m in _RUN_IN_TEXT.finditer(text):
        yield int(m.group(1) or m.group(2))


def _output_text(cell: dict) -> str:
    parts = []
    for out in cell.get("outputs") or []:
        text = out.get("text")
        if text is None:
            text = (out.get("data") or {}).get("text/plain")
        if isinstance(text, list):
            text = "".join(text)
        if isinstance(text, str):
            parts.append(text)
    return "\n".join(parts)


def cut_runs(t: Transcript, archive: Archive, cut_index: int, cut_ts: datetime,
             notebooks: dict[str, tuple[dict, NotebookCut]] | None = None) -> RunsCut:
    """A run the agent had seen: named in a tool result before the cut, in the
    outputs of a kept, executed notebook cell, or in the agent's own text (a
    sweep launched from the page and watched only through `tail` never names
    its id in a result; the agent still knows which run it launched)."""
    first_seen: dict[int, int] = {}
    for tc in t.calls_before(cut_index):
        if not _observes_session(tc, t.layout, t.session_id):
            continue
        for rid in run_ids_in(tool_result_text_of(tc.result)):
            first_seen.setdefault(rid, tc.result_index)
    in_notebook: dict[int, str] = {}
    for name, (nb, _cut) in (notebooks or {}).items():
        for c in nb["cells"]:
            if c.get("cell_type") != "code":
                continue
            for rid in run_ids_in(_output_text(c)):
                in_notebook.setdefault(rid, f"{name}:{c.get('id')}")
    in_text: dict[int, int] = {}
    for e in t.entries[:cut_index]:
        if e.type != "assistant":
            continue
        for b in e.blocks("text"):
            for rid in _run_ids_in_text(b.get("text", "")):
                in_text.setdefault(rid, e.index)
    observed = set(first_seen) | set(in_notebook) | set(in_text)
    dirs = archive.run_dirs
    kept, in_flight, end_from_mtime = [], [], {}
    for rid in sorted(observed):
        where = (f"line {first_seen[rid]}" if rid in first_seen else f"cell {in_notebook[rid]}" if rid in in_notebook
                 else f"agent text at line {in_text[rid]}")
        if rid not in dirs:
            raise CutError(f"run {rid} was observed at {where} but data/{rid}/ is not in the archive")
        meta_path = dirs[rid] / "metadata.json"
        if not meta_path.is_file():
            raise CutError(f"data/{rid}/metadata.json missing; cannot tell whether the run had finished at the cut")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("end_time") is None:
            end = _last_write(f"data/{rid}", dirs[rid], t.end)
            end_from_mtime[rid] = end.isoformat()
        else:
            end = epoch_ts(float(meta["end_time"]))
        if end <= cut_ts:
            kept.append(rid)
        else:
            in_flight.append({"id": rid, "first_seen": where, "end_time": end.isoformat()})
    unobserved = sorted(set(dirs) - observed)
    return RunsCut(kept=kept, in_flight=in_flight, unobserved=unobserved, first_seen=first_seen,
                   first_seen_in_notebook=in_notebook, first_seen_in_text=in_text, end_from_mtime=end_from_mtime)


# --- the cut -----------------------------------------------------------------


@dataclass
class Derivation:
    cut: Entry
    cut_ts: datetime
    cut_call: ToolCall
    notebooks: dict[str, tuple[dict, NotebookCut]]
    runs: RunsCut
    files: dict[str, FileState]
    targets: TargetLog


def locate_cut(t: Transcript, uuid: str) -> tuple[Entry, ToolCall]:
    e = t.entry(uuid)
    if not t.is_tool_result(e):
        raise CutError(f"cut {uuid} (line {e.index}) is a {e.type!r} entry, not a tool_result")
    tc = t.call_for_result(e)
    if tc is None:
        raise CutError(f"cut {uuid} (line {e.index}) carries a tool_result with no matching tool_use")
    if e.timestamp is None:
        raise CutError(f"cut {uuid} (line {e.index}) has no timestamp")
    return e, tc


def derive(archive: Archive, uuid: str) -> Derivation:
    t = archive.transcript
    cut, cut_call = locate_cut(t, uuid)
    cut_ts = cut.timestamp
    start = t.start
    ops, targets = collect_file_ops(t)
    for rel in ops:
        if rel in AS_ARCHIVED and any(o.kind != "read" for o in ops[rel]):
            raise CutError(f"{rel} is archived as-is, but the agent wrote it (line {ops[rel][0].index})")
        if rel.endswith(".ipynb") and any(o.kind != "read" for o in ops[rel]):
            raise CutError(f"{rel}: the agent wrote the notebook file directly (line {ops[rel][0].index})")
        if rel.startswith("data/") and any(o.kind != "read" for o in ops[rel]):
            raise CutError(f"{rel}: the agent wrote under data/ (line {ops[rel][0].index})")
    notebooks: dict[str, tuple[dict, NotebookCut]] = {}
    loaded = {n: archive.load_notebook(n) for n in archive.notebooks}
    ids = {n: {c.get("id"): i for i, c in enumerate(nb["cells"]) if c.get("id")} for n, nb in loaded.items()}
    refs = cell_references(t, ids, cut.index)
    for n, nb in loaded.items():
        notebooks[n] = (nb, cut_notebook(n, nb, refs[n], start, cut_ts))
    runs = cut_runs(t, archive, cut.index, cut_ts, notebooks)
    files: dict[str, FileState] = {}
    for rel, fops in ops.items():
        if rel in AS_ARCHIVED or rel.endswith(".ipynb") or rel.startswith("data/"):
            continue
        st = reconstruct(rel, fops, cut.index, archive.root / rel, cut_ts, t.end)
        if st is not None:
            files[rel] = st
    files.update(_written_before_the_cut(archive, files, cut_ts, t.end))
    return Derivation(cut=cut, cut_ts=cut_ts, cut_call=cut_call, notebooks=notebooks, runs=runs, files=files, targets=targets)
