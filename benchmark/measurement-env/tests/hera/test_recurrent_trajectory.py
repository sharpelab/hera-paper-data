import json
import math
from pathlib import Path

import pytest
import yaml

from hera.recurrent_trajectory import (
    STATE_KEYS,
    build_turn_prompt,
    claude_command,
    extract_json,
    load_manifest,
    score_turn,
    validate_response,
)


def valid_response():
    return {
        "belief": {
            "aba": 0.05,
            "abc": 0.05,
            "aba_dominant_fl_fork": 0.8,
            "unresolved": 0.1,
        },
        "confidence": 0.7,
        "current_read": "ABA evidence with an unresolved F_L origin",
        "evidence_used": ["13+55 closes", "F_L remains"],
        "ambiguities": ["F_L may be breakdown or minority ABC"],
        "next_action": {"class": "density_fan", "rationale": "track branches"},
        "guards": {"clipping": True},
        "correction": {"retracted_prior": False, "what_changed": ""},
    }


def test_extract_json_accepts_fence_and_prefix():
    parsed = extract_json("note\n```json\n" + json.dumps(valid_response()) + "\n```")
    assert parsed["belief"]["aba_dominant_fl_fork"] == 0.8


def test_validate_response_rejects_bad_distribution():
    response = valid_response()
    response["belief"]["aba"] = 0.5
    with pytest.raises(ValueError, match="sum"):
        validate_response(response)


def test_build_prompt_only_includes_context_on_first_turn():
    step = {"label": "Map", "evidence": "historical map"}
    first = build_turn_prompt(step, 0, 2, "SECRET GENERIC CONTEXT")
    later = build_turn_prompt(step, 1, 2)
    assert "SECRET GENERIC CONTEXT" in first
    assert "SECRET GENERIC CONTEXT" not in later
    assert "2/2" in later


def test_claude_command_uses_persistent_session_and_disables_tools(tmp_path):
    first = claude_command(
        prompt="x", model="claude-haiku-4-5", session_id="uuid", first=True,
        mcp_config=tmp_path / "mcp.json",
    )
    resumed = claude_command(
        prompt="y", model="claude-haiku-4-5", session_id="uuid", first=False,
        mcp_config=tmp_path / "mcp.json",
    )
    assert "--session-id" in first and "--resume" not in first
    assert "--resume" in resumed and "--session-id" not in resumed
    assert first[first.index("--tools") + 1] == ""


def test_score_turn_uses_proper_loss_and_action_rubric():
    record = {"parsed": valid_response()}
    step = {
        "id": "corrected_spots",
        "target": {"aba": 0.05, "abc": 0.02, "aba_dominant_fl_fork": 0.88, "unresolved": 0.05},
        "acceptable_actions": ["density_fan"],
    }
    score = score_turn(record, step)
    assert score["action_quality"] is True
    assert score["fork_recognized"] is True
    assert score["unsupported_confidence"] is False
    expected = -sum(step["target"][key] * math.log(record["parsed"]["belief"][key]) for key in STATE_KEYS)
    assert score["cross_entropy"] == pytest.approx(expected)


def test_score_does_not_treat_excluded_breakdown_as_open_fork():
    response = valid_response()
    response["belief"] = {"aba": .8, "abc": .1, "aba_dominant_fl_fork": .05, "unresolved": .05}
    response["current_read"] = "Magnetic breakdown is excluded; this resolves the fork toward ABA."
    response["ambiguities"] = []
    response["correction"] = {"retracted_prior": False, "what_changed": "No revision."}
    step = {
        "id": "ladder_v1",
        "target": {"aba": .08, "abc": .02, "aba_dominant_fl_fork": .88, "unresolved": .02},
        "acceptable_actions": ["audit_or_refit"],
    }
    score = score_turn({"parsed": response}, step)
    assert score["fork_recognized"] is False
    assert score["correction_recognized"] is False


def test_load_manifest_rejects_non_normalized_target(tmp_path):
    manifest = {
        "version": 1,
        "states": list(STATE_KEYS),
        "steps": [{"id": "x", "target": {key: 0.1 for key in STATE_KEYS}}],
    }
    path = tmp_path / "manifest.yaml"
    path.write_text(yaml.safe_dump(manifest))
    with pytest.raises(ValueError, match="target"):
        load_manifest(path)
