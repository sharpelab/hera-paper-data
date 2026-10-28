# jupyter-config

Repo-side JupyterLab configuration, layered onto the deployed servers via
`JUPYTER_CONFIG_PATH` rather than written into the env. Because it lives in
the repo (not under `.venv`), it **survives `uv sync` / env rebuilds** and
arrives through the normal deploy path: `git pull` updates it, and the
launch command points `JUPYTER_CONFIG_PATH` at this directory.

## `labconfig/default_setting_overrides.json`

JupyterLab setting-default overrides. `jupyterlab_server` reads
`default_setting_overrides.json` from a `labconfig/` directory on the
Jupyter config path (`jupyter_core.paths.jupyter_config_path()`), and
`JUPYTER_CONFIG_PATH` prepends to that path. Keys are
`<plugin-id>` → `<settings>`.

Currently sets:

- `@jupyterlab/notebook-extension:tracker` → `recordTiming: true` — makes
  executed cells carry kernel start/end times under
  `cell.metadata.execution` (`iopub.execute_input`, `shell.execute_reply`,
  ISO-8601 UTC). This is the cell-execution half of session timing
  reconstruction (the cell-landing half is `metadata.hera.*_at`, stamped by
  `nb-collab`). No browser setting required — it's a server-served default.

## Wiring

Deploy paths that set `JUPYTER_CONFIG_PATH` to this directory:

- **VTI (Qt launcher GUI):** the shared Jupyter panel
  (`src/gui/qt/jupyter_panel.py`) injects it into the JupyterLab child's
  environment. (Until the Qt launcher deploys, the rig-side interim is the
  section-4 launch line in `hera/docs/vti/preflight-runbook.md`, which
  exports `JUPYTER_CONFIG_PATH="$HOME/measurement_env/jupyter-config"`.)
- **Toploader (launcher GUI):** `src/gui/toploader_launcher.py` injects it into the
  JupyterLab child's environment.

Verify a running server picked it up. The override raises the served
*default*, so read it from the schema — the `settings` field holds only
user-modified values and stays empty:

```bash
curl -s "http://localhost:<port>/lab/api/settings/@jupyterlab/notebook-extension:tracker" \
  | python -c "import json,sys; print(json.load(sys.stdin)['schema']['properties']['recordTiming']['default'])"
```
