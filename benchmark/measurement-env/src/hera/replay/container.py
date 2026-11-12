"""Docker primitives for `hera-replay run`.

One episode is one container: the image's entrypoint serves JupyterLab over the
episode's session dir, and the `claude -p` turn — resumed or fresh — runs as
`docker exec` into it. Every docker invocation goes through `_docker` so tests replace the
whole surface.
"""

from __future__ import annotations

import base64
import json
import os
import queue
import secrets
import string
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

NAME_PREFIX = "hera-replay-"
GRADE_PREFIX = "hera-grade-"
TAG_CHARS = string.ascii_lowercase + string.digits

DOCKER = "docker"
IMAGE_PREFIX = "hera-agent"
BUILD_SCRIPT = "hera/docker/build.sh"
CONTAINER_HOME = "/home/hera"
CONTAINER_REPO = f"{CONTAINER_HOME}/measurement_env"
CONTAINER_PYTHON = f"{CONTAINER_REPO}/.venv/bin/python"
IMAGE_METADATA = f"{CONTAINER_REPO}/.hera-image.json"
MEASUREMENTS_ROOT = f"{CONTAINER_HOME}/measurements"
STUB_BIN = f"{CONTAINER_HOME}/.local/bin"
FAKEDATE_JS = "/opt/hera/fakedate.js"
AGENT = "hera-tactical"
# Every rig is in the same lab: the CLI's injected date, tool shells, JupyterLab and
# the kernels read the rig's local time, as the archived transcripts do.
RIG_TZ = "America/Los_Angeles"
OAUTH_TOKEN_FILE = Path.home() / ".config" / "hera" / "claude-oauth-token"
# Codex: the harness's own ChatGPT login (`CODEX_HOME=~/.config/hera/codex-home codex login`),
# passed into the container as base64 and written by the exec-time render. Refresh tokens
# rotate, so a copy of the operator's `~/.codex` login would kill whichever side refreshes second.
CODEX_AUTH_FILE = Path.home() / ".config" / "hera" / "codex-home" / "auth.json"
CODEX_HOME_MOUNT = "/home/hera/.codex"
READY_TIMEOUT_S = 60.0
STOP_TIMEOUT_S = 20


class DockerError(RuntimeError):
    """A docker command failed, or an image/credential the run needs is missing."""


