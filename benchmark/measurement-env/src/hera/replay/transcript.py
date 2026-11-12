"""A Claude Code session jsonl as the replay tools read it.

Loads every line, pairs each tool_use with the user entry carrying its
tool_result, and derives the rig layout (home, session dir, user, session)
from the transcript's own ``cwd``.
"""

from __future__ import annotations

import ast
import json
import re
import shlex
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from hera.replay.errors import CutError


@dataclass
class Entry:
    index: int
    raw: dict
    line: str

    @property
    def type(self) -> str:
        return self.raw.get("type", "")

    @property
    def uuid(self) -> str | None:
        return self.raw.get("uuid")

    @property
    def timestamp(self) -> datetime | None:
        ts = self.raw.get("timestamp")
        return parse_ts(ts) if ts else None

    @property
    def cwd(self) -> str | None:
        return self.raw.get("cwd")

    @property
    def content(self):
        message = self.raw.get("message")
        if not isinstance(message, dict):
            return None
        return message.get("content")

    def blocks(self, kind: str) -> list[dict]:
        content = self.content
        if not isinstance(content, list):
            return []
        return [b for b in content if isinstance(b, dict) and b.get("type") == kind]

    @property
    def text(self) -> str:
        content = self.content
        if isinstance(content, str):
            return content
        return "\n".join(b.get("text", "") for b in self.blocks("text"))


@dataclass
class ToolCall:
    call: Entry
    block: dict
    result: Entry | None = None

    @property
    def name(self) -> str:
        return self.block.get("name", "")

    @property
    def input(self) -> dict:
        return self.block.get("input") or {}

    @property
    def id(self) -> str:
        return self.block.get("id", "")

    @property
    def result_text(self) -> str:
        if self.result is None:
            return ""
        for b in self.result.blocks("tool_result"):
            if b.get("tool_use_id") != self.id:
                continue
            content = b.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                return "\n".join(
                    x.get("text", "") for x in content if isinstance(x, dict) and x.get("type") == "text"
                )
        return ""

    @property
    def is_error(self) -> bool:
        if self.result is None:
            return False
        return any(b.get("is_error") for b in self.result.blocks("tool_result") if b.get("tool_use_id") == self.id)

    @property
    def tool_use_result(self):
        return self.result.raw.get("toolUseResult") if self.result is not None else None

    @property
    def result_index(self) -> int | None:
        return self.result.index if self.result is not None else None


