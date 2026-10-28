import math

import pytest

from hera.measurement_classifier import (
    CLASSIFIER_VERSION,
    MeasurementType,
    classify_tool_call,
    extract_measurement_parameters,
    summarize_tool_calls,
)


def classify(callable_name="s.sweep", axes=None, rationale=""):
    return classify_tool_call({
        "callable": callable_name,
        "axes": axes or [],
        "kwargs": {},
        "rationale": rationale,
    })


def test_classifies_one_dimensional_field_sweep():
    result = classify(axes=[{"name": "magnet.field", "start": 0, "stop": 8, "points": 161}])
    assert result.classifier_version == CLASSIFIER_VERSION
    assert result.measurement_type == MeasurementType.FIELD_SWEEP_1D.value
    assert result.swept_variables == ("B",)


@pytest.mark.parametrize("density_name", [
    "n_line_D0",
    "carrier density (D~0 line)",
    "paired_gates_n_line",
])
def test_classifies_landau_fan_with_density_aliases(density_name):
    result = classify(
        "s.multimegasweep",
        axes=[{"name": "mag.field"}, {"name": density_name}],
    )
    assert result.measurement_type == MeasurementType.LANDAU_FAN_2D.value
    assert result.swept_variables == ("B", "n")


def test_classifies_singular_axes_with_param_aliases():
    result = classify_tool_call({
        "callable": "s.multimegasweep",
        "slow_axis": {"param": "magnet.field"},
        "fast_axes": {"params": ["k_tg.volt", "k_bg.volt"], "n_range": [-3, -0.5]},
    })
    assert result.measurement_type == MeasurementType.LANDAU_FAN_2D.value
    assert result.swept_variables == ("B", "n")


def test_classifies_split_slow_and_fast_axes_schema():
    result = classify_tool_call({
        "callable": "s.multimegasweep",
        "slow_axes": [{"name": "magnet.mag"}],
        "fast_axes": [{
            "parameters": ["k_tg", "k_bg"],
            "n_range_e12_cm2": [1.0, 10.0],
            "D_value": 0.0,
        }],
    })
    assert result.measurement_type == MeasurementType.LANDAU_FAN_2D.value
    assert result.swept_variables == ("B", "n")


def test_classifies_nested_axis_groups_as_landau_fan():
    proposal = {
        "callable": "s.multimegasweep",
        "axes": [
            [{"name": "mag.field", "start": 0.5, "stop": 3.0, "points": 101}],
            [{"name": "k_tg.volt", "points": 151},
             {"name": "k_bg.volt", "points": 151}],
        ],
    }
    result = classify_tool_call(proposal)
    params = extract_measurement_parameters(proposal)
    assert result.measurement_type == MeasurementType.LANDAU_FAN_2D.value
    assert result.swept_variables == ("B", "V_tg", "V_bg")
    assert params["field_points"] == 101.0


def test_classifies_landau_fan_from_parameter_and_parameters_schema():
    result = classify(
        "s.multimegasweep",
        axes=[
            {"parameter": "magnet.mag", "points": 141},
            {
                "parameters": ["dc205_volt", "k_bg.volt"],
                "n_window_e12_cm2": [0.5, 6.0],
                "D_fixed_V_nm": 0.0,
            },
        ],
    )
    assert result.measurement_type == MeasurementType.LANDAU_FAN_2D.value
    assert result.swept_variables == ("B", "n")
    assert result.raw_axis_labels == ("magnet.mag", "dc205_volt", "k_bg.volt")


def test_classifies_landau_fan_with_qc0426_dc205_gate_axis():
    result = classify(
        "s.megasweep",
        axes=[{"name": "dc205_volt"}, {"name": "magnet.mag"}],
        rationale="Landau fan at fixed D=0",
    )
    assert result.measurement_type == MeasurementType.LANDAU_FAN_2D.value
    assert result.swept_variables == ("B", "V_tg")


def test_classifies_gate_map_from_independent_gate_axes():
    result = classify(
        "s.megasweep",
        axes=[{"name": "k_tg.volt"}, {"name": "k_bg.volt"}],
    )
    assert result.measurement_type == MeasurementType.GATE_MAP.value
    assert result.swept_variables == ("V_tg", "V_bg")


def test_classifies_explicit_dc_bias_spectroscopy_before_field_rule():
    result = classify(
        "s.megasweep",
        axes=[{"name": "DC_bias"}, {"name": "mag.field"}],
    )
    assert result.measurement_type == MeasurementType.BIAS_SPECTROSCOPY.value
    assert result.swept_variables == ("B", "I_dc")


def test_disambiguates_dc205_1_using_strong_bias_intent():
    result = classify(
        "s.sweep",
        axes=[{"name": "dc205_1.volt"}],
        rationale="Bias spectroscopy dV/dI vs I_dc to extract critical current",
    )
    assert result.measurement_type == MeasurementType.BIAS_SPECTROSCOPY.value
    assert result.swept_variables == ("I_dc",)
    assert "intent:strong-bias-spectroscopy" in result.evidence


def test_does_not_guess_ambiguous_numbered_dc205_without_intent():
    result = classify("s.sweep", axes=[{"name": "dc205_1.volt"}])
    assert result.measurement_type == MeasurementType.OTHER_UNCLASSIFIABLE.value
    assert result.swept_variables == ()


@pytest.mark.parametrize("callable_name,axes", [
    ("s.temperature_ladder", []),
    ("s.megasweep", [{"name": "heater.sample_setpoint"}]),
    ("s.temperature_dependence", [{"name": "T_sample"}, {"name": "magnet.field"}]),
])
def test_classifies_temperature_dependence(callable_name, axes):
    result = classify(callable_name, axes=axes)
    assert result.measurement_type == MeasurementType.TEMPERATURE_DEPENDENCE.value
    assert "T" in result.swept_variables


