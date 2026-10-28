from hera.context_ablation import score_final_record, score_tool_record


def test_tool_rubric_scores_both_acquisition_guards():
    record = {
        "parsed": {
            "callable": "s.multimegasweep",
            "axes": [
                {"name": "magnet.field", "start": 0.4, "stop": 4, "points": 451},
                {"name": "n at D=0 via co-swept gates", "start": 1, "stop": 4.5, "points": 61},
            ],
            "delays": {"fast": 1.2, "slow": 3.0},
            "rationale": "Size sensitivity for the low-n high-B worst corner to prevent clipping; sample uniformly in 1/B.",
        }
    }
    score = score_tool_record(record, "")
    assert score["fan_scope"] is True
    assert score["clipping_guard"] is True
    assert score["settling_guard"] is True
    # Prose-only 1/B language is design intent, not the preregistered
    # executable outcome (audit 2026-08-29): primary `inverse_b` stays False.
    assert score["inverse_b"] is False
    assert score["inverse_b_executable"] is False
    assert score["inverse_b_intent"] is True
    assert score["inverse_b_mention"] is True
    assert score["primary_guard_score"] == 1.0


def test_tool_rubric_inverse_b_requires_executable_geometry():
    record = {
        "parsed": {
            "callable": "s.megasweep",
            "axes": [
                {"name": "magnet.field", "start": 0.8, "stop": 4, "points": 180,
                 "spacing": "uniform in 1/B"},
            ],
            "delays": {"fast": 1.2},
            "rationale": "Fourier transform in the field.",
        }
    }
    score = score_tool_record(record, "")
    assert score["inverse_b"] is True
    assert score["inverse_b_executable"] is True
    assert score["inverse_b_intent"] is True
    assert score["inverse_b_mention"] is True


def test_tool_rubric_accepts_density_grid_encoded_in_kwargs():
    record = {
        "parsed": {
            "callable": "s.multimegasweep",
            "axes": [{"name": "mag.field", "start": 0, "stop": 4, "points": 81}],
            "kwargs": {"fast_params": ["k_tg.volt", "k_bg.volt"], "carrier_density_points": 101},
            "delays": {"fast": 0.8},
        }
    }
    assert score_tool_record(record, "")["fan_scope"] is True


def test_tool_rubric_does_not_credit_claimed_guard_with_bad_fixed_range():
    record = {
        "parsed": {
            "callable": "s.multimegasweep",
            "axes": [
                {"name": "magnet.field", "points": 81},
                {"name": "D=0 density", "n_points": 50},
            ],
            "delays": {"fast": .9},
            "kwargs": {"sr1_sensitivity": 1e-5, "sr2_sensitivity": 1e-5},
            "rationale": "High-field-sized sensitivities sr1/sr2=1e-5 avoid clipping.",
        }
    }
    score = score_tool_record(record, "")
    assert score["fan_scope"] is True
    assert score["clipping_guard"] is False


def test_tool_rubric_rejects_fixed_density_field_sweep_as_fan():
    record = {
        "parsed": {
            "callable": "s.megasweep",
            "axes": [
                {"name": "magnet.field", "start": 0, "stop": 8, "points": 401},
                {"name": "dc205_volt", "start": 2.4, "stop": 2.4, "points": 1},
            ],
            "delays": {"fast": 0.05},
        }
    }
    assert score_tool_record(record, "")["fan_scope"] is False


def test_tool_rubric_rejects_inherited_under_ranged_fast_design():
    record = {
        "parsed": {
            "callable": "s.multimegasweep",
            "axes": [
                {"name": "magnet.field", "start": 0.4, "stop": 4, "points": 251},
                {"name": "gate density n", "start": 1, "stop": 4.5, "points": 41},
            ],
            "delays": {"fast": 0.8},
            "rationale": "Reuse the spot-check settings.",
        }
    }
    score = score_tool_record(record, "")
    assert score["fan_scope"] is True
    assert score["clipping_guard"] is False
    assert score["settling_guard"] is False
    assert score["primary_guard_score"] == 0.0


def test_final_rubric_rewards_fork_aware_analysis():
    record = {
        "parsed": {
            "verdict": "UNDERDETERMINED",
            "confidence": "MEDIUM",
            "summary": "ML and BL form a two-pocket partition, but the F_L tone is ambiguous between an ABC domain and magnetic breakdown.",
            "evidence": ["8 T and 44 T sum to F_L near 52 T", "Use an LK mass split or B-window split next"],
        }
    }
    score = score_final_record(record, "")
    assert score["aba_pair_recognized"] is True
    assert score["f_l_tone_ambiguity"] is True
    assert score["calibrated_conclusion"] is True
    assert score["deciding_followup"] is True
    assert score["evidence_specificity"] is True
    assert score["primary_analysis_score"] == 1.0


def test_final_rubric_does_not_reward_bare_confident_call():
    record = {
        "parsed": {
            "verdict": "ABA",
            "confidence": "HIGH",
            "summary": "The device is unambiguously ABA.",
            "evidence": ["oscillations are present"],
        }
    }
    score = score_final_record(record, "")
    assert score["aba_pair_recognized"] is False
    assert score["f_l_tone_ambiguity"] is False
    assert score["calibrated_conclusion"] is False
    assert score["deciding_followup"] is False
    assert score["primary_analysis_score"] == 0.0