def parse_ts(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def epoch_ts(value: float) -> datetime:
    return datetime.fromtimestamp(value, tz=timezone.utc)


CONTAINER_HOME = "/home/hera"

_WIN_CWD = re.compile(r"^([A-Za-z]):[\\/]+Users[\\/]+([^\\/]+)[\\/]+(.+?)[\\/]*$")
_POSIX_CWD = re.compile(r"^/(?:home|Users)/([^/]+)/(.+?)/*$")


@dataclass
class RigLayout:
    """Where the session lived on the rig, and where it lives in the container."""

    cwd: str
    style: str  # "windows" | "posix"
    home: str
    home_pattern: str  # regex alternation matching every spelling of the home prefix
    session_rel: tuple[str, ...]  # components of the session dir below home
    user: str
    session: str

    @property
    def container_session_dir(self) -> str:
        return f"{CONTAINER_HOME}/measurements/{self.user}/{self.session}"

    @property
    def container_projects_slug(self) -> str:
        return project_slug(self.container_session_dir)

    @property
    def session_rel_pattern(self) -> str:
        return r"[\\/]+".join(re.escape(c) for c in self.session_rel)

    @classmethod
    def from_cwd(cls, cwd: str) -> "RigLayout":
        m = _WIN_CWD.match(cwd)
        if m:
            drive, name, rest = m.groups()
            d = re.escape(drive)
            n = re.escape(name)
            # The name ends at a separator or the end: `C:\Users\DGG` is not a prefix of `C:\Users\DGG~1`.
            pattern = (
                rf"(?:[{d.lower()}{d.upper()}]:[\\/]+Users[\\/]+{n}"
                rf"|/[{d.lower()}{d.upper()}]/Users/{n})(?![^\\/\s])"
            )
            home = f"{drive}:\\Users\\{name}"
            style = "windows"
        else:
            m = _POSIX_CWD.match(cwd)
            if not m:
                raise CutError(f"cannot derive the rig home from cwd {cwd!r}: not under C:\\Users\\<name> or /home/<name>")
            name, rest = m.groups()
            home = cwd[: cwd.index(name) + len(name)]
            pattern = re.escape(home)
            style = "posix"
        parts = tuple(p for p in re.split(r"[\\/]+", rest) if p)
        if len(parts) < 2:
            raise CutError(f"session cwd {cwd!r} has no <user>/<session> tail below the rig home")
        return cls(
            cwd=cwd,
            style=style,
            home=home,
            home_pattern=pattern,
            session_rel=parts,
            user=parts[-2],
            session=parts[-1],
        )


def project_slug(path: str) -> str:
    """The directory name Claude Code uses under ~/.claude/projects for a cwd.

    Every character outside [A-Za-z0-9] becomes '-', verified against this
    machine's ~/.claude/projects/ (`.`, `_`, `/` and `:` all map to '-').
    """
    return re.sub(r"[^A-Za-z0-9]", "-", path)


class Transcript:
    def __init__(self, path: Path):
        self.path = path
        self.entries: list[Entry] = []
        with path.open(encoding="utf-8") as fh:
            for i, line in enumerate(fh):
                line = line.rstrip("\n")
                if not line.strip():
                    continue
                self.entries.append(Entry(i, json.loads(line), line))
        cwds = {e.cwd for e in self.entries if e.cwd}
        if len(cwds) != 1:
            raise CutError(f"{path.name}: expected one cwd across the transcript, found {sorted(cwds)}")
        self.cwd = cwds.pop()
        sids = {e.raw.get("sessionId") for e in self.entries if e.raw.get("sessionId")}
        if len(sids) != 1:
            raise CutError(f"{path.name}: expected one sessionId, found {sorted(sids)}")
        self.session_id = sids.pop()
        self.layout = RigLayout.from_cwd(self.cwd)
        self.tool_calls: list[ToolCall] = self._pair_tool_calls()
        self._by_uuid = {e.uuid: e for e in self.entries if e.uuid}

    def _pair_tool_calls(self) -> list[ToolCall]:
        calls: list[ToolCall] = []
        by_id: dict[str, ToolCall] = {}
        for e in self.entries:
            if e.type == "assistant":
                for b in e.blocks("tool_use"):
                    tc = ToolCall(e, b)
                    calls.append(tc)
                    by_id[tc.id] = tc
            elif e.type == "user":
                for b in e.blocks("tool_result"):
                    tc = by_id.get(b.get("tool_use_id"))
                    if tc is not None and tc.result is None:
                        tc.result = e
        return calls

    @property
    def start(self) -> datetime:
        for e in self.entries:
            if e.timestamp:
                return e.timestamp
        raise CutError(f"{self.path.name}: no timestamped entry")

    @property
    def end(self) -> datetime:
        for e in reversed(self.entries):
            if e.timestamp:
                return e.timestamp
        raise CutError(f"{self.path.name}: no timestamped entry")

    def entry(self, uuid: str) -> Entry:
        e = self._by_uuid.get(uuid)
        if e is None:
            raise CutError(f"no entry with uuid {uuid} in {self.path.name}")
        return e

    def is_tool_result(self, e: Entry) -> bool:
        return e.type == "user" and bool(e.blocks("tool_result"))

    def calls_before(self, cut_index: int) -> list[ToolCall]:
        """Tool calls whose result landed at or before the cut entry."""
        return [tc for tc in self.tool_calls if tc.result_index is not None and tc.result_index <= cut_index]

    def call_for_result(self, e: Entry) -> ToolCall | None:
        for tc in self.tool_calls:
            if tc.result is e:
                return tc
        return None


@dataclass
class Heredoc:
    """One `cat > path <<'EOF' … EOF` (or `>>`) in a Bash command."""

    path: str
    append: bool
    body: str | None  # None when the content is not literal; `reason` says why
    cd: str | None = None
    reason: str | None = None
    pos: int = 0  # offset in the command, to order it against other ops of the same call


_CD_PREFIX = re.compile(r"^\s*cd\s+(\S+)\s*(?:&&|;)\s*")
_HEREDOC = re.compile(
    r"(?:^|&&|;|\|\||\n)[ \t]*cat[ \t]*(>>?)[ \t]*(\S+)[ \t]*<<[ \t]*(-?)[ \t]*(['\"]?)(\w+)\4([^\n]*)\n(.*?)\n\5[ \t]*(?=\n|$)",
    re.DOTALL,
)
_SHELL_EXPANSION = re.compile(r"[$`\\]")


@dataclass
class SedInPlace:
    """One `sed -i … <file>` in a Bash command: the sed argv without `-i` and
    without the file operands, applied to each file. `cd` is the leading
    `cd X &&` prefix, as for heredocs."""

    files: list[str]
    argv: list[str]
    cd: str | None = None


_SED_VALUE_OPTIONS = {"-e", "--expression", "-f", "--file", "-l", "--line-length"}


def _segments(command: str) -> list[list[str]]:
    """Simple commands of a Bash command line, as token lists, split on
    `&&`, `||`, `;`, `|` and newlines; heredoc bodies are dropped first."""
    stripped = HEREDOC_BODY.sub("<<HEREDOC", command).replace("\\\n", " ")
    lexer = shlex.shlex(stripped, posix=True, punctuation_chars="();<>|&\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return []
    segs: list[list[str]] = [[]]
    for tok in tokens:
        if tok.replace("\n", "") in ("&&", "||", ";", "|", ";;", "&") or not tok.strip("\n"):
            segs.append([])
        else:
            segs[-1].append(tok)
    return [seg for seg in segs if seg]


def parse_sed_in_place(command: str) -> list[SedInPlace]:
    """Every in-place sed in a Bash command. The script is passed through
    verbatim; the caller runs sed on the reconstructed content."""
    out: list[SedInPlace] = []
    cd = None
    for seg in _segments(command):
        if seg[0] == "cd" and len(seg) == 2:
            cd = seg[1]
            continue
        if seg[0] != "sed" or not any(t == "--in-place" or t.startswith("--in-place=") or (t.startswith("-i") and not t.startswith("--")) for t in seg[1:]):
            continue
        argv: list[str] = []
        files: list[str] = []
        have_script = False
        it = iter(seg[1:])
        for t in it:
            if t == "--in-place" or t.startswith("--in-place=") or (t.startswith("-i") and not t.startswith("--")):
                continue
            if t in _SED_VALUE_OPTIONS:
                argv += [t, next(it, "")]
                have_script = have_script or t in ("-e", "--expression", "-f", "--file")
                continue
            if t.startswith("--expression=") or t.startswith("--file="):
                argv.append(t)
                have_script = True
                continue
            if t.startswith("-") and t != "-":
                argv.append(t)
                continue
            if not have_script:
                argv.append(t)
                have_script = True
            else:
                files.append(t)
        if files:
            out.append(SedInPlace(files=files, argv=argv, cd=cd))
    return out


def parse_heredocs(command: str) -> list[Heredoc]:
    """Every heredoc-fed `cat` redirect in a Bash command. A form whose content
    is not literal (`<<-`, trailing shell text, unquoted delimiter with
    expansions) comes back with `body=None` and the reason."""
    cd = None
    m = _CD_PREFIX.match(command)
    if m:
        cd = m.group(1)
    out: list[Heredoc] = []
    for m in _HEREDOC.finditer(command):
        op, path, dash, quote, delim, tail, body = m.groups()
        reason = None
        if dash:
            reason = f"`<<-{delim}` strips tabs"
        elif tail.strip():
            reason = f"trailing shell text {tail.strip()!r} after the redirect"
        elif not quote and _SHELL_EXPANSION.search(body):
            reason = f"unquoted `<<{delim}` and the body has shell expansions"
        out.append(Heredoc(path=path.strip("'\""), append=(op == ">>"), body=None if reason else body + "\n", cd=cd, reason=reason, pos=m.start()))
    return out


@dataclass(frozen=True)
class PythonScript:
    """One heredoc-fed `python -` in a Bash command that rewrites a file by
    literal edits only. `edits` are ("append", text) / ("replace", old, new)
    in script order; `pos` is the script's offset in the command."""

    path: str
    edits: tuple[tuple, ...]
    pos: int
    cd: str | None = None


_PY_HEREDOC = re.compile(
    r"(?:^|&&|;|\|\||\n)[ \t]*(?:menv[ \t]+)?python3?[ \t]+-[ \t]*<<[ \t]*'(\w+)'[ \t]*\n(.*?)\n\1[ \t]*(?=\n|$)",
    re.DOTALL,
)


def _literal_edits(body: str) -> tuple[str, tuple[tuple, ...]] | None:
    """The file and edits of a script of the exact shape
    `import …; p = '<file>'; s = open(p…).read(); s = s.replace(<lit>, <lit>)…;
    s += <lit>…; for k, v in {<lit>: <lit>…}.items(): s = s.replace(k, v);
    open(p, 'w'…).write(s); print(…)`. None for anything else."""
    try:
        tree = ast.parse(body)
    except SyntaxError:
        return None
    path = None
    edits: list[tuple] = []
    seen: list[str] = []
    for st in tree.body:
        if isinstance(st, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
            name, value = st.targets[0].id, st.value
            if name == "p" and isinstance(value, ast.Constant) and isinstance(value.value, str) and path is None:
                path = value.value
                seen.append("path")
                continue
            if name == "s" and isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute):
                if value.func.attr == "read" and _opens_path(value.func.value, "r") and seen == ["path"]:
                    seen.append("read")
                    continue
                if (value.func.attr == "replace" and isinstance(value.func.value, ast.Name) and value.func.value.id == "s"
                        and len(value.args) == 2 and not value.keywords
                        and all(isinstance(a, ast.Constant) and isinstance(a.value, str) for a in value.args)
                        and seen[-1:] != ["write"] and "read" in seen):
                    edits.append(("replace", value.args[0].value, value.args[1].value))
                    continue
            return None
        if (isinstance(st, ast.AugAssign) and isinstance(st.op, ast.Add) and isinstance(st.target, ast.Name)
                and st.target.id == "s" and isinstance(st.value, ast.Constant) and isinstance(st.value.value, str)
                and "read" in seen and seen[-1:] != ["write"]):
            edits.append(("append", st.value.value))
            continue
        if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call):
            call = st.value
            if (isinstance(call.func, ast.Attribute) and call.func.attr == "write" and _opens_path(call.func.value, "w")
                    and len(call.args) == 1 and isinstance(call.args[0], ast.Name) and call.args[0].id == "s"
                    and "read" in seen and "write" not in seen):
                seen.append("write")
                continue
            if isinstance(call.func, ast.Name) and call.func.id == "print" and seen[-1:] == ["write"]:
                continue
        if (isinstance(st, ast.For) and "read" in seen and seen[-1:] != ["write"] and not st.orelse
                and isinstance(st.target, ast.Tuple) and len(st.target.elts) == 2
                and all(isinstance(t, ast.Name) for t in st.target.elts)
                and isinstance(st.iter, ast.Call) and isinstance(st.iter.func, ast.Attribute) and st.iter.func.attr == "items"
                and not st.iter.args and isinstance(st.iter.func.value, ast.Dict)
                and all(isinstance(k, ast.Constant) and isinstance(k.value, str) for k in st.iter.func.value.keys)
                and all(isinstance(v, ast.Constant) and isinstance(v.value, str) for v in st.iter.func.value.values)
                and len(st.body) == 1 and isinstance(st.body[0], ast.Assign) and len(st.body[0].targets) == 1
                and isinstance(st.body[0].targets[0], ast.Name) and st.body[0].targets[0].id == "s"
                and isinstance(st.body[0].value, ast.Call) and isinstance(st.body[0].value.func, ast.Attribute)
                and st.body[0].value.func.attr == "replace" and isinstance(st.body[0].value.func.value, ast.Name)
                and st.body[0].value.func.value.id == "s" and not st.body[0].value.keywords
                and [a.id for a in st.body[0].value.args if isinstance(a, ast.Name)] == [t.id for t in st.target.elts]):
            for k, v in zip(st.iter.func.value.keys, st.iter.func.value.values):
                edits.append(("replace", k.value, v.value))
            continue
        return None
    if path is None or seen[-1:] != ["write"]:
        return None
    return path, tuple(edits)


def _opens_path(node: ast.AST, mode: str) -> bool:
    """`open(p, …)` / `io.open(p, …)` on the script's `p`, in text mode `mode`
    (positional or `mode=`), utf-8 or unspecified encoding, no other keywords."""
    if not isinstance(node, ast.Call):
        return False
    f = node.func
    if not ((isinstance(f, ast.Name) and f.id == "open")
            or (isinstance(f, ast.Attribute) and f.attr == "open" and isinstance(f.value, ast.Name) and f.value.id == "io")):
        return False
    if not node.args or not (isinstance(node.args[0], ast.Name) and node.args[0].id == "p"):
        return False
    given = None
    if len(node.args) > 1:
        if len(node.args) > 2 or not isinstance(node.args[1], ast.Constant):
            return False
        given = node.args[1].value
    for kw in node.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
            given = kw.value.value
        elif kw.arg == "encoding" and isinstance(kw.value, ast.Constant) and str(kw.value.value).lower().replace("-", "") == "utf8":
            continue
        else:
            return False
    return (given or "r") == mode


def parse_python_scripts(command: str) -> list[PythonScript]:
    """Every literal-edit `python -` heredoc in a Bash command, in command
    order. A script of any other shape is not an op: the file's later state is
    whatever the next truth point says."""
    cd = None
    m = _CD_PREFIX.match(command)
    if m:
        cd = m.group(1)
    out: list[PythonScript] = []
    for m in _PY_HEREDOC.finditer(command):
        parsed = _literal_edits(m.group(2))
        if parsed is not None:
            out.append(PythonScript(path=parsed[0], edits=parsed[1], pos=m.start(), cd=cd))
    return out


# The hook (episode_stop.py) and the nb-collab stub run standalone in the container and carry their own parsing.
HEREDOC_BODY = re.compile(r"<<\s*-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\2[ \t]*(?=\n|$)", re.DOTALL)
HANDOFF_SUBCOMMANDS = ("execute-cell", "exec-all", "wait", "append")
# Only the measure notebook talks to instruments; executing an ana cell is analysis.
MEASURE_SUFFIX = "_measure.ipynb"
# Built-in tools the agent uses only to wait on a running measurement.
WAIT_TOOLS = ("ScheduleWakeup", "Monitor")


def handoff_invocation(command: str) -> str | None:
    """The nb-collab invocation that hands a cell to the rig, if the command has
    one: execute-cell / exec-all / wait, or append --execute, on a measure
    notebook. Heredoc bodies, --help calls and ana-notebook cells do not count;
    an invocation ends at its line."""
    stripped = HEREDOC_BODY.sub("<<HEREDOC", command).replace("\\\n", " ")
    lexer = shlex.shlex(stripped, posix=True, punctuation_chars="();<>|&\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return None
    i = 0
    while i < len(tokens):
        if tokens[i] == "nb-collab" and i + 1 < len(tokens) and tokens[i + 1] in HANDOFF_SUBCOMMANDS:
            j = i + 2
            while j < len(tokens) and not set(tokens[j]) <= set(lexer.punctuation_chars):
                j += 1
            # `2>/dev/null` lexes as `2`, `>`: the digit belongs to the redirect.
            args = [t for k, t in enumerate(tokens[i + 2 : j], i + 2)
                    if not (t.isdigit() and k + 1 < len(tokens) and tokens[k + 1][:1] in "<>")]
            ok = any(a.endswith(MEASURE_SUFFIX) for a in args) and not ({"--help", "-h"} & set(args))
            if ok and (tokens[i + 1] != "append" or "--execute" in args):
                return " ".join([tokens[i], tokens[i + 1], *args])
            i = j
        else:
            i += 1
    return None


NB_COLLAB_APPEND = re.compile(r"\bnb-collab\s+append\b")
# Where a run id shows up in a result, by the tool that prints it: the sweep
# library (lib/measureme/sweep/sweep.py: "Starting sweep with ID", "Data saved
# in …data/<id>/…"), hera-watch (src/hera/watch.py: the "# <id>  <kind>  <recipe>"
# header and "(known runs: …)"), summarize_run (src/hera/analysis.py: "run <id>"),
# and any path under data/.
_RUN_ID_SINGLE = (
    re.compile(r"\bdata[\\/]+(\d+)(?![\d])"),
    re.compile(r"\bStarting (?:multi)?sweep with ID (\d+)\b"),
    re.compile(r"^# (\d+)  \S", re.M),
    re.compile(r"^run (\d+)$", re.M),
)
_RUN_ID_LIST = re.compile(r"\(known runs: ([\d, ]+)\)")


_JUPYTER_URL = re.compile(r"connected: http://(?:localhost|127\.0\.0\.1):(\d+)\b")


def jupyter_port(t: "Transcript", cut_index: int) -> int:
    """The port nb-collab reported connecting to before the cut. The container's
    JupyterLab listens there so the agent's prior context stays true."""
    ports = set()
    for tc in t.calls_before(cut_index):
        ports.update(int(m) for m in _JUPYTER_URL.findall(tool_result_text_of(tc.result)))
    if len(ports) != 1:
        raise CutError(f"expected one JupyterLab port in nb-collab results before the cut, found {sorted(ports)}")
    return ports.pop()


def run_ids_in(text: str) -> list[int]:
    """Run ids a tool result names, in order of first appearance."""
    found: list[int] = []
    positions: list[tuple[int, int]] = []
    for rx in _RUN_ID_SINGLE:
        positions.extend((m.start(), int(m.group(1))) for m in rx.finditer(text))
    for m in _RUN_ID_LIST.finditer(text):
        positions.extend((m.start(), int(x)) for x in m.group(1).split(",") if x.strip())
    for _, rid in sorted(positions):
        if rid not in found:
            found.append(rid)
    return found
CELL_ID_IN_RESULT = re.compile(r"\bid=([\w-]+)")

_TOKEN_SPLIT = re.compile(r"[\s\"'`;&|()<>$]+")


def command_tokens(command: str) -> list[str]:
    return [t for t in _TOKEN_SPLIT.split(command) if t]


def notebooks_named(command: str, names: set[str]) -> set[str]:
    """Which of the archive's notebook file names a Bash command mentions."""
    return {n for n in names if n in command}


def first_line(s: str, n: int = 100) -> str:
    s = s.strip().splitlines()[0] if s.strip() else ""
    return s if len(s) <= n else s[: n - 1] + "…"


def walk_strings(obj, fn):
    """Apply fn to every string value in a JSON tree, returning the rewritten tree."""
    if isinstance(obj, str):
        return fn(obj)
    if isinstance(obj, list):
        return [walk_strings(x, fn) for x in obj]
    if isinstance(obj, dict):
        return {k: walk_strings(v, fn) for k, v in obj.items()}
    return obj


def all_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, list):
        for x in obj:
            yield from all_strings(x)
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from all_strings(v)


def tool_result_text_of(entry: Entry) -> str:
    """All text a tool_result entry carried, blocks joined."""
    parts = []
    for b in entry.blocks("tool_result"):
        content = b.get("content")
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            parts.extend(x.get("text", "") for x in content if isinstance(x, dict) and x.get("type") == "text")
    return "\n".join(parts)

