# Worker Architecture

Workers are long-running subprocess scripts that talk to hardware and push data to InfluxDB. The launcher manages their lifecycle via `ManagedProcess` and communicates through a stdout line protocol.

## Stdout Protocol

Every line is `[tag] payload` or `[tag]` (no payload). Lines without a recognized tag are logged as-is (this captures tracebacks from unhandled exceptions).

| Tag | When | Launcher routing |
|-----|------|-----------------|
| `[init]` | During startup (device scan, connection, config) | `_log(tag, payload)` |
| `[waiting]` | Init done, polling for first data | `_log` + `on_waiting`, panel shows "Waiting for data..." |
| `[ready]` | After first successful read/publish | Fires `on_ready`, logged |
| `[data]` | Each measurement cycle | Parsed as JSON, updates panel UI, **not logged** |
| `[error]` | Non-fatal errors (write failures, sensor glitches) | `_log(tag, "ERROR: " + payload)` |
| (untagged) | Tracebacks, unexpected output | `_log(tag, line)` |

Example session (fast startup, e.g. Thorlabs):
```
[init] Scanning USB devices...
[init] Found TSP01B on USB0::0x1313::0x8099
[init] Connected. Starting readings.
[init] InfluxDB: https://metrics.aaronsharpe.science org=dgg bucket=023_toploader
[init] First reading: 23.4 C, 42.1%
[ready]
[data] {"_summary": "23.4C — Oh so chilly!", "temp": "23.4 C", "humidity": "42.1%"}
[data] {"_summary": "23.5C — Oh so chilly!", "temp": "23.5 C", "humidity": "42.0%"}
[error] InfluxDB write failed: 401 Unauthorized
[data] {"_summary": "23.5C — Oh so chilly!", "temp": "23.5 C", "humidity": "42.0%"}
```

Example session (slow startup with waiting, e.g. LC scraper):
```
[init] LC Scraper FP
[init] Logs folder: C:\LC Data\Data
[init] InfluxDB: https://metrics.aaronsharpe.science org=dgg bucket=023_toploader
[init] Resuming from 2026-03-02 18:30:00+00:00
[init] Tailing logFP__20260228.dat
[waiting]
[ready]
[data] {"P1": "1.2 mbar", "Pc": "0.5 mbar", ...}
```

Example session (waiting timeout):
```
[init] LC Scraper FP
...
[waiting]
[error] Timed out waiting for data (10s)
```

`[waiting]` is optional — workers that get data quickly during init (e.g. Thorlabs) can skip it and go straight to `[ready]`. Workers that poll for data (e.g. LC scraper) should emit `[waiting]` after init and handle their own timeout, exiting with a non-zero code if data doesn't arrive.

Workers should wrap startup in try/except and emit `[error]` before re-raising, so the launcher log gets a clean summary alongside the traceback.

## Data Line Format

`[data]` payload is JSON with string values that include units:

```json
{"_summary": "23.4C — Oh so chilly!", "temp": "23.4 C", "humidity": "42.1%"}
```

String values with units allow the launcher panel to display them generically without knowing the schema per worker.

### `_summary` (optional)

If the JSON contains a `_summary` key, its value is shown inline on the status row (e.g. `Status: Running — 23.4C — Oh so chilly!`). It is excluded from the collapsible data detail. Use it for a short human-readable headline — one metric plus context, not a dump of all values.

Keys prefixed with `_` are reserved for metadata and stripped from the detail display.

## ManagedProcess Integration

Two start modes:

### `start()` — poll-based (Jupyter)
Launches with stdout suppressed. Background thread polls a `ready_check()` function until truthy. Used when readiness is detected externally (e.g., Jupyter server file).

### `start_with_output()` — stdout protocol (workers)
Launches with stdout captured (stderr merged via `STDOUT`). Background reader thread parses `[tag]` lines and routes them. Five callbacks:

- `on_waiting()` — `[waiting]` received, init done but no data yet
- `on_ready()` — `[ready]` received, process is live
- `on_failed(rc)` — process exited before `[ready]`
- `on_died(rc)` — process exited after `[ready]` unexpectedly
- `on_data(payload)` — `[data]` JSON string for panel display

