"""Lab-specific constants for Sharpe Lab measurement setups."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FridgeConfig:
    """Constants for a specific fridge/cryostat setup."""

    name: str
    coil_constant: float  # T/A
    temp_logfiles: dict[str, str] = field(default_factory=dict)
    # Candidate logfiles per sensor (sensor name -> list of paths). The
    # readout (temperature_from_logfiles) picks whichever is freshest, so a
    # dead worker / wrong probe is auto-skipped instead of read stale.
    temp_logfile_candidates: dict[str, list[str]] = field(default_factory=dict)


TOPLOADER = FridgeConfig(
    name="toploader",
    coil_constant=0.116783,
    temp_logfiles={
        "T_probe": r"C:\Users\toploader\temperature_logs\Probe1_MixingCh_low.txt",
        "T_fridge": r"C:\Users\toploader\temperature_logs\Fridge_MixingCh_low.txt",
        "T_magnet": r"C:\Users\toploader\temperature_logs\Fridge_Magnet.txt",
    },
    temp_logfile_candidates={
        # Two probes are racked (1=straight, 2=rotator); only the installed
        # one's logfile advances. Read both, use the live one.
        "T_probe": [
            r"C:\Users\toploader\temperature_logs\Probe1_MixingCh_low.txt",
            r"C:\Users\toploader\temperature_logs\Probe2_MixingCh_low.txt",
        ],
        "T_fridge": [r"C:\Users\toploader\temperature_logs\Fridge_MixingCh_low.txt"],
        "T_magnet": [r"C:\Users\toploader\temperature_logs\Fridge_Magnet.txt"],
    },
)

VTI = FridgeConfig(
    name="vti",
    coil_constant=1 / 7.3,
    temp_logfiles={
        "T_sample": r"C:\Users\DGG\temperature_logs\VTI_sample.txt",
        "T_vaporizer": r"C:\Users\DGG\temperature_logs\VTI_vaporizer.txt",
    },
    temp_logfile_candidates={
        # LS335 input A (sample-mount Cernox) and B (vaporizer Cernox), each
        # written by the lakeshore worker. Single candidate per sensor — the
        # list form still drives the staleness / dead-worker warning.
        "T_sample": [r"C:\Users\DGG\temperature_logs\VTI_sample.txt"],
        "T_vaporizer": [r"C:\Users\DGG\temperature_logs\VTI_vaporizer.txt"],
    },
)
