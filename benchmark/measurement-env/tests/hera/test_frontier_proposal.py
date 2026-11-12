from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

FRONTIER = Path(__file__).resolve().parents[2] / "hera/evaluations/frontier"
sys.path.insert(0, str(FRONTIER))

import grade  # noqa: E402
import proposal  # noqa: E402

EXPERIMENT = yaml.safe_load((FRONTIER / "experiments/qc0426-sdh-m41.yaml").read_text())
CONTRACT = EXPERIMENT.get("measurement_contract")
if not CONTRACT:
    pytest.skip("measurement_contract not in experiment YAML", allow_module_level=True)



def sdh_plan():
    return {
        "rationale": "Resolve SdH oscillations at the calibrated hole density.",
        "recipe": "sdh-spot-check",
        "ops": [
            {"op": "set", "param": "sr1.sensitivity", "value": 1e-5},
            {"op": "ramp", "param": "k_bg.volt", "setpoint": -1.763},
            {"op": "ramp", "param": "dc205_volt", "setpoint": -2.278},
            {"op": "sweep", "param": "magnet.mag",
             "setpoints": {"kind": "linspace", "start": 0.0, "stop": 4.0, "num": 501},
             "delay": 2.2},
        ],
    }


def test_generated_schema_avoids_cli_incompatible_draft_metadata():
    assert "$schema" not in proposal.schema_for(CONTRACT)


def test_user_proposed_sdh_plan_is_valid_and_passes_physics_grade():
    plan = sdh_plan()

    assert proposal.validate(plan, CONTRACT) is None
    result = grade.grade_proposal(plan, EXPERIMENT["calibration"], CONTRACT)

    assert result["status"] == "graded"
    assert result["ok"] is True
    assert result["kind"] == "spot"
    assert result["B_rows"] == 501
    assert result["B_range_T"] == [0.0, 4.0]
    assert result["n_cm2"][0] == pytest.approx(-5e12, rel=1e-3)


def test_unknown_parameter_is_rejected():
    plan = sdh_plan()
    plan["ops"][1]["param"] = "fake_gate.volt"

    assert "fake_gate.volt" in proposal.validate(plan, CONTRACT)


def test_parameter_specific_range_is_enforced():
    plan = sdh_plan()
    plan["ops"][1]["setpoint"] = -5.0

    assert proposal.validate(plan, CONTRACT) == "ops.1.setpoint: values must be within [-4.5, 4.5] V"


def test_real_sr830_sensitivity_enum_is_enforced():
    plan = sdh_plan()
    plan["ops"][0]["value"] = 3e-9

    assert "value must be one of" in proposal.validate(plan, CONTRACT)


def test_plan_requires_a_scan_operation():
    plan = sdh_plan()
    plan["ops"] = plan["ops"][:3]

    assert proposal.validate(plan, CONTRACT) == "ops: at least one sweep or megasweep operation is required"


def test_megasweep_represents_a_two_dimensional_scan():
    plan = {
        "rationale": "Map resistance against both gates.",
        "recipe": "gatemap",
        "ops": [{
            "op": "megasweep",
            "slow_param": "k_bg.volt",
            "slow_setpoints": {"kind": "linspace", "start": -4.0, "stop": 4.0, "num": 17},
            "fast_param": "dc205_volt",
            "fast_setpoints": {"kind": "linspace", "start": -6.0, "stop": 7.0, "num": 105},
            "slow_delay": 2.0,
            "fast_delay": 1.0,
        }],
    }

    assert proposal.validate(plan, CONTRACT) is None
    assert grade.grade_proposal(plan, EXPERIMENT["calibration"], CONTRACT)["status"] == "no_field_sweep"
