# Replay — running Codex CLI as the episode agent

Design and implementation record, 2026-09-22 (workstream E). Scope: fresh-start
cases (`fresh: {brief}`, the `vti02-fan-design-*` arms) on `hera-replay run`,
with OpenAI Codex CLI in place of `claude -p` (`runner: codex` in the case
file; `hera.replay.codex`). Resume is out of scope by definition. Not
agent-visible.

Facts below are from Codex 0.155.1 as installed on edhar and from runs in the
live corpus image `hera-agent:8bf4e7d.c13b07e9p-full` with the Codex binaries
bind-mounted (luna for plumbing, one astra consult, terra/sol for the episode
smokes — §8). Docs consulted: learn.chatgpt.com/docs (non-interactive-mode,
config-reference, config-advanced, hooks).

## Models

| Zack's name | id | default effort | efforts accepted | $/1M in · cached · out |
|---|---|---|---|---|
| sol | `gpt-5.6-sol` | low | low, medium, high, xhigh, max, ultra | 4.00 · 0.40 · 20.00 |
| astra | `gpt-6-astra` | medium | low, medium, high, xhigh, max, ultra | 10.00 · 1.00 · 50.00 |

Both `supported_in_api: true`, 272k context, `tool_mode: code_mode_only`.
Source: the CLI's `models_cache.json` and the `[tui.model_availability_nux]`
table in `~/.codex/config.toml`, which names exactly these two; prices from
developers.openai.com/api/docs/pricing (standard tier). Plumbing models:
`gpt-5.6-luna` (0.20 · 0.02 · 1.20), `gpt-5.6-terra` (2.00 · 0.20 · 12.00).
The case `run.effort` vocabulary (`low … max`) is accepted verbatim by
`model_reasoning_effort`.

## How Codex runs a command

Code mode: the model emits one JS script per tool call (`exec` custom tool)
that calls `tools.exec_command({cmd, workdir, login, yield_time_ms,
max_output_tokens})`, optionally several times; each `exec_command` is one
`command_execution` item in the stream and one PreToolUse event. The command
runs as `/bin/bash -c` or `/bin/bash -lc` (`login`, default true), through the
image's bash wrapper either way. `yield_time_ms` (the model picks, 10 s
typical) returns control with the process still running; `write_stdin` polls
it. A second binary, `codex-code-mode-host`, must sit beside `codex` or every
tool call fails closed.

## 1. Invocation

`hera.replay.codex.exec_args`:

```
docker exec -i -w <session_dir> <name> /bin/sh -c 'python3 /opt/hera/codex-config.py \
    && exec codex exec --json --skip-git-repo-check \
    --dangerously-bypass-approvals-and-sandbox --dangerously-bypass-hook-trust \
    -C <session_dir> -m <model> -c model_reasoning_effort="<effort>" \
    -c model_reasoning_summary="detailed" -o /tmp/last-message.txt -'
```

