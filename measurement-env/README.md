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

Create a shortcut to `.venv\Scripts\measurement-env.exe` on the desktop.
Set the icon from `assets\measurement-env.ico`.

## Usage

Launch `measurement-env.exe` (or the desktop shortcut) to open the launcher GUI.
From there you can:
- **Create a new run** — select user, enter device name, and dated measurement +
  analysis notebooks are created from templates
- **Start/Stop JupyterLab** — rooted at `~/measurements`

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