def stamp() -> str:
    """UTC second plus a random tag (`20260922T201530-k3f9qz`): names sort by time, and
    two processes minting one in the same second never collide."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S-") + "".join(secrets.choice(TAG_CHARS) for _ in range(6))


def _docker(args: list[str], *, stdin_text: str | None = None, timeout: float | None = None,
            check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run([DOCKER, *args], input=stdin_text, capture_output=True, text=True, timeout=timeout)
    if check and proc.returncode:
        raise DockerError(f"docker {' '.join(args[:2])} failed ({proc.returncode}): "
                          f"{(proc.stderr or proc.stdout).strip()[-800:]}")
    return proc


def _user_spec() -> str:
    return f"{os.getuid()}:{os.getgid()}"


def docker_version() -> dict:
    proc = _docker(["version", "--format", "{{json .}}"], timeout=60)
    v = json.loads(proc.stdout)
    return {"client": v["Client"]["Version"], "server": v["Server"]["Version"]}


# ------------------------------------------------------------------ images
def image_tag(sha: str, condition: str, *, corpus_sha: str | None = None, corpus_prompt: bool = False) -> str:
    """Tag for one (code, corpus, condition). `sha` is the whole image unless `corpus_sha`
    overlays a corpus onto it, which build.sh marks with `.c<corpus7>` (plus `p` when the
    agent prompts come from the corpus too)."""
    stem = sha[:7] if corpus_sha is None else f"{sha[:7]}.c{corpus_sha[:7]}{'p' if corpus_prompt else ''}"
    return f"{IMAGE_PREFIX}:{stem}-{condition}"


def build_command(sha: str, condition: str, *, corpus_sha: str | None = None, corpus_prompt: bool = False) -> str:
    overlay = "" if corpus_sha is None else f" --corpus {corpus_sha}" + (" --corpus-prompt" if corpus_prompt else "")
    return f"{BUILD_SCRIPT} {sha}{overlay} {condition}"


def resolve_image(sha: str, condition: str, *, corpus_sha: str | None = None, corpus_prompt: bool = False) -> dict:
    """Tag + image id for a condition. Missing images are the operator's to build: an
    auto-build here would silently pick up an unreviewed working tree."""
    tag = image_tag(sha, condition, corpus_sha=corpus_sha, corpus_prompt=corpus_prompt)
    proc = _docker(["image", "inspect", "--format", "{{.Id}}", tag], check=False, timeout=60)
    if proc.returncode:
        raise DockerError(f"image {tag} is not built; run:\n    "
                          + build_command(sha, condition, corpus_sha=corpus_sha, corpus_prompt=corpus_prompt))
    return {"tag": tag, "id": proc.stdout.strip()}


def image_metadata(tag: str) -> dict:
    """The build stamp baked into the image (corpus sha, condition, strip list, claude version)."""
    proc = _docker(["run", "--rm", "--entrypoint", "cat", tag, IMAGE_METADATA], check=False, timeout=120)
    if proc.returncode:
        raise DockerError(f"{tag} carries no {IMAGE_METADATA}: {proc.stderr.strip()[-300:]}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as err:
        raise DockerError(f"{tag}: {IMAGE_METADATA} is not JSON: {err}") from None


# ------------------------------------------------------------------ credentials
def credential_env(runner: str = "claude") -> dict[str, str]:
    """Whichever credential the host carries. `~/.claude` and `~/.codex` are never
    mounted: the container gets a token, not the operator's logged-in CLI state."""
    if runner == "codex":
        key = os.environ.get("CODEX_API_KEY")
        if key:
            return {"CODEX_API_KEY": key}
        if CODEX_AUTH_FILE.exists():
            auth = CODEX_AUTH_FILE.read_bytes()
            if refresh_token(auth) and refresh_token(auth) == refresh_token(_operator_codex_auth()):
                raise DockerError(f"{CODEX_AUTH_FILE} shares its refresh token with the operator's Codex login; "
                                  f"give the harness its own:\n    CODEX_HOME={CODEX_AUTH_FILE.parent} codex login")
            return {"HERA_CODEX_AUTH_JSON": base64.b64encode(auth).decode("ascii")}
        raise DockerError(f"no Codex credential: set CODEX_API_KEY, or log the harness in:\n"
                          f"    CODEX_HOME={CODEX_AUTH_FILE.parent} codex login")
    token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if token:
        return {"CLAUDE_CODE_OAUTH_TOKEN": token}
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return {"ANTHROPIC_API_KEY": key}
    if OAUTH_TOKEN_FILE.exists():
        return {"CLAUDE_CODE_OAUTH_TOKEN": OAUTH_TOKEN_FILE.read_text(encoding="utf-8").strip()}
    raise DockerError("no Claude credential: set CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY, "
                      f"or write the OAuth token to {OAUTH_TOKEN_FILE}")


def _operator_codex_auth() -> bytes:
    path = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex") / "auth.json"
    return path.read_bytes() if path.exists() else b""


def refresh_token(auth: bytes) -> str | None:
    try:
        return (json.loads(auth).get("tokens") or {}).get("refresh_token")
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
        return None


SECRET_ENV = ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "CODEX_API_KEY", "HERA_CODEX_AUTH_JSON")


def redact(argv: list[str]) -> list[str]:
    return [f"{a.split('=', 1)[0]}=<redacted>" if a.split("=", 1)[0] in SECRET_ENV else a for a in argv]


def redact_text(text: str, secrets: list[str]) -> str:
    """Exception text can quote a whole docker argv, token included."""
    for secret in secrets:
        if secret:
            text = text.replace(secret, "<redacted>")
    return text