with the brief on stdin (`-`), `CODEX_HOME=/home/hera/.codex` in the
container env, and the episode's `codex-home/` dir mounted there (the analogue
of `claude-projects/`). `/bin/sh` so the render and the CLI start without the
wrapper's faketime; Codex's own shells go through the wrapper. Verified end to
end in §8. `model_reasoning_summary` puts the reasoning summaries in the
stream as `reasoning` items (the rollout's own are encrypted); without it the
stream shows none. astra's are headings only (a dozen words each).

- **Prompt.** Codex has no `--agent`. `developer_instructions` is the layer the
  agent prompt occupies: a developer message on top of the CLI's own base
  instructions (17.7k chars: "You are Codex…", personality, code-mode
  guidance), below the first user message. `model_instructions_file` would
  *replace* the base instructions — a different experiment. The prompt goes
  into `$CODEX_HOME/config.toml` as a TOML multi-line literal (`'''…'''`;
  neither prompt vintage contains `'''`; the render refuses one that does),
  frontmatter stripped, the harness notes (§2) prepended. `codex-config.py`
  (`hera/docker/`, at `/opt/hera/` in the image) renders it inside the
  container from the image's `hera/hera_tactical.md` right before `codex exec`,
  so a `prompt: corpus` overlay still takes the prompt from the corpus sha; it
  also writes `hooks.json`, the token file when one comes in the environment
  (§5), and prints one `hera.codex_config` line (sha256 of prompt, notes,
  instructions, config) that the run loop keeps with the stream events.
- **Config** (the rest of the rendered `config.toml`):

  ```toml
  web_search = "disabled"
  approval_policy = "never"
  sandbox_mode = "danger-full-access"
  project_doc_fallback_filenames = []
  [history]
  persistence = "save-all"
  [shell_environment_policy]
  inherit = "all"
  [features]
  multi_agent = false
  plugins = false
  apps = false
  recommended_plugins = false
  memories = false
  skill_search = false
  ```

  `inherit = "all"` is load-bearing: the default (`core`) drops `HERA_*`, and
  the stubs read `HERA_EPISODE_DIR` while the wrapper reads `HERA_FAKETIME`.
  Verified: with it, tool shells see `HERA_EPISODE_DIR`, `HERA_FAKETIME`, `TZ`,
  and the wrapper's `LD_PRELOAD`/`FAKETIME`. The feature flags remove the
  18k-char `<skills_instructions>` developer message (system skills) and the
  `<recommended_plugins>` user message Codex otherwise injects.
  `multi_agent = false` does not remove the 2.3k-char team preamble ("You are
  `/root`, the primary agent in a team… `spawn_agent`…"); Codex appends a
  271-char `<multi_agent_mode>` retraction after it instead. Ruled 2026-09-22:
  kept as is — what the harness gives. No episode called an agent tool.
  `features.web_search` is deprecated (a warning item); the top-level key is
  the one that works.
  Codex appends `[projects."<cwd>"] trust_level = "trusted"` to this file on
  first run — harmless, but the file is not byte-stable.
- **Sandbox.** Codex's own sandbox (bwrap/landlock) is not attempted: the
  bypass flag's documented purpose is "environments that are externally
  sandboxed", which the container is. No `--allowedTools` equivalent; the
  Claude allowlist's exclusions map to `multi_agent`/`web_search` off.
- **Working dir.** `-C` = `-w` = the session dir. No git repo there
  (`--skip-git-repo-check`). AGENTS.md discovery walks from cwd to a project
  root (`.git`; absent, cwd) plus `$CODEX_HOME/AGENTS.md`; neither exists.
- **No `--max-turns`, no `--session-id`, no allowlist.** One `codex exec` is one
  turn with an unbounded tool loop; the thread id arrives in `thread.started`.
  A `runner: codex` case therefore carries neither `run.max_turns` nor
  `allowed_tools` (`case.py` refuses both). Guards: `timeout_s`, `stall_s`, the
  marker (§3). A tool-call cap enforced by the hook is the option if one is
  wanted later.
- **`CODEX_HOME`** must not sit under `/tmp` (the CLI refuses to create its
  PATH helpers there; warns and proceeds, but `/tmp` is the episode's own
  mount). `/home/hera/.codex`, with `codex-home/` mounted over it.

Nathan's `run_pi` (`hera/evaluations/frontier/sample.py`) is the precedent for
a non-Claude runner; same shape, one level up in the container.

## 2. What the prompt relies on that Codex lacks

Inventory of `hera_tactical.md` (HEAD; the 13b07e9 corpus vintage differs by
two table cells, the 039b0f5 none vintage adds the `plan.md` mandate — same
inventory in all three):

| Site | Mechanism | Codex | Needed by a fresh fan-design episode? | Disposition |
|---|---|---|---|---|
| frontmatter `name`/`description` | Claude agent header | would sit in the developer message | no | strip |
| L353, 407, 429, 484 `run_in_background`; L429 "Claude Code background monitor" | Bash `run_in_background` | none; `exec_command` yields and the process keeps running, pollable via `write_stdin` | yes — arming `hera-watch --next --follow` is the handoff | one glossary line in the harness notes |
| L103 "a scheduled wakeup" (E1) | `ScheduleWakeup` | `sleep_tool` (stable, on) | no — the stubs end the episode at the handoff | leave |
| L353, 396 "~600 s foreground shell cap" | Claude Bash timeout | yield-based, no fixed cap | no | leave |
| L537 `NotebookEdit` | Claude tool in a "never" list | n/a | no | leave |
| §"Bash + Read + local python", L327 "then Read them" | Read tool | shell + `view_image` | no | leave |
| `@`-file refs, `Skill`/`/skills`, hooks, agent memory | — | — | not present in the prompt (zero sites) | — |

Harness-side Claude affordances the prompt never mentions: the
`.claude/settings.json` hook (§3), `--allowedTools`, `claude-projects/`,
`--session-id`, `--max-turns`, `BUN_OPTIONS` (§4).

**Harness notes block** (the declared delta; `hera/docker/codex-notes.md`,
prepended at render time, recorded in `episode.json` by sha256):

```
# Harness notes (Codex)
- This session runs under Codex CLI. Where the protocol says `run_in_background`,
  let the exec yield and poll the process; a yielded `hera-watch` keeps running.
- The date the harness reports is not the rig's clock. `date` in the shell is.
```

Two lines. Anything more is a different protocol.

## 3. The stop rule

Today: the `nb-collab` / `hera-watch` stubs write `episode-stop.json`; the
PreToolUse hook denies every later call with `continue: false`, and
`claude -p` exits with its result event.

**Codex hooks fire under `codex exec` and under code mode**, once per
`exec_command`, with a payload of the same shape as Claude's: `tool_name:
"Bash"`, `tool_input: {command}`, `tool_use_id: "exec-…"`, `cwd` (the session
dir), plus `model`, `permission_mode: "bypassPermissions"`, and
`transcript_path` (the rollout file). `hooks.json` lives in `CODEX_HOME`;
matcher `^Bash$`; `--dangerously-bypass-hook-trust` is required (two `error`
items in the stream announce it; harmless). Two contract differences from
Claude, both verified:

- `continue` and `stopReason` are **unsupported for PreToolUse** in 0.155.1
  (the binary carries the diagnostics), and an output containing them is
  rejected whole — the deny is silently dropped and the command runs. A bare
  `{"hookSpecificOutput": {"hookEventName": "PreToolUse",
  "permissionDecision": "deny", "permissionDecisionReason": …}}` blocks the
  command; so does exit code 2 with the reason on stderr. The model sees
  `Command blocked by PreToolUse hook: <reason>`.
- A deny does not end the turn. The turn ends when the model stops calling
  tools (2/2 luna runs stopped on the first denied call and wrote their final
  message; `turn.completed` then carries the usage).

So `episode_stop.py` ports nearly verbatim (the one append passed after a
watch arms included; the Codex copy is `hera/docker/codex-hook.py`, which also
logs every payload to `codex-home/hook-log.jsonl`), minus the two unsupported keys, and
the run loop keeps a **marker poll** as the backstop and the kill path
(`codex.marker_guard`, the `extra_guard` of `container.stream_claude`, a
fourth guard beside stall, timeout, interrupt):

1. `session/episode-stop.json` appears.
2. Settle: `tool == nb-collab` and the command is `append …` → wait for
   `append_landed` (the stub writes it after the real tool returns), cap 60 s.
   `tool == hera-watch` → the watch armed on the first appended code cell;
   wait up to 120 s for `append_landed` (the one further append the hook lets
   through), then stop either way. `execute-cell`/`exec-all`/`wait`
   handoff → stop now.
3. If `codex exec` has not exited by then, `stop_container` (JupyterLab gets
   TERM via the entrypoint trap and flushes the notebooks); guard =
   `stop_marker`, status `ok`.

Everything downstream is unchanged: `_notebook_diff` reads the session dir,
`stop_cell_sweeps` reads the marker's `cell_ids` against the appended cells,
the stubs are the same files. A yielded `hera-watch` stub (`sleep(60)` loop)
is harmless: the marker is already down.

## 4. Clock

`fakedate.js` shifts `Date` inside the Claude CLI's Bun runtime. Codex is a
static-pie musl binary: `LD_PRELOAD` does not apply, `clock_gettime` goes
through the vDSO so seccomp cannot intercept it, Linux time namespaces offset
only MONOTONIC/BOOTTIME, and no config or env overrides the date (astra
concurs). The CLI injects the real date once, into the first user turn's
`environment_context` (`<current_date>`, `<timezone>`); `current_time_reminder`
is a non-default feature, so there is no per-turn repeat.

Every tool shell reads the cut clock: Codex spawns `/bin/bash` (`-c` or `-lc`),
which on merged-`/usr` Debian is the wrapper, so `HERA_FAKETIME` applies as it
does for Claude's Bash. Verified: `date` → `Fri Aug 21 … PDT 2026`,
`python3 datetime.now()` the same, `ls -la` mtimes at the cut, in every run.

**Login-shell deadlock (fixed in the wrapper).** For `login: true` commands
Codex captures a login shell's environment once (`bash -l` → `declare -x`)
and replays it on each command. Through the wrapper that capture contains
`LD_PRELOAD` and the capturing shell's `FAKETIME_SHARED` (libfaketime names
its semaphore/shm after the first process and `putenv`s it for children). The
capturing shell has exited, so every replayed process blocks in libfaketime's
constructor (`__futex_wait`) before its first instruction — the wrapper's
own interpreter included, so no script-level fix can run. Reproduced without
a model (a child with an inherited or bogus `FAKETIME_SHARED` hangs; unset,
it runs) and in 7/7 model runs that took the login path; `login: false`
calls never hang, which is why some runs "worked" (luna often opts out; terra
opted out after four hangs). Neither `features.shell_snapshot = false` nor
`shell_environment_policy.exclude = ["FAKETIME_SHARED"]` reaches the replayed
environment.

Fix: the wrapper's interpreter becomes static (`#!/bin/busybox sh`,
`busybox-static`), which `LD_PRELOAD` cannot touch; it does `unset
FAKETIME_SHARED`, exports the faketime vars, and execs `/bin/bash.real`.
Verified: a poisoned environment runs and gets a fresh segment; `login: true`
commands complete under faketime (3/3, cut date read). The Claude path is
unaffected: its shells never inherit a dead segment, and a fresh segment per
shell start is what they already get.

Disposition: the Codex model is told the real date once; the harness notes
point it at `date`; `episode.json` records `clock: {shells: "faketime",
agent_date: "real"}`.

## 5. Image

One image serves both runners. The Dockerfile installs `codex` and
`codex-code-mode-host` from the release tarballs
(`<name>-x86_64-unknown-linux-musl.tar.gz`, one binary each, 269 MB + 69 MB)
right after the Claude install so the layer caches across corpus/condition
builds; adds `busybox-static` for the wrapper (§4); creates `/home/hera/.codex`
for the mount; and ships `codex-config.py`, `codex-notes.md`, `codex-hook.py`
beside `fakedate.js` under `/opt/hera/`. `build.sh` pins `CODEX_VERSION=0.155.1`
beside `CLAUDE_VERSION`, records it in `.hera-image.json` and the labels as
`codex_version`, and folds the three new files into `docker_dir_sha256`. Tags
stay as they are: the runner is a case key, not an image axis, and both CLIs
are inert until exec'd. Rebuilding a tag replaces the image the Claude arms
ran on; the metadata's `docker_dir_sha256` and `codex_version` tell the two
apart.

**Credentials.** Never mount `~/.codex`. `container.credential_env("codex")`:

- `CODEX_API_KEY` in the host env → passed through (nothing on disk, API
  billing). Built, unused: there is no key for these runs.
- else `~/.config/hera/codex-home/auth.json`, the harness's own ChatGPT login
  (`CODEX_HOME=~/.config/hera/codex-home codex login`) → base64 in
  `HERA_CODEX_AUTH_JSON`, read per episode; the exec-time render writes it to
  `$CODEX_HOME/auth.json` mode 600. Refresh tokens rotate: a CLI that refreshes
  mid-episode spends the one it was given, so `codex.write_back_auth` copies the
  rotated file over the host credential (compare-and-swap under a lock,
  `run.auth_writeback`: `written` / `unchanged` / `conflict`) before
  `codex.scrub_secrets` deletes it from the episode (`run.secrets_removed`). A
  credential sharing its refresh token with the operator's `~/.codex` login is
  refused: whichever side refreshed second would be logged out. Billed to the
  plan's weekly window.

Both names are in `SECRET_ENV`, so the run log and the recorded `docker.run`
argv redact them.

## 6. Records

Codex's `--json` stream carries tokens (`turn.completed.usage`) but no model,
version, effort or cost. The rollout
(`$CODEX_HOME/sessions/YYYY/MM/DD/rollout-<ts>-<thread_id>.jsonl`, written
incrementally, path also given in every hook payload's `transcript_path`)
carries all of them: `session_meta` (`cli_version`, `cwd`,
`base_instructions`), `turn_context` (`model`, `effort`, `sandbox_policy`,
`developer_instructions`), every `response_item` (developer/user/assistant
messages, `custom_tool_call` + output, reasoning), a `token_usage_record`
after each model response (`usage`, `turn_token_usage`, `thread_token_usage`)
and `event_msg: token_count` after each tool result. A rollout killed mid-command
keeps everything up to the last response (verified). It is the transcript a
Codex episode archives, under `codex-home/`.

Per-episode `run` block (`run.py` + `codex.collect`); the session-derived
fields (`stop`, `stop_cell_sweeps`, `notebooks`, `cells_appended`,
`notifications`, `appended_cells.json`) are computed the same way for both
runners:

| Field | Codex source |
|---|---|
| `runner` (`claude` on every claude record; `run.json` carries it too) | case key |
| `model.pinned` / `model.observed` | case / `turn_context.model` over the rollout |
| `effort` / `effort_observed` | case / `turn_context.effort`; drift → `model_mismatch` |
| `codex_version` (in place of `claude_version`) | `{image: codex_version, observed: session_meta.cli_version}` |
| `tokens` | `turn.completed.usage` when the turn completed, else the last `token_usage_record.thread_token_usage`. Mapping: `input_tokens − cached_input_tokens → input`, `cached_input_tokens → cache_read`, `cache_write_input_tokens → cache_creation`, `output_tokens → output` (includes `reasoning_output_tokens`). OpenAI's `input_tokens` is inclusive of cached; Claude's is not. `tokens_source`: `stream`, `rollout` or `none` |
| `cost_usd` / `cost_source` | `src/hera/replay/prices.toml` (dated, per model id) |
| `turns.num_turns` | `null` (one Codex turn) |
| `turns.api_messages` | assistant `response_item` messages in the rollout |
| `turns.tool_calls` / `commands_completed` / `exec_items` | `command_execution` items started / completed in the stream (one per `exec_command`); code-mode scripts in the rollout |
| `result` | `{subtype: turn.completed or turn.failed, is_error, error, usage}`; `null` when the marker poll killed the turn |
| `max_turns`, `allowed_tools` | `null` |
| `rollout` | path under `codex-home/`, entries, token records |
| `config` | the `hera.codex_config` line: prompt / notes / instructions / config sha256, `auth` mode |
| `hook_events`, `stream_errors`, `auth_writeback`, `secrets_removed` | hook payload count; `error` items in the stream (the trust warnings); whether a rotated token reached the host credential (§5); the token file, if deleted |
| `clock` | `{shells: "faketime", agent_date: "real"}` |
| `outputs.stderr` | `codex-stderr.txt` |

Status (`codex.status`): `stop_marker` → `ok` (`no_stop` without a marker);
other guards by name; `turn.failed` or a non-zero exit → `error`;
`turn.completed` → `ok`/`no_stop` by the marker. For both runners an `error`,
`stall` or `timeout` with usage-limit evidence (`hera.replay.quota`: a
rejected rate-limit event, a limit message in the error result, `turn.failed`,
stderr, or the rollout's `rate_limit_reached_type`) becomes `quota`, with the
evidence as the record's `quota` block. `summary.csv` is unchanged.
`hera-grade` reads only `session/` and `episode.json["run"]` (`image`, and
`case` for the claim rectangle); the extractor stays `claude -p` on the corpus
image regardless of who wrote the cells.

**Case file.** `runner: codex` (default `claude`); `allowed_tools` and
`run.max_turns` refused under it. Arm files:
`vti02-fan-design-{sol,astra}-{corpus,none}.yaml`.

## 7. Implementation

Files: `hera/docker/{Dockerfile,build.sh,bash-wrapper,codex-config.py,codex-notes.md,codex-hook.py}`,
`src/hera/replay/{codex.py,prices.toml}`, `case.py` (`runner`), `container.py`
(credential branch, secrets, `codex-home` mount, `extra_guard`), `run.py`
(runner branch, `_collect_codex`, `_collect_session`, `_status`), the four arm
cases, `tests/hera/test_replay_codex.py` (29 tests). `summarize.py`,
`materialize.py` and the grader are untouched.

Risks, in order:

1. **Protocol drift.** The Codex model sits on 17.7k chars of Codex base
   instructions (personality, code-mode guidance, "collaborate with the
   user") plus the multi-agent preamble and its retraction under our
   protocol; Claude sits on Claude Code's. Symmetric in kind, not in content.
   A Codex column is a *harness × model* column, and the doc of record should
   say so.
2. **Clock.** The model is told the real date once (§4).
3. **Rate limits.** Plan-billed auth throttles a matrix; a limit surfaces as
   `turn.failed`. Concurrent sessions on one login are untested.
4. **Version drift.** The image pins the release tarballs; `cli_version` is
   recorded per episode. The hook contract (unsupported keys) is a per-version
   fact.
5. **Tool-call counts** are not 1:1 with Claude's (one code-mode script,
   several commands).
6. **Login-shell deadlock** is fixed at the wrapper; any future shell-spawning
   path that replays a captured environment would resurface it. The
   `commands_completed` count against `tool_calls` is the check.

Cost class: luna plumbing runs are cents; terra ~$0.50 an episode; sol ~$1.1–1.4;
astra ~$1 for the prep-cell episodes seen so far.

## 8. Smokes (2026-09-22)

Mechanism runs (luna, low): E1–E5 and runs 11–21 established §1, §3, §4 as
written. One astra consult (medium, ~$0.50) identified the unsupported hook
keys from the binary's diagnostics. Episode runs on the fan-design cut
(`vti02-fan-design-fable-corpus` 20260922T155920, corpus brief, corpus-vintage
prompt), hand-driven with the marker poll and the hook installed:

| Model | Outcome |
|---|---|
| terra, medium (first) | every default-login command hung (§4); the model switched to `login:false` after four tries and continued; stopped by hand |
| terra, medium (static wrapper) | 226 s, 28 commands all completed on the login path, ~$0.50 (977k in, 880k cached, 10.5k out). Read cards, brief recipes, notebooks, every run on disk, the scratch analyses and the forward model; landed a three-cell Si-control analysis in the ana notebook; designed the fan (15 × 417, n 3.35→2.0e12, B 0→10 T, wrote it to `hera_scratch/`); then armed `hera-watch data --next --follow` **before** appending, called `nb-collab append --help`, was denied (correctly: not an append), and ended its turn. `turn.completed` present; marker from the watch stub; no measure cell — the watch-first prep pattern, excluded and counted as on the Claude arms |
| sol, medium | 556 s, 42 commands all completed, ~$1.40 (1.90M in, 1.80M cached, 14.5k out). Same read sequence (cards, notes, both notebooks by `nb`, run metadata, scratch analyses, five recipes); landed a raw-first three-cell Si-control analysis in ana (one `edit-cell` + re-execute after its first version assumed a helper from the dead kernel); **landed a paired markdown + code fan cell in the measure notebook** (`landau-fan-vti`, D = 0 electron side, n 1.90→3.35e12 × 25, B 2.4→10 T × 34 uniform in 1/B, 3.0 samples per F_L period by its own check, priced 1 h 40 min from run 4's measured overhead, preconditions asserted, coverage trade stated); armed `hera-watch data --next --follow`; then tried `nb-collab execute-cell` on the measure notebook (E1 habit; also what the live 08-21 agent did), denied by the hook; ended its turn with a summary. `turn.completed` present; marker from the watch stub; `stop_cell_sweeps` true; fan-design grade below |

**Sol fan, `fan-design` grade** (`b_cut` 2.0 T, m = 3, same grader revision
as the Claude smokes in the plan of record; extractor `claude-opus-5`, $0.55;
scored under `vti02-fan-design` by setting `run.case` in the episode's
`episode.json`, which the harness will do for real):

| Arm (n = 1) | Landed | Resolved fraction | Min rows/period | Episode cost |
|---|---|---|---|---|
| Fable + corpus | fan, 1/B, 91 rows 10→2.2 T | 0.886 | 7.85 | $5.78 |
| Opus + corpus | fan, 1/B, 71 rows 9.95→1.2 T | 0.962 | 2.94 | $4.14 |
| sol + corpus | fan, 1/B, 34 rows 2.4→10 T, 25 columns | 0.792 | 3.27 | ~$1.40 |
| sol, none | fan, 1/B, 81 rows 2.4→10 T, 39 columns, 2 h | 0.792 | 7.81 | ~$1.10 |
| astra + corpus (n = 2) | prep cell both times: a read-only VERIFY / kernel-binding probe appended with `--execute`, 50–66 s | excluded | — | ~$0.9 each |
| astra, none | prep cell: kernel-binding probe with `--execute` after a three-cell raw audit of runs 6–7 in ana, 112 s | excluded | — | ~$1.0 |

Sol sampled at the recipe's m ≈ 3 on the nose with the corpus ("3.0 samples
per period" by its own check) and at m ≈ 8 without it, and lost resolved
fraction both times by starting at 2.4 T, 08-21's own onset read, against the
grader's 2.0 T cut (0.4 T unsampled) — the same `b_cut` sensitivity the plan
flags for the Claude arms. Electron side, `B_max_ratio` 1.25, no flags, in
both arms.

**Astra ends on the brief's own first E1 act, 3/3.** The brief's autonomy
section says the first E1 execute is a read-only kernel-binding probe, then
VERIFY; astra does exactly that, with `--execute`, and the stub counts it as
the handoff. Sol and the Claude arms skip straight to the design. This is the
prep-cell exclusion the plan already counts (1/6 on QC0426, the 08-24 corpus
smoke), but at 3/3 it makes the astra column unmeasurable at this frontier
without the fake rig or a brief that asserts the probe already ran — a ruling,
not a harness fix.

**Through the harness** (`hera-replay run vti02-fan-design-sol-corpus.yaml --n 1
--model gpt-5.6-luna --effort low`, run `20260922T173453`): cut, container,
render, `codex exec`, stream, rollout and record all as designed; 101 s, 13
commands all completed, `tokens_source: stream`, $0.03, 13 hook payloads,
`secrets_removed: ["auth.json"]`, `docker.run` redacted; luna analysed and
ended its turn without a cell → `no_stop`.

Hand-driven episodes: hooks fired on every command (44 payloads on sol), the
rollout carried model/effort/version, no shell hung, `date` read the cut
clock throughout, and the model was told the real date once. Residual
scaffolding with the §1 flags: the 2.3k-char multi-agent team preamble and
its `<multi_agent_mode>` retraction still appear (`features.multi_agent =
false` does not remove them for these `multi_agent_version: v2` models);
the skills and plugin messages are gone.

Throwaway artifacts on edhar: image `hera-codex-test:wrapper` (the corpus
image + busybox-static + the static wrapper), the scratchpad driver and the
two episode dirs (`ep-gpt-5.6-terra-*`, `ep-gpt-5.6-sol-*`, each with
`transcript.jsonl`, `codex-home/` rollout + hook log, `appended_cells.json`).
