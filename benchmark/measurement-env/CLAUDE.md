# measurement-env

uv-managed measurement environment for Sharpe Lab's toploader cryostat.
Lives at `~/measurement_env` on the toploader PC.

## Working with Zack

Three modes — wait for the signal before switching:
- **Discussion** — sketch, propose, ask questions. No file writes.
- **Coding** — "build it" or similar. Write code, run syntax checks. No commits.
- **Deploying** — "commit" or "commit and push". Only then touch git.

Do not commit, push, or take destructive git actions unless explicitly asked.

See `WORKSTREAM.md` (gitignored) for current work-in-progress state.

## Running

```bash
uv run measurement-env-toploader   # launch a rig GUI (also -vti, -pink)
uv run pytest              # run tests
```

## Key Files

- `pyproject.toml` — dependency manifest (sweep, measurebot, qcodes, jupyterlab, etc.)
- `src/gui/qt/` — Qt (PyQt5) launcher layer: `base_launcher.py` (scaffolding + tray + single-instance + close-to-tray), `worker_panel.py`, `jupyter_panel.py` (shared JL panel, venv-pinned `-m jupyterlab` launch), `toploader_launcher.py` (`measurement-env-toploader`: adds new-run + UPS panels), `vti_launcher.py` (`measurement-env-vti`), `pink_launcher.py` (`measurement-env-pink`), `avs_probe_panel.py` (probe/channel/EXC dropdowns), `qcs_panel.py` (heater controls)
- `src/gui/influx_health.py` — `fetch_last_writes()` + `InfluxHealthPoller` (daemon thread, no Qt); a panel is healthy only while every metric it lists is fresh
- `src/core/config.py` — shared config schema: `BaseConfig` + per-rig `ToploaderConfig`/`VtiConfig`/`PinkConfig` (one loader; `load_config`/`load_vti_config`/`load_pink_config`)
- `toploader.toml` / `vti.toml` / `pink.toml` — local per-rig config: InfluxDB, hardware addresses, health thresholds (gitignored)
- `toploader.toml.example` / `vti.toml.example` / `pink.toml.example` — committed templates
- `templates/toploader_measure.ipynb` — measurement notebook template
- `templates/toploader_ana.ipynb` — analysis notebook template (TODO)
- `scripts/generate_icon.py` — generates the SR830 icon in `assets/`
- `lib/measureme/` — vendored in-tree (from measureme's `sharpelab` branch), provides `sweep`
- `lib/measurebot/` — vendored in-tree, provides alerts and UPS monitoring
- `src/workers/thorlabs_thermo.py` — Thorlabs TSP01B temp/humidity worker
- `src/workers/vti_he_level.py` — VTI He level worker (AMI 1700, poll driver)
- `src/workers/vti_pressure.py` — VTI probe-space pressure worker (Terranova 906A, poll driver)
- `src/workers/vti_l218.py` — VTI Lakeshore 218 magnet/gm temperature worker (poll driver)
- `src/workers/lc_scraper.py` — LC log file tailer (`--family FP|PT`)
- `src/workers/pink_scraper.py` — pink fridge LC/AVS log tailer (`--family FP|TC`), byte-exact port of the rig's legacy publisher
- `src/workers/avs_calibration.py` — AVS-47B calibration curves + sensor arrays (pure numpy)
- `src/workers/avs_fridge.py` / `avs_probe.py` — AVS-47B fridge scanner (all 6 channels) / probe single-channel worker (poll driver, persistent GPIB)
- `src/workers/qcs_heater.py` — QCS heater worker (first command-taking worker: JSON over stdin; `--sim` for hardware-free dev)
- `src/drivers/leiden_qcs.py` — Leiden QCS v1 driver (MCC USB-3101 via mcculw; `QCS_V1_MAP` pending pin-map extraction — see docs/plans/QCS_HEATER_CONTROL.md)
- `src/gui/qt/qcs_panel.py` — heater panel (per-channel setpoint/on/off/lamp); the toploader launcher shows it once `hardware.qcs_board_num` is set
- `docs/worker-architecture.md` — worker stdout protocol and conventions
- `docs/plans/` — design/migration plans (e.g. `LAUNCHER_QT_PLAN.md` — the Qt launcher architecture)
- `AVS_PLAN.md` — AVS bridge integration plan (fridge + probe)
- `TODO.md` — roadmap

## HERA tooling

`hera/` holds the agent stack for live measurement sessions — agent prompts,
the recipe corpus, rig/device cards, templates, and the post-session triage
loop. See [`hera/CLAUDE.md`](hera/CLAUDE.md) for the full map.

Installed via `scripts/install.sh` (re-run after pulls): agent prompts →
`~/.claude/agents/`; launcher shims → `~/.local/bin/` (`hera-session`,
`hera-archive`, `chiron`, `iris`, `nb`, `nb-collab`, `menv`, `newclaude`).

HERA runs bill the Anthropic AI for Science award (Console org "Sharpe Lab"),
one workspace per kind of run: `hera-rig` (live sessions: `hera-session`,
`hera-tactical`, `iris`), `hera-offline` (replay benchmark, ablations), `hera-dev`
(harness development, `chiron`). Launchers fetch the key with `hera-key <role>`
from `~/.config/hera/keys/<role>` and refuse to start without it, so a HERA
session never silently bills a personal subscription. The replay harness already
honors `ANTHROPIC_API_KEY`: run it with `ANTHROPIC_API_KEY=$(hera-key offline)`.

## How It Works

The launcher GUI lets users:
1. Create a new run — picks user + device name, copies dated templates into `~/measurements/<user>/<name>/`
2. Start/stop JupyterLab — rooted at `~/measurements`
3. Start/stop hardware workers — subprocess scripts using stdout protocol (see docs/worker-architecture.md)
4. Monitor aggregate health — status panel shows green/yellow/red based on worker state, InfluxDB freshness, and Jupyter

Notebooks import from `sweep` and `measurebot` (path installs from `lib/`) and
`sharpelab_nb` (part of this package, under `src/`).

## Conventions

- **No inline imports** — all imports at top of file. Conditional imports OK when guarding optional deps.
- Toploader-specific constants live in `sharpelab_nb.constants.TOPLOADER`
- Instrument drivers in `sharpelab_nb.drivers` (SRS_DC205, Yokogawa7651)
- Measurement configs use `sharpelab_nb.build_measurement_config(mc, contact_pairs)`
- Temperature readout via `sharpelab_nb.thermometry.temperature_from_logfiles`
- Rig launchers subclass `gui.qt.base_launcher.BaseLauncher`: `_make_workers()` returns the panel list; rig-only panels go in `_build_pre_worker_panels()` / `_build_post_worker_panels()`
- `_log(tag, msg)` — tag is required, use component name (e.g. "jupyter", "health")
- Health checks configured in `[health.*]` sections of `<rig>.toml` (`metrics = [...]`, `threshold`)
- `ComponentStatus(ok, message)` tracks each component; `_refresh_status()` recomputes aggregate
- `WorkerPanel(name=, desc=)` — titled "Instrument - function"; owns `InfluxHealthPoller`, has `refresh_ui()`/`get_status()`/`shutdown()`
- Single `_tick()` (1s) on launcher drives `refresh_ui()` on all panels then `_refresh_status()`
- Workers use `start_with_output()` with `on_waiting/on_ready/on_failed/on_died/on_data` callbacks
- `[data]` JSON can include `_summary` key for inline status (e.g. `"_summary": "23.4C — Oh so chilly!"`)
- Hardware workers are `core.poller` Sources (connect/close/read) + a publish callable; AVS workers keep persistent GPIB sessions with the `wait_opc()` timeout wrapper
- `jupyterlab` and `jupyter-collaboration` are a paired version surface — bumping one without re-verifying the other can silently break RTC. Re-run `hera/nb-collab/PLAN.md` probes after any change.

## Toploader PC

- **SSH**: `ssh toploader` (toploader-1.[tailnet].ts.net via Tailscale)
- **User**: toploader
- **OS**: Windows 11
- **Default shell**: Git Bash (set via OpenSSH DefaultShell registry key)
- **Repo**: `~/measurement_env`
- **Package manager**: uv

SSH commands use bash syntax (`ls`, `cat`, etc.). For PowerShell, use `powershell -c "..."`.

## Platform

Develops on Linux, deploys on Windows (toploader PC). Keep both working:
- Process kill: `taskkill /T /F` on Windows, `os.killpg` on Unix
- `os.startfile` is Windows-only (guarded by `sys.platform`)
- Paths: use `Path` / `as_posix()` for URLs, never hardcode separators
- `creationflags=_NO_WINDOW` suppresses console windows on Windows (no-op on Linux)

## InfluxDB

- **Server**: `https://metrics.aaronsharpe.science` (InfluxDB 2.7.6, AWS EC2)
- **Org**: `dgg` / **Bucket**: `023_toploader`
- **Auth**: API token in `toploader.toml`

| Measurement | Source scripts | Key metrics | Write interval |
|---|---|---|---|
| `LC_scrapper` | `lc_scraper.py --family FP` | P1-P7, Flow, Pc, MG0-5 | 60s |
| `LC_scrapper` | `lc_scraper.py --family PT` | PT1.ON, W_in/out, He, Oil, P_low/high, I_mtr, Status | 60s |
| `thorlabs_thermo` | `thorlabs_thermo.py` | temp, humidity | 60s |
| `AVS_bridge` | `avs_probe.py` | P<probe>_<sensor> (selection-named) + `probe status` (always) | 15s |
| `AVS_bridge` | `avs_fridge.py` | 3K_low, 50mK, Still, MixingCh_low/high, Magnet | ~210s |
| `AVS_bridge` | `magnet.py` | magnetic field (Tesla via AMI430); `--rig pink` adds `ramping state` + `quenched` into `AMI430` | 30s |
| `QCS` | `qcs_heater.py` | 3K/Still/MC `_on` + `_current` (µA; `_current` absent until first setpoint) | 30s + on command |
