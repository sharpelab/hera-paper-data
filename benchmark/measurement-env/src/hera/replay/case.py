"""The case file for `hera-replay run`: what to replay, on which corpus, how.

Two unions. Where the episode comes from: `source` + `cut` (cut from an archive
per run), `episode` (an already-cut bundle), or `session` (a hand-built session
dir with no transcript behind it, and the time it stands at). How the agent
starts: `resume` (the archived transcript continues) or `fresh` (a new instance
whose first message is the brief the block names; that text is also the
episode's `hera_session.md`).

Every other key is required and nothing else is accepted — bar the corpus block's
`harness` and `prompt`, which name the overlay image, and its `reads`, which
says whether the pre-cut corpus reads show the archived text or the corpus sha's
— and a value the run cannot use aborts here, before any container starts. `${VAR}` in a path is
expanded from the environment and must be set; a relative path is relative to
the case file.

`runner` picks the agent CLI: `claude` (default) or `codex` (`hera.replay.codex`).
Codex has no tool allowlist and no turn cap, so a codex case carries neither
`allowed_tools` nor `run.max_turns`.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml

from hera.replay.errors import CutError

EFFORTS = ("low", "medium", "high", "xhigh", "max")
RUNNERS = ("claude", "codex")
PROMPT_SOURCES = ("harness", "corpus")
READ_SOURCES = ("archived", "corpus")
STARTS = ("resume", "fresh")
RUN_KEYS = {"model": str, "effort": str, "n": int, "timeout_s": (int, float), "stall_s": (int, float), "max_turns": int}
_VAR = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


@dataclass(frozen=True)
class Case:
    path: Path
    name: str
    source: Path | None
    episode: Path | None
    session: Path | None          # a hand-built session dir; fresh only
    session_ts: datetime | None   # the time that session stands at: the episode's clock and mtimes
    session_user: str | None      # names the container path, measurements/<user>/<dir name>
    cut_transcript: str | None
    cut_at: str | None
    corpus_sha: str
    condition: str
    harness_sha: str | None   # the code the corpus is overlaid onto; None when the corpus sha is the whole image
    prompt_source: str        # "harness" or "corpus" — which sha the agent prompts come from
    read_source: str          # "archived" or "corpus" — which text the pre-cut corpus reads show
    model: str
    effort: str
    n: int
    timeout_s: float
    stall_s: float
    max_turns: int | None                 # None under runner codex
    allowed_tools: tuple[str, ...] | None  # None under runner codex
    runner: str                            # "claude" or "codex"
    grader: str | None      # hera/graders/<name>; null for a decision point that has no grader yet
    start: str                  # "resume" or "fresh"
    resume_close: str | None    # the synthetic assistant line that closes the cut turn (the agent's own next words)
    resume_prompt: str | None   # the operator's turn that resumes the episode
    brief_path: Path | None     # fresh: the brief file
    brief_text: str | None      # fresh: its text — the first message, and the episode's hera_session.md
    mask_path: Path | None      # edits to the materialized state, every arm alike (hera.replay.mask)
    raw: dict


def _expand_path(value: str, base: Path, where: str) -> Path:
    def sub(m: re.Match) -> str:
        v = os.environ.get(m.group(1))
        if v is None:
            raise CutError(f"{where}: ${{{m.group(1)}}} is not set in the environment")
        return v

    p = Path(os.path.expanduser(_VAR.sub(sub, value)))
    return p if p.is_absolute() else (base / p).resolve()


def _mapping(d: object, keys: set[str], where: str, optional: set[str] = frozenset()) -> dict:
    if not isinstance(d, dict):
        raise CutError(f"{where}: expected a mapping")
    missing = keys - d.keys()
    extra = d.keys() - keys - optional
    if missing or extra:
        raise CutError(f"{where}: missing {sorted(missing)}, unknown {sorted(extra)}")
    return d


def load_case(path: Path) -> Case:
    path = Path(path).resolve()
    if not path.is_file():
        raise CutError(f"case file not found: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise CutError(f"{path.name}: not a mapping")
    top = set(raw)
    has_cut = {"source", "cut"} <= top
    origins = [k for k, present in (("source + cut", has_cut), ("episode", "episode" in top), ("session", "session" in top)) if present]
    if len(origins) != 1:
        raise CutError(f"{path.name}: give exactly one of source + cut (cut per run), episode (pre-cut) or "
                       f"session (hand-built), got {origins or 'none'}")
    origin = origins[0]
    starts = [k for k in STARTS if k in top]
    if len(starts) != 1:
        raise CutError(f"{path.name}: give exactly one of resume (the archived transcript continues) or "
                       f"fresh (a new instance, the brief as its first message), got {starts or 'none'}")
    start = starts[0]
    runner = raw.get("runner", "claude")
    if runner not in RUNNERS:
        raise CutError(f"{path.name}: runner must be one of {RUNNERS}, got {runner!r}")
    codex = runner == "codex"
    if codex and "allowed_tools" in raw:
        raise CutError(f"{path.name}: allowed_tools has no meaning under runner codex (no tool allowlist); drop it")
    _mapping(raw, {"case", "corpus", "run", "grader", start} | ({"allowed_tools"} if not codex else set())
             | set(origin.split(" + ")), path.name, {"mask", "runner"})
    mask_path = None
    if "mask" in raw:
        if not isinstance(raw["mask"], str):
            raise CutError(f"{path.name}: mask must be a path")
        mask_path = _expand_path(raw["mask"], path.parent, f"{path.name}: mask")
        if not mask_path.is_file():
            raise CutError(f"{path.name}: mask not found: {mask_path}")
    resume_close = resume_prompt = brief_path = brief_text = None
    if start == "resume":
        resume = _mapping(raw["resume"], {"close", "prompt"}, f"{path.name}: resume")
        for key in ("close", "prompt"):
            if not isinstance(resume[key], str) or not resume[key].strip() or "\n" in resume[key]:
                raise CutError(f"{path.name}: resume.{key} must be one non-empty line")
        resume_close, resume_prompt = resume["close"].strip(), resume["prompt"].strip()
        if origin == "session":
            raise CutError(f"{path.name}: a hand-built session has no transcript to resume; it starts fresh")
    else:
        fresh = _mapping(raw["fresh"], {"brief"}, f"{path.name}: fresh")
        if not isinstance(fresh["brief"], str):
            raise CutError(f"{path.name}: fresh.brief must be a path")
        brief_path = _expand_path(fresh["brief"], path.parent, f"{path.name}: fresh.brief")
        if not brief_path.is_file():
            raise CutError(f"{path.name}: fresh.brief not found: {brief_path}")
        brief_text = brief_path.read_text(encoding="utf-8")
        if not brief_text.strip():
            raise CutError(f"{path.name}: fresh.brief is empty: {brief_path}")
    name = raw["case"]
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
        raise CutError(f"{path.name}: case must be a [A-Za-z0-9._-] name, got {name!r}")
    corpus = _mapping(raw["corpus"], {"sha", "condition"}, f"{path.name}: corpus", {"harness", "prompt", "reads"})
    for key in ("sha", *(("harness",) if "harness" in corpus else ())):
        if not isinstance(corpus[key], str) or not re.fullmatch(r"[0-9a-f]{7,40}", corpus[key]):
            raise CutError(f"{path.name}: corpus.{key} must be a hex sha, got {corpus[key]!r}")
    if not isinstance(corpus["condition"], str) or not corpus["condition"]:
        raise CutError(f"{path.name}: corpus.condition must be a name")
    prompt_source = corpus.get("prompt", "harness")
    if prompt_source not in PROMPT_SOURCES:
        raise CutError(f"{path.name}: corpus.prompt must be one of {PROMPT_SOURCES}, got {prompt_source!r}")
    if prompt_source == "corpus" and "harness" not in corpus:
        raise CutError(f"{path.name}: corpus.prompt only chooses between the two shas, so it needs corpus.harness")
    read_source = corpus.get("reads", "archived")
    if read_source not in READ_SOURCES:
        raise CutError(f"{path.name}: corpus.reads must be one of {READ_SOURCES}, got {read_source!r}")
    if start == "fresh" and read_source == "corpus":
        raise CutError(f"{path.name}: corpus.reads rewrites the resumed transcript; a fresh start stages none")
    if codex and isinstance(raw["run"], dict) and "max_turns" in raw["run"]:
        raise CutError(f"{path.name}: run.max_turns has no meaning under runner codex (no turn cap); drop it")
    run_keys = {k: t for k, t in RUN_KEYS.items() if not (codex and k == "max_turns")}
    run = _mapping(raw["run"], set(run_keys), f"{path.name}: run")
    for key, typ in run_keys.items():
        if isinstance(run[key], bool) or not isinstance(run[key], typ):
            raise CutError(f"{path.name}: run.{key} must be {typ.__name__ if isinstance(typ, type) else 'a number'}, got {run[key]!r}")
    if run["effort"] not in EFFORTS:
        raise CutError(f"{path.name}: run.effort must be one of {EFFORTS}, got {run['effort']!r}")
    for key in ("n", *(() if codex else ("max_turns",))):
        if run[key] < 1:
            raise CutError(f"{path.name}: run.{key} must be >= 1")
    for key in ("timeout_s", "stall_s"):
        if run[key] <= 0:
            raise CutError(f"{path.name}: run.{key} must be > 0")
    tools = None if codex else raw["allowed_tools"]
    if not codex and (not isinstance(tools, list) or not tools
                      or not all(isinstance(t, str) and re.fullmatch(r"[A-Za-z]+", t) for t in tools)):
        raise CutError(f"{path.name}: allowed_tools must be a non-empty list of tool names")
    grader = raw["grader"]
    if grader is not None and (not isinstance(grader, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", grader)):
        raise CutError(f"{path.name}: grader must be a grader dir name or null, got {grader!r}")
    source = episode = session = session_ts = session_user = cut_transcript = cut_at = None
    if origin == "source + cut":
        if not isinstance(raw["source"], str):
            raise CutError(f"{path.name}: source must be a path")
        source = _expand_path(raw["source"], path.parent, f"{path.name}: source")
        cut = _mapping(raw["cut"], {"transcript", "at"}, f"{path.name}: cut")
        cut_transcript, cut_at = cut["transcript"], cut["at"]
        if not isinstance(cut_transcript, str) or not cut_transcript.endswith(".jsonl"):
            raise CutError(f"{path.name}: cut.transcript must be the tactical transcript's file name")
        if not isinstance(cut_at, str) or not re.fullmatch(r"[0-9a-f-]{36}", cut_at):
            raise CutError(f"{path.name}: cut.at must be an entry uuid, got {cut_at!r}")
    elif origin == "session":
        block = _mapping(raw["session"], {"dir", "ts", "user"}, f"{path.name}: session")
        if not isinstance(block["dir"], str):
            raise CutError(f"{path.name}: session.dir must be a path")
        session = _expand_path(block["dir"], path.parent, f"{path.name}: session.dir")
        session_user = block["user"]
        if not isinstance(session_user, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", session_user):
            raise CutError(f"{path.name}: session.user must be a [A-Za-z0-9._-] name, got {session_user!r}")
        try:
            # YAML reads an unquoted timestamp as a datetime already.
            session_ts = block["ts"] if isinstance(block["ts"], datetime) else datetime.fromisoformat(block["ts"])
        except (TypeError, ValueError):
            raise CutError(f"{path.name}: session.ts must be an ISO timestamp, got {block['ts']!r}") from None
        if session_ts.tzinfo is None:
            raise CutError(f"{path.name}: session.ts must carry a UTC offset, got {block['ts']!r}")
        block["ts"] = session_ts.isoformat()
    else:
        if not isinstance(raw["episode"], str):
            raise CutError(f"{path.name}: episode must be a path")
        episode = _expand_path(raw["episode"], path.parent, f"{path.name}: episode")
    return Case(
        path=path, name=name, source=source, episode=episode, session=session, session_ts=session_ts,
        session_user=session_user, cut_transcript=cut_transcript, cut_at=cut_at,
        corpus_sha=corpus["sha"], condition=corpus["condition"],
        harness_sha=corpus.get("harness"), prompt_source=prompt_source, read_source=read_source,
        model=run["model"], effort=run["effort"], n=run["n"], timeout_s=float(run["timeout_s"]),
        stall_s=float(run["stall_s"]), max_turns=None if codex else run["max_turns"],
        allowed_tools=None if tools is None else tuple(tools), runner=runner, grader=grader,
        start=start, resume_close=resume_close, resume_prompt=resume_prompt, brief_path=brief_path,
        brief_text=brief_text, mask_path=mask_path, raw=raw,
    )