# ------------------------------------------------------------------ episode container
def run_args(name: str, image: str, episode_dir: Path, *, session_dir: str, stubs: dict[str, Path],
             faketime_s: int, jupyter_port: int, credential: dict[str, str], codex_home: Path | None = None) -> list[str]:
    """`docker run` argv for one episode. The session mount nests inside an empty
    measurements root so JupyterLab's tree holds the session and nothing else. `/tmp`
    is the episode's own dir, so what the agent stages there is archived with it.
    `codex_home` (a codex runner) is mounted as the CLI's home, where its config is
    rendered and its rollout lands — the `claude-projects/` of that runner."""
    episode_dir = Path(episode_dir)
    env = {
        "HOME": CONTAINER_HOME,
        **credential,
        "HERA_EPISODE_DIR": session_dir,
        "HERA_FAKETIME": f"-{faketime_s}",
        "HERA_JL_ROOT": MEASUREMENTS_ROOT,
        "HERA_JL_PORT": str(jupyter_port),
        "TZ": RIG_TZ,
        **({"CODEX_HOME": CODEX_HOME_MOUNT} if codex_home is not None else {}),
    }
    args = ["run", "-d", "--name", name, "--user", _user_spec(),
            "-v", f"{episode_dir / 'mnt'}:{MEASUREMENTS_ROOT}",
            "-v", f"{episode_dir / 'session'}:{session_dir}",
            "-v", f"{episode_dir / 'claude-projects'}:{CONTAINER_HOME}/.claude/projects",
            "-v", f"{episode_dir / 'tmp'}:/tmp"]
    if codex_home is not None:
        args += ["-v", f"{Path(codex_home)}:{CODEX_HOME_MOUNT}"]
    for stub, path in stubs.items():
        args += ["-v", f"{path}:{STUB_BIN}/{stub}:ro"]
    for key, value in env.items():
        args += ["-e", f"{key}={value}"]
    args += ["-w", session_dir, image]
    return args


def start_container(args: list[str]) -> str:
    return _docker(args, timeout=300).stdout.strip()


def container_running(name: str) -> bool:
    proc = _docker(["inspect", "-f", "{{.State.Running}}", name], check=False, timeout=30)
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def container_logs(name: str, tail: int = 40) -> str:
    proc = _docker(["logs", "--tail", str(tail), name], check=False, timeout=30)
    return (proc.stdout + proc.stderr).strip()[-2000:]


def replay_containers() -> list[str]:
    """Every episode and extraction container that exists, running or not."""
    proc = _docker(["ps", "-a", "--filter", f"name={NAME_PREFIX}", "--filter", f"name={GRADE_PREFIX}",
                    "--format", "{{.Names}}"], timeout=60)
    return sorted(line for line in proc.stdout.splitlines() if line.startswith((NAME_PREFIX, GRADE_PREFIX)))


def stop_container(name: str) -> None:
    _docker(["stop", "-t", str(STOP_TIMEOUT_S), name], check=False, timeout=STOP_TIMEOUT_S + 60)


def remove_container(name: str) -> None:
    _docker(["rm", "-f", name], check=False, timeout=120)


def _ready_probe(port: int) -> str:
    return ("import sys, urllib.request\n"
            "try:\n"
            f"    urllib.request.urlopen('http://127.0.0.1:{port}/api/status', timeout=2)\n"
            "except Exception as e:\n"
            "    print(e)\n"
            "    sys.exit(1)\n")


def wait_for_jupyter(name: str, port: int, timeout_s: float = READY_TIMEOUT_S, poll_s: float = 1.0,
                     stop: threading.Event | None = None) -> float:
    """Block until the container's JupyterLab answers /api/status. Returns seconds waited."""
    t0 = time.monotonic()
    detail = ""
    while time.monotonic() - t0 < timeout_s:
        if stop is not None and stop.is_set():
            raise DockerError("interrupted before JupyterLab was ready")
        if not container_running(name):
            raise DockerError(f"{name} exited before JupyterLab came up: {container_logs(name)}")
        probe = _docker(["exec", name, CONTAINER_PYTHON, "-c", _ready_probe(port)], check=False, timeout=30)
        if probe.returncode == 0:
            return round(time.monotonic() - t0, 1)
        detail = (probe.stdout + probe.stderr).strip()[-300:]
        time.sleep(poll_s)
    raise DockerError(f"JupyterLab in {name} not ready after {timeout_s:.0f}s: {detail}")


def _open_sessions(port: int, paths: list[str]) -> str:
    return ("import json, urllib.request\n"
            f"for path in {paths!r}:\n"
            "    body = json.dumps({'path': path, 'type': 'notebook', 'name': path, 'kernel': {'name': 'python3'}}).encode()\n"
            f"    req = urllib.request.Request('http://127.0.0.1:{port}/api/sessions', data=body, method='POST',\n"
            "                                 headers={'Content-Type': 'application/json'})\n"
            "    urllib.request.urlopen(req, timeout=30)\n")


