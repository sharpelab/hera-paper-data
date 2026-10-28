# measurement-env

Measurement environment for Sharpe Lab toploader instruments. Manages Python
dependencies via [uv](https://docs.astral.sh/uv/) and vendors lab packages
in-tree under `lib/`.

## Setup

```bash
git clone https://github.com/sharpelab/measurement-env.git measurement_env
cd measurement_env
uv sync
```

Copy `<rig>.toml.example` to `<rig>.toml` and fill in the InfluxDB token.
Create a desktop shortcut to the rig's launcher in `.venv\Scripts\`
(`measurement-env-toploader.exe`, `measurement-env-vti.exe`,
`measurement-env-pink.exe`) and set its icon from `assets\measurement-env.ico`.

## Usage

The launcher GUI lives in the system tray (closing the window hides it; Quit
is in the tray menu) and owns the rig's InfluxDB workers, JupyterLab, and the
aggregate health panel. The toploader launcher also creates new runs (dated
measurement + analysis notebooks from `templates/`) under `~/measurements`.

## Vendored packages

Formerly git submodules, now vendored in-tree. The upstream repos remain the
public front; this tree is the version the lab actually runs.

| Path | Package | Vendored from | Description |
|------|---------|---------------|-------------|
| `lib/measureme` | `sweep` | `sharpelab/measureme@040d615` (`sharpelab` branch) | Measurement orchestration for QCoDeS |
| `lib/measurebot` | `measurebot` | `sharpelab/measurebot@0810c0e` (`main`) | Notifications via Discord, Slack, email |

## Dependencies

Core: `qcodes`, `qcodes-contrib-drivers`, `pyvisa`, `jupyterlab`, `numpy`,
`matplotlib`, `scipy`, `tqdm`

Instrument communication uses NI-VISA (installed separately on the measurement
PC).