Both modes:
- Use `_NO_WINDOW` creationflags on Windows (no console popup)
- Support `stop()` which kills the process tree and cancels pending callbacks
- Track `running` property via process poll
- Clear `_proc` on unexpected exit so the process can be restarted

## Status Panel & ComponentStatus

The launcher tracks aggregate health via `ComponentStatus` dataclass:

```python
@dataclass
class ComponentStatus:
    ok: bool = True
    message: str = ""
```

Three tiers:
- **Green "Ready"** — all health checks fresh, all workers running, Jupyter running
- **Yellow "Ready (Jupyter stopped)"** — everything OK except Jupyter isn't started
- **Red "Issues"** — any health check stale/missing, any worker not running/failed/died

Components tracked:
- `WorkerPanel.get_status()` — InfluxDB health per worker (each panel owns an `InfluxHealthPoller`)
- `_jupyter_status` — Jupyter process state
- `_ups_status` — UPS service state (Windows only)
- `_worker_status` dict — worker process states (keyed by display name)

A single `_tick()` timer (1s) calls `refresh_ui()` on each worker panel, then `_refresh_status()` to recompute the aggregate.

## WorkerPanel

`WorkerPanel` is a reusable class that encapsulates the full worker UI and lifecycle:
- Start/Stop buttons
- Status line (Stopped / Starting... / Waiting for data... / Running / Failed to start / Died with rc)
- Inline `_summary` on status row (e.g. `Running — 23.4C — Oh so chilly!`)
- Collapsible data detail (▶/▼ disclosure button, collapsed by default, one metric per line)
- InfluxDB health via own `InfluxHealthPoller` (daemon thread, no tkinter calls)
- `refresh_ui()` — called by launcher `_tick()`, updates InfluxDB age label from poller state
- `get_status()` — returns `ComponentStatus` for aggregate roll-up
- `destroy()` — stops process and poller

Workers are instantiated in `Launcher.__init__` via `self._workers` list. All handler
methods (`on_waiting`, `on_ready`, `on_failed`, `on_died`, `on_data`, `on_stopped`) live on `WorkerPanel`.

## Adding a New Worker

1. Create `src/workers/<name>.py` implementing the stdout protocol
2. Add a `WorkerPanel` entry to `self._workers` in `Launcher.__init__`:
   ```python
   WorkerPanel(
       self, title="My Worker", tag="my_worker",
       cmd=[sys.executable, "-m", "workers.my_worker"],
       health_key="my_worker", health_measurement="my_measurement",
       status_name="My Worker", config=cfg,
   ),
   ```
3. Add a `[health.my_worker]` section to `toploader.toml` with `metric` and `threshold`

## Current Workers

| Worker | Hardware | Measurement | Interval |
|--------|----------|-------------|----------|
| `thorlabs_thermo` | Thorlabs TSP01B (USB/VISA) | `thorlabs_thermo` | 60s |
| `lc_scraper --family FP` | LabVIEW FP.vi log files | `LC_scrapper` | 5s poll |
| `lc_scraper --family PT` | LabVIEW FP.vi log files | `LC_scrapper` | 5s poll |
| `avs_fridge` | AVS-47B via GPIB (persistent) | `AVS_bridge` | ~194s |
| `magnet` | AMI Model 430 via TCP/IP | `AVS_bridge` | 30s |
| `avs_probe` (planned) | AVS-47B via GPIB (persistent) | `AVS_bridge` | ~20s |

AVS workers use persistent GPIB connections (opened once at startup) and
`_wait_opc()` with configurable timeout to avoid hanging on device issues.
See `AVS_PLAN.md` for full design (probe param dropdowns, calibration system).

## File Layout

```
src/workers/
  __init__.py
  thorlabs_thermo.py    # TSP01B temp/humidity → InfluxDB
  lc_scraper.py         # LabVIEW log tailer → InfluxDB (FP + PT families)
  avs_calibration.py    # Calibration curves + sensor arrays (pure numpy, no I/O)
  avs_fridge.py         # Fridge AVS scan → InfluxDB (persistent GPIB)
  magnet.py             # AMI430 field read → InfluxDB (TCP/IP)
  avs_probe.py          # (planned) Probe AVS measure → InfluxDB
```