def test_landau_fan_callable_is_auditable_fallback():
    result = classify("s.landau_fan", axes=[])
    assert result.measurement_type == MeasurementType.LANDAU_FAN_2D.value
    assert result.swept_variables == ("B", "n")
    assert "rule:landau-fan-callable" in result.evidence


def test_unknown_call_remains_unclassifiable():
    result = classify("s.unknown", axes=[{"name": "mystery_axis"}])
    assert result.measurement_type == MeasurementType.OTHER_UNCLASSIFIABLE.value
    assert result.raw_axis_labels == ("mystery_axis",)


def test_extracts_field_span_points_and_sampling():
    result = extract_measurement_parameters({
        "callable": "s.sweep",
        "axes": [{"name": "magnet.field", "start": 1.0, "stop": 4.0, "points": 141,
                  "spacing": "uniform in 1/B"}],
        "delays": {"fast": 1.0, "slow": 2.0},
    })
    assert result["field_start"] == 1.0
    assert result["field_stop"] == 4.0
    assert result["field_span"] == 3.0
    assert result["field_points"] == 141.0
    assert result["field_step"] == pytest.approx(3.0 / 140.0)
    assert 1.0 / result["field_step"] == pytest.approx(140.0 / 3.0)
    assert result["field_sampling"] == "inverse_B"
    assert result["fast_delay"] == 1.0
    assert result["slow_delay"] == 2.0


def test_extracts_top_level_field_spacing():
    result = extract_measurement_parameters({
        "callable": "s.sweep",
        "axes": [{"name": "magnet.field", "start": 1.0, "stop": 4.0, "points": 141}],
        "field_spacing": "uniform-1/B",
    })
    assert result["field_sampling"] == "inverse_B"


def test_extracts_density_from_n_range_schema():
    result = extract_measurement_parameters({
        "callable": "s.multimegasweep",
        "axes": [
            {"name": "magnet.mag", "start": 0.0, "stop": 8.0, "points": 161},
            {"parameters": ["k_tg", "k_bg"], "n_range_e12_cm2": [1.0, 10.0], "n_points": 100},
        ],
    })
    assert result["density_start"] == 1.0
    assert result["density_stop"] == 10.0
    assert result["density_span"] == 9.0
    assert result["density_points"] == 100.0


def test_extracts_density_from_generic_range_schema():
    result = extract_measurement_parameters({
        "callable": "s.multimegasweep",
        "axes": [{"name": "density n", "range": [-4.0, 4.0], "points": 9}],
    })
    assert result["density_span"] == 8.0
    assert result["density_step"] == 1.0


def test_extract_handles_missing_axes_gracefully():
    result = extract_measurement_parameters({"callable": "s.sweep", "axes": []})
    assert result == {"fast_delay": None, "slow_delay": None, "settle_delay": None}


def test_extracts_nested_temperature_ladder_and_repeated_field_sweep():
    proposal = {
        "callable": "temperature_dependence_ladder",
        "temperature_ladder": {
            "heater_setpoints": [0.0, 1.5, 3.0, 4.5],
            "thermalization_time_s": 600,
        },
        "repeated_sweep": {
            "axis": "magnet.field", "start": 10.0, "stop": 2.0, "points": 401,
        },
        "measurement_config": {"dwell": 0.7},
    }
    result = extract_measurement_parameters(proposal)
    classification = classify_tool_call(proposal)
    assert classification.measurement_type == MeasurementType.TEMPERATURE_DEPENDENCE.value
    assert result["field_step"] == pytest.approx(0.02)
    assert result["temperature_points"] == 4.0
    assert result["fast_delay"] == 0.7
    assert result["settle_delay"] == 600.0


def test_extracts_nested_field_and_temperature_values():
    result = extract_measurement_parameters({
        "callable": "s.temperature_ladder",
        "temperatures": [1.3, 2.0, 4.0, 8.0],
        "field": {"start": 0.5, "stop": 8.0, "points": 151},
        "heater": {"settle_minutes": 3},
    })
    assert result["temperature_points"] == 4.0
    assert result["temperature_span"] == pytest.approx(6.7)
    assert result["field_step"] == pytest.approx(0.05)
    assert result["settle_delay"] == 180.0


def test_extracts_bias_range_from_dc205_axis():
    result = extract_measurement_parameters({
        "callable": "s.sweep",
        "axes": [{"name": "dc205_1.volt", "start": -10.0, "stop": 10.0, "points": 101}],
        "rationale": "Bias spectroscopy dV/dI to extract critical current",
    })
    assert result["bias_span"] == 20.0
    assert result["bias_points"] == 101.0


def test_summary_reports_type_and_variable_entropy_in_bits():
    calls = [
        {"callable": "s.sweep", "axes": [{"name": "mag.field"}]},
        {"callable": "s.sweep", "axes": [{"name": "mag.field"}]},
        {
            "callable": "s.megasweep",
            "axes": [{"name": "k_tg.volt"}, {"name": "k_bg.volt"}],
        },
    ]
    summary = summarize_tool_calls(calls)
    expected = -(2 / 3 * math.log2(2 / 3) + 1 / 3 * math.log2(1 / 3))
    assert summary["n"] == 3
    assert summary["measurement_type_counts"] == {
        "1D_FIELD_SWEEP": 2,
        "GATE_MAP": 1,
    }
    assert summary["measurement_type_entropy_bits"] == pytest.approx(expected)
    assert summary["swept_variable_set_entropy_bits"] == pytest.approx(expected)
    assert len(summary["classifications"]) == 3
