"""Rig-path rewrite for the container, and the corpus text its reads show.

Two path rules, derived from the transcript's own cwd: the rig session dir
becomes the container session dir, and any other path under the rig home moves
under the container home. Every match is tallied by class so the episode records
what was touched.

`CorpusReads` is the second rewrite: a pre-cut read of a recipe, crop or model is
re-served from the case's corpus sha, so the sha governs the text the resumed
agent carries as well as the files it can open.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from hera.replay.errors import CutError
from hera.replay.transcript import CONTAINER_HOME, RigLayout, Transcript, ToolCall, _segments, command_tokens, first_line

_REST = r"(?:[\\/]+[^\s\"'`<>|;&()\[\]{}*?,:=\\/]+)*(?<!\.)[\\/]*"


@dataclass
class RewriteTally:
    counts: Counter = field(default_factory=Counter)
    home_other: Counter = field(default_factory=Counter)

    def as_json(self) -> dict:
        return {
            "session_dir": self.counts["session_dir"],
            "measurement_env": self.counts["measurement_env"],
            "home_other": self.counts["home_other"],
            "tilde_session_dir": self.counts["tilde_session_dir"],
            "home_other_paths": sorted(self.home_other),
        }


class PathRewriter:
    def __init__(self, layout: RigLayout):
        self.layout = layout
        self.tally = RewriteTally()
        # The CLI's task-output paths carry whatever spelling %TEMP% gave the home
        # (the toploader's is the 8.3 form `C:\Users\TOPLOA~1`); the AppData tail
        # is what identifies them, so the home prefix is matched loosely there.
        alt = r"(?:[A-Za-z]:[\\/]+Users[\\/]+[^\s\\/]+(?=[\\/]+AppData[\\/]+Local[\\/]+Temp[\\/]+claude[\\/]))"
        self._abs = re.compile(rf"(?<![A-Za-z0-9+/=])(?:{layout.home_pattern}|{alt})(?P<rest>{_REST})")
        # `~/x/../<session>` hops (the agent wrote `cd ~/measurement_env/../VTI_local_data/…`) are the session dir too.
        self._tilde = re.compile(
            rf"(?<![\w/])~[\\/]+(?:[^\s\\/]+[\\/]+\.\.[\\/]+)*{layout.session_rel_pattern}(?P<rest>{_REST})"
        )
        self._session_rel = re.compile(rf"^[\\/]+{layout.session_rel_pattern}(?=[\\/]|$)")

    def _components(self, rest: str) -> list[str]:
        return [c for c in re.split(r"[\\/]+", rest) if c]

    def _abs_sub(self, m: re.Match) -> str:
        rest = m.group("rest")
        trailing = "/" if rest and rest[-1] in "\\/" else ""
        sm = self._session_rel.match(rest)
        if sm:
            self.tally.counts["session_dir"] += 1
            tail = self._components(rest[sm.end():])
            return "/".join([self.layout.container_session_dir, *tail]) + trailing
        comps = self._components(rest)
        cls = "measurement_env" if comps[:1] == ["measurement_env"] else "home_other"
        self.tally.counts[cls] += 1
        out = "/".join([CONTAINER_HOME, *comps]) + trailing
        if cls == "home_other":
            self.tally.home_other[out] += 1
        return out

    def _tilde_sub(self, m: re.Match) -> str:
        self.tally.counts["tilde_session_dir"] += 1
        rest = m.group("rest")
        trailing = "/" if rest and rest[-1] in "\\/" else ""
        tail = self._components(rest)
        return "/".join([f"~/measurements/{self.layout.user}/{self.layout.session}", *tail]) + trailing

    def __call__(self, s: str) -> str:
        s = self._abs.sub(self._abs_sub, s)
        return self._tilde.sub(self._tilde_sub, s)


# --- corpus reads -------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]
CORPUS_DIRS = ("recipes", "crops", "models")
# What each condition empties in the image (hera/docker/build.sh STRIP): a read of
# one of these under that condition finds nothing, whatever the sha holds.
STRIPPED = {"none": ("hera/recipes/", "hera/crops/")}
ARCHIVED_READS = {"mode": "archived"}


def corpus_rel(path: str) -> str | None:
    """The repo-relative corpus path a rig path names, matched on its
    `hera/<recipes|crops|models>/…` tail: the archives spell the same file
    `C:\\Users\\…\\measurement_env\\hera\\…`, `/c/Users/…` and `~/measurement_env/…`."""
    comps = [c for c in re.split(r"[\\/]+", path.strip("'\"")) if c not in ("", ".")]
    for i in range(len(comps) - 1):
        if comps[i] == "hera" and comps[i + 1] in CORPUS_DIRS:
            return "/".join(comps[i:])
    return None


@dataclass(frozen=True)
class Corpus:
    """The sha a case's pre-cut corpus reads are served from."""

    sha: str
    condition: str
    repo: Path | None = None  # the checkout the text comes from; the harness's own by default

    @property
    def root(self) -> Path:
        return self.repo or REPO_ROOT

    def verify(self) -> None:
        proc = subprocess.run(["git", "-C", str(self.root), "rev-parse", "--verify", f"{self.sha}^{{commit}}"],
                              capture_output=True, text=True)
        if proc.returncode:
            raise CutError(f"corpus sha {self.sha} is not a commit in {self.root}")

    def content(self, rel: str) -> str | None:
        """The file's text at the sha, or None when the image carries no such file."""
        if rel.startswith(STRIPPED.get(self.condition, ())):
            return None
        proc = subprocess.run(["git", "-C", str(self.root), "show", f"{self.sha}:{rel}"],
                              capture_output=True, text=True, encoding="utf-8")
        return proc.stdout if proc.returncode == 0 else None