def open_notebook_sessions(name: str, port: int, paths: list[str]) -> None:
    """One kernel session per notebook (paths relative to the JupyterLab root), as
    hera-session's preflight leaves them: nb-collab binds the kernel it finds
    instead of forking one on the agent's first call."""
    probe = _docker(["exec", name, CONTAINER_PYTHON, "-c", _open_sessions(port, paths)], check=False, timeout=120)
    if probe.returncode:
        raise DockerError(f"could not open notebook sessions in {name}: {(probe.stdout + probe.stderr).strip()[-300:]}")


# ------------------------------------------------------------------ the agent's turn
def exec_args(name: str, *, session_dir: str, resume: bool, session_id: str, model: str, effort: str,
              max_turns: int, allowed_tools: list[str], faketime_s: int) -> list[str]:
    """`resume` continues the staged transcript `session_id`; otherwise a new
    instance starts under that id, so its session jsonl lands at a known path."""
    # --allowedTools is variadic and goes last: a trailing positional would be swallowed by it,
    # which is why the prompt goes on stdin.
    return [DOCKER, "exec", "-i", "-w", session_dir,
            "-e", f"BUN_OPTIONS=--preload {FAKEDATE_JS}", "-e", f"HERA_FAKE_OFFSET_MS={faketime_s * 1000}",
            name, "claude", "-p", "--agent", AGENT, "--model", model, "--effort", effort,
            "--output-format", "stream-json", "--verbose", "--resume" if resume else "--session-id", session_id,
            "--max-turns", str(max_turns), "--allowedTools", ",".join(allowed_tools)]


def _feed_stdin(proc: subprocess.Popen, prompt: str) -> None:
    try:
        assert proc.stdin is not None
        proc.stdin.write(prompt)
        proc.stdin.close()
    except (BrokenPipeError, OSError, ValueError):
        pass


def _pump_stdout(stream, sink: "queue.Queue[str | None]") -> None:
    try:
        for line in stream:
            sink.put(line)
    finally:
        sink.put(None)


def stream_claude(cmd: list[str], prompt: str, transcript_path: Path, stderr_path: Path, *,
                  timeout_s: float, stall_s: float, on_guard, on_event=None,
                  stop: threading.Event | None = None, extra_guard=None) -> dict:
    """Run one agent turn (`claude -p`, or `codex exec`, both JSONL on stdout) and
    stream it to disk line by line.

    Three guards: no event for `stall_s` (the session is dead), `timeout_s` of wall
    clock (hard backstop), and the run's `stop` event (an interrupt); `extra_guard`,
    called once a second, may name a fourth (the codex runner's marker poll). Any one
    calls `on_guard` and keeps the partial stream. Returns the parsed events, the
    exit code, and which guard fired, if any."""
    events: list[dict] = []
    lines: "queue.Queue[str | None]" = queue.Queue()
    # A fresh env for the docker client: the host's nested-session markers would
    # make the exec'd claude think it runs inside another Claude Code.
    env = {k: v for k, v in os.environ.items() if not (k.startswith("CLAUDE_") or k == "CLAUDECODE")}
    guard: str | None = None
    t0 = time.monotonic()
    with open(stderr_path, "w", encoding="utf-8") as err_fh:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=err_fh,
                                text=True, env=env, start_new_session=True)
        threading.Thread(target=_feed_stdin, args=(proc, prompt), daemon=True).start()
        threading.Thread(target=_pump_stdout, args=(proc.stdout, lines), daemon=True).start()
        last = t0
        with open(transcript_path, "w", encoding="utf-8") as tfh:
            while True:
                now = time.monotonic()
                if stop is not None and stop.is_set():
                    guard = "interrupted"
                elif now - t0 > timeout_s:
                    guard = "timeout"
                elif now - last > stall_s:
                    guard = "stall"
                elif extra_guard is not None:
                    guard = extra_guard()
                if guard:
                    on_guard(guard)
                    break
                try:
                    line = lines.get(timeout=1.0)
                except queue.Empty:
                    continue
                if line is None:
                    break
                last = time.monotonic()
                tfh.write(line)
                tfh.flush()
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(event, dict):
                    events.append(event)
                    if on_event:
                        on_event(event)
        try:
            rc = proc.wait(timeout=60)
        except subprocess.TimeoutExpired:
            proc.kill()
            rc = proc.wait()
    return {"events": events, "returncode": rc, "guard": guard, "wall_s": round(time.monotonic() - t0, 1)}
