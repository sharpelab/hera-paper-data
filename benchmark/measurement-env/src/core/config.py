"""Typed configuration for the rig launchers.

Shared schema for every rig: a `BaseConfig` carries the rig-agnostic sections
(`[influxdb]`, `[health]`); per-rig configs extend it with their `[hardware]`
(and, for the toploader, an optional `[hera]`). One loader validates the common
sections; each rig supplies only its hardware dataclass + toml path.

- Shared:    InfluxConfig, HealthEntry, BaseHardware, BaseConfig
- Toploader: ToploaderHardware, ToploaderConfig  (load_config / toploader.toml)
- VTI:       VtiHardware, VtiConfig              (load_vti_config / vti.toml)
- Pink:      PinkHardware, PinkConfig            (load_pink_config / pink.toml)
"""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from core import REPO_DIR

TOPLOADER_PATH = REPO_DIR / "toploader.toml"
VTI_PATH = REPO_DIR / "vti.toml"
PINK_PATH = REPO_DIR / "pink.toml"


class ConfigError(Exception):
    """Raised when required config keys are missing or invalid."""


# --- Shared field dataclasses --------------------------------------------


@dataclass(frozen=True)
class InfluxConfig:
    url: str
    token: str
    org: str
    bucket: str


@dataclass(frozen=True)
class HealthEntry:
    """One worker's InfluxDB freshness guard.

    A worker owning several instruments lists one metric per instrument: the
    panel is healthy only while every one of them is being written.
    """
    metrics: tuple[str, ...]
    threshold: int

    @classmethod
    def from_toml(cls, raw: dict) -> "HealthEntry":
        """Build from a [health.*] table: `metrics = ["a", "b"]`, `threshold = N`."""
        return cls(metrics=tuple(raw["metrics"]), threshold=raw["threshold"])


@dataclass(frozen=True)
class BaseHardware:
    """Base for per-rig hardware dataclasses (each adds its address fields)."""


@dataclass(frozen=True)
class BaseConfig:
    """Rig-agnostic sections shared by every rig config."""
    influxdb: InfluxConfig
    health: dict[str, HealthEntry]


# --- Toploader -----------------------------------------------------------


@dataclass(frozen=True)
class HeraConfig:
    gemini_api_key: str
    classifier_model: str


@dataclass(frozen=True)
class ToploaderHardware(BaseHardware):
    avs_fridge_gpib: str
    avs_probe_gpib: str
    ami430_addr: str
    lc_logs_folder: str
    temperature_log_dir: str
    # Leiden QCS heater current source (via MCC USB-3101 DAQ). Optional so
    # existing configs load; the qcs_heater worker refuses to start without
    # a board number. Currents in µA, keyed by channel name (3K/Still/MC).
    qcs_board_num: int = -1
    qcs_max_ua: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class ToploaderConfig(BaseConfig):
    hardware: ToploaderHardware
    hera: Optional[HeraConfig] = None


# --- VTI -----------------------------------------------------------------


@dataclass(frozen=True)
class VtiHardware(BaseHardware):
    lakeshore_gpib: str
    temperature_log_dir: str
    ami1700_addr: str
    terranova_addr: str
    lakeshore218_gpib: str
    fastbi_host: str


@dataclass(frozen=True)
class VtiConfig(BaseConfig):
    hardware: VtiHardware


# --- Pink ----------------------------------------------------------------


@dataclass(frozen=True)
class PinkHardware(BaseHardware):
    lc_logs_folder: str
    ami430_addr: str


@dataclass(frozen=True)
class PinkConfig(BaseConfig):
    hardware: PinkHardware


# --- Loading -------------------------------------------------------------


_INFLUX_KEYS = ("url", "token", "org", "bucket")
_TOPLOADER_HW_KEYS = (
    "avs_fridge_gpib", "avs_probe_gpib", "ami430_addr",
    "lc_logs_folder", "temperature_log_dir",
)
_VTI_HW_KEYS = (
    "lakeshore_gpib", "temperature_log_dir",
    "ami1700_addr", "terranova_addr", "lakeshore218_gpib", "fastbi_host",
)
_PINK_HW_KEYS = ("lc_logs_folder", "ami430_addr")


def _load_raw(path: Path | None, default: Path) -> dict:
    if path is None:
        path = default
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}")


def _validate_common(raw: dict, hardware_keys: tuple[str, ...]) -> None:
    """Validate the [influxdb]/[hardware]/[health] sections shared by all rigs."""
    missing: list[str] = []

    for section in ("influxdb", "hardware", "health"):
        if section not in raw:
            missing.append(f"[{section}]")
    if missing:
        raise ConfigError(f"Missing required sections: {', '.join(missing)}")

    for key in _INFLUX_KEYS:
        if not raw["influxdb"].get(key):
            missing.append(f"influxdb.{key}")

    for key in hardware_keys:
        if not raw["hardware"].get(key):
            missing.append(f"hardware.{key}")

    for name, entry in raw["health"].items():
        if not isinstance(entry, dict):
            missing.append(f"health.{name} (must be a table)")
            continue
        if "threshold" not in entry:
            missing.append(f"health.{name}.threshold")
        # A bare string would tuple() into one-character metrics.
        if not isinstance(entry.get("metrics"), list) or not entry["metrics"]:
            missing.append(f"health.{name}.metrics (must be a non-empty list)")

    if missing:
        raise ConfigError(f"Missing required config keys: {', '.join(missing)}")


def _common_kwargs(raw: dict) -> dict:
    """Build the shared BaseConfig fields from validated raw config."""
    return dict(
        influxdb=InfluxConfig(**raw["influxdb"]),
        health={k: HealthEntry.from_toml(v) for k, v in raw["health"].items()},
    )


def load_config(path: Path | None = None) -> ToploaderConfig:
    """Load and validate toploader.toml. Raises ConfigError on problems."""
    raw = _load_raw(path, TOPLOADER_PATH)
    _validate_common(raw, _TOPLOADER_HW_KEYS)

    hera_raw = raw.get("hera") or {}
    hera = None
    if hera_raw.get("gemini_api_key"):
        hera = HeraConfig(
            gemini_api_key=hera_raw["gemini_api_key"],
            classifier_model=hera_raw.get("classifier_model", "gemini-2.5-flash"),
        )

    return ToploaderConfig(
        **_common_kwargs(raw),
        hardware=ToploaderHardware(**raw["hardware"]),
        hera=hera,
    )


def load_vti_config(path: Path | None = None) -> VtiConfig:
    """Load and validate vti.toml. Raises ConfigError on problems."""
    raw = _load_raw(path, VTI_PATH)
    _validate_common(raw, _VTI_HW_KEYS)
    return VtiConfig(
        **_common_kwargs(raw),
        hardware=VtiHardware(**raw["hardware"]),
    )


def load_pink_config(path: Path | None = None) -> PinkConfig:
    """Load and validate pink.toml. Raises ConfigError on problems."""
    raw = _load_raw(path, PINK_PATH)
    _validate_common(raw, _PINK_HW_KEYS)
    return PinkConfig(
        **_common_kwargs(raw),
        hardware=PinkHardware(**raw["hardware"]),
    )