@dataclass
class _Substitution:
    tool_use_id: str
    content: str
    tool_use_result: object
    is_error: bool


class CorpusReads:
    """Pre-cut reads of corpus files, re-served from the case's corpus sha.

    A Read (whole or partial) and a lone `cat <file>` are substituted; every other
    shell form naming a corpus path stays archived and is logged, so what the
    resumed context still carries from the session's own corpus is visible."""

    def __init__(self, t: Transcript, cut_index: int, corpus: Corpus):
        corpus.verify()
        self.corpus = corpus
        self.layout = t.layout
        self.rewritten: list[dict] = []
        self.unrewritten: list[dict] = []
        self._subs: dict[int, _Substitution] = {}
        for tc in t.calls_before(cut_index):
            if tc.name == "Read":
                rel = corpus_rel(str(tc.input.get("file_path") or ""))
                if rel is not None:
                    self._read(tc, rel)
            elif tc.name == "Bash":
                self._bash(tc)

    def apply(self, index: int, raw: dict) -> dict:
        """The entry as the resumed transcript carries it."""
        sub = self._subs.get(index)
        if sub is None:
            return raw
        blocks = []
        for b in raw.get("message", {}).get("content") or []:
            if isinstance(b, dict) and b.get("tool_use_id") == sub.tool_use_id:
                b = {**b, "content": sub.content, **({"is_error": True} if sub.is_error else {})}
            blocks.append(b)
        return {**raw, "message": {**raw["message"], "content": blocks}, "toolUseResult": sub.tool_use_result}

    def as_json(self) -> dict:
        return {"mode": "corpus", "sha": self.corpus.sha, "condition": self.corpus.condition,
                "rewritten": self.rewritten, "unrewritten": self.unrewritten}

    # -- one call
    def _read(self, tc: ToolCall, rel: str) -> None:
        tur = tc.tool_use_result
        if tc.is_error or not isinstance(tur, dict) or not isinstance(tur.get("file"), dict):
            return self._skip(tc, [rel], "the archived Read carries no file payload")
        if tur.get("type") == "file_unchanged":
            return self._skip(tc, [rel], "the archived Read was answered file-unchanged; the text is the earlier read's")
        f = tur["file"]
        if tur.get("type") == "image" or "content" not in f:
            return self._skip(tc, [rel], "not a text read; only text is re-served")
        text = tc.result_text
        eol = "\r\n" if "\r\n" in text else "\n"
        new = self.corpus.content(rel)
        if new is None:
            missing = f"File does not exist. Note: your current working directory is {tc.call.cwd or self.layout.cwd}."
            return self._sub(tc, rel, _Substitution(tc.id, missing, f"Error: {missing}", True), f["content"], None)
        # The Read tool counts the empty line a trailing newline leaves, and numbers it.
        lines = new.replace("\r\n", "\n").split("\n")
        start = int(tc.input.get("offset") or 1)
        limit = tc.input.get("limit")
        shown = lines[start - 1: start - 1 + int(limit)] if limit else lines[start - 1:]
        content = eol.join(shown)
        # The line-number column is right-aligned to whatever width the archived result used.
        m = re.match(r"([ \t]*\d+)\t", text)
        width = len(m.group(1)) if m else 0
        numbered = eol.join(f"{n:>{width}}\t{line}" for n, line in enumerate(shown, start))
        file_field = {**f, "content": content, "numLines": len(shown), "startLine": start, "totalLines": len(lines)}
        self._sub(tc, rel, _Substitution(tc.id, numbered, {**tur, "file": file_field}, False), f["content"], content,
                  partial=bool(limit or tc.input.get("offset")))

    def _bash(self, tc: ToolCall) -> None:
        command = tc.input.get("command", "")
        paths: list[str] = []
        for tok in command_tokens(command):
            rel = corpus_rel(tok)
            if rel is not None and rel not in paths:
                paths.append(rel)
        if not paths:
            return
        segs = [s for s in _segments(command) if s[0] != "cd"]
        operand = segs[0][1] if len(segs) == 1 and len(segs[0]) == 2 and segs[0][0] == "cat" else ""
        rel = corpus_rel(operand)
        if rel is None:
            return self._skip(tc, paths, f"shell form other than `cat <file>`: {first_line(command, 60)}")
        tur = tc.tool_use_result
        if tc.is_error or not isinstance(tur, dict) or "stdout" not in tur:
            return self._skip(tc, paths, "the archived `cat` did not succeed")
        text = tc.result_text
        eol = "\r\n" if "\r\n" in text else "\n"
        archived = tur["stdout"]
        new = self.corpus.content(rel)
        if new is None:
            missing = f"Exit code 1\ncat: {_shell_path(operand, self.layout)}: No such file or directory"
            return self._sub(tc, rel, _Substitution(tc.id, missing, f"Error: {missing}", True), archived, None)
        body = _relines(new, eol)
        # The CLI trims the trailing newline off a command's output; and whatever it
        # appended after that output (a cwd reset) still applies.
        if not archived.endswith("\n"):
            body = body.rstrip("\r\n")
        suffix = text[len(archived):] if text.startswith(archived) else ""
        self._sub(tc, rel, _Substitution(tc.id, body + suffix, {**tur, "stdout": body}, False), archived, body)

    # -- the log
    def _sub(self, tc: ToolCall, rel: str, sub: _Substitution, archived: str, substituted: str | None,
             partial: bool = False) -> None:
        if tc.result_index in self._subs:
            raise CutError(f"line {tc.result_index}: two corpus reads share one tool_result entry")
        self._subs[tc.result_index] = sub
        record = {"line": tc.result_index, "uuid": tc.result.uuid, "tool": tc.name, "path": rel,
                  "archived_sha256": _sha(archived),
                  "substituted_sha256": None if substituted is None else _sha(substituted),
                  "identical": substituted == archived}
        if substituted is None:
            record["missing_at_sha"] = True
        if partial:
            record["partial"] = True
        self.rewritten.append(record)

    def _skip(self, tc: ToolCall, paths: list[str], reason: str) -> None:
        self.unrewritten.append({"line": tc.result_index, "uuid": tc.result.uuid if tc.result else None,
                                 "tool": tc.name, "paths": paths, "reason": reason})


def _relines(text: str, eol: str) -> str:
    """The text under the archived result's line-ending convention."""
    lf = text.replace("\r\n", "\n")
    return lf if eol == "\n" else lf.replace("\n", eol)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _shell_path(path: str, layout: RigLayout) -> str:
    """What the shell handed `cat`: bash expands a leading `~`, which Git Bash
    spells `/c/Users/<name>`."""
    if not path.startswith("~"):
        return path
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", layout.home)
    home = f"/{m.group(1).lower()}/{m.group(2)}".replace("\\", "/") if m else layout.home
    return home + path[1:]
