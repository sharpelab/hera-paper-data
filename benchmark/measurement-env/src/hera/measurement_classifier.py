"""Deterministic scientific classification of HERA tool-call proposals.

The classifier maps heterogeneous machine-level call schemas onto two stable
analysis outputs:

* a scientific measurement type; and
* a canonical swept-variable set.

It deliberately does not judge whether a proposal is scientifically good.
Unknown or ambiguous calls remain auditable as OTHER_UNCLASSIFIABLE.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Iterable, Mapping

CLASSIFIER_VERSION = "1.0.1"


class MeasurementType(str, Enum):
    FIELD_SWEEP_1D = "1D_FIELD_SWEEP"
    LANDAU_FAN_2D = "2D_LANDAU_FAN"
    GATE_MAP = "GATE_MAP"
    BIAS_SPECTROSCOPY = "BIAS_SPECTROSCOPY"
    TEMPERATURE_DEPENDENCE = "TEMPERATURE_DEPENDENCE"
    OTHER_UNCLASSIFIABLE = "OTHER_UNCLASSIFIABLE"


_VARIABLE_ORDER = ("B", "n", "D", "V_tg", "V_bg", "I_dc", "T")
_FIELD_RE = re.compile(
    r"(?:^|[^a-z0-9])b(?:[^a-z0-9]|$)|magnet|mag(?:netic)?[._ -]?field|"
    r"mag[._ -]|field[ _-]?(?:t|axis|sweep|slow)",
)
_DENSITY_RE = re.compile(
    r"carrier.?density|density|(?:^|[^a-z0-9])n(?:[^a-z0-9]|$)|n[_ -]?(?:line|window|range|points)|"
    r"d0[_ -]?line|d\s*(?:~|≈|=)\s*0|paired.?gates",
)
_DISPLACEMENT_RE = re.compile(
    r"displacement|(?:^|[^a-z0-9])d(?:[^a-z0-9]|$)|d[_ -]?(?:line|axis|sweep)",
)
_TG_RE = re.compile(r"k[_ -]?(?:2400[_ -]?)?tg|v[_ -]?tg|top.?gate")
_BG_RE = re.compile(r"k[_ -]?(?:2400[_ -]?)?bg|v[_ -]?bg|back|bottom.?gate")
_TEMPERATURE_RE = re.compile(r"temperature|t[_ -]?sample|heater|therm")
_EXPLICIT_BIAS_AXIS_RE = re.compile(
    r"dc[_ -]?bias|i[_ -]?dc|idc|bias[_ -]?(?:current|axis|sweep)|current[_ -]?bias",
)
_STRONG_BIAS_INTENT_RE = re.compile(
    r"bias.?spectroscop|d\s*v\s*/\s*d\s*i|critical.?current|extract\s+i[_ ]?c|"
    r"switching.?current",
)


@dataclass(frozen=True)
class MeasurementClassification:
    classifier_version: str
    measurement_type: str
    swept_variables: tuple[str, ...]
    raw_callable: str
    raw_axis_labels: tuple[str, ...]
    evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        doc = asdict(self)
        doc["swept_variables"] = list(self.swept_variables)
        doc["raw_axis_labels"] = list(self.raw_axis_labels)
        doc["evidence"] = list(self.evidence)
        return doc


def _axis_fragments(axis: Mapping[str, Any]) -> list[str]:
    fragments: list[str] = []
    for key in ("name", "parameter", "param"):
        value = axis.get(key)
        if value is not None:
            fragments.append(str(value))
    for key in ("parameters", "params"):
        value = axis.get(key)
        if isinstance(value, (list, tuple)):
            fragments.extend(str(item) for item in value)
        elif value is not None:
            fragments.append(str(value))
    return fragments


def _ordered_variables(values: set[str]) -> tuple[str, ...]:
    known = [name for name in _VARIABLE_ORDER if name in values]
    unknown = sorted(values - set(_VARIABLE_ORDER))
    return tuple(known + unknown)


def _canonical_axis_variables(
    axis: Mapping[str, Any], *, strong_bias_intent: bool
) -> set[str]:
    fragments = _axis_fragments(axis)
    fragment_text = " ".join(fragments).lower()
    axis_text = json.dumps(axis, sort_keys=True, ensure_ascii=False).lower()
    variables: set[str] = set()

    if _FIELD_RE.search(fragment_text):
        variables.add("B")
    if _TEMPERATURE_RE.search(fragment_text):
        variables.add("T")

    explicit_bias = bool(_EXPLICIT_BIAS_AXIS_RE.search(fragment_text))
    hardware_bias = bool(re.search(r"dc205[_ -]?1(?:\.|$)", fragment_text))
    if explicit_bias or (hardware_bias and strong_bias_intent):
        variables.add("I_dc")

    # An axis described as a density line or paired D=0 gate trajectory is a
    # scientific density dimension, even when its physical parameters are two
    # gate voltages.
    density_semantic = bool(
        _DENSITY_RE.search(fragment_text)
        or re.search(r'"n_(?:window|range|points)', axis_text)
        or re.search(r'"d_fixed', axis_text)
    )
    if density_semantic:
        variables.add("n")
    else:
        if _TG_RE.search(fragment_text):
            variables.add("V_tg")
        if _BG_RE.search(fragment_text):
            variables.add("V_bg")
        # In the QC0426 rig, an unnumbered dc205 axis is the second gate
        # control. Numbered dc205_1 is treated as I_dc only with strong bias
        # evidence above; otherwise it remains unknown rather than guessed.
        if re.search(r"(?:^|[^a-z0-9])dc205(?:_volt|\.volt|$)", fragment_text):
            variables.add("V_tg")

    if _DISPLACEMENT_RE.search(fragment_text) and not density_semantic:
        variables.add("D")
    return variables


def _axis_mappings(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        return [value]
    if isinstance(value, (list, tuple)):
        return [axis for item in value for axis in _axis_mappings(item)]
    return []


def _proposal_axes(proposal: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    axes: list[Mapping[str, Any]] = []
    for key in ("axes", "slow_axes", "fast_axes"):
        axes.extend(_axis_mappings(proposal.get(key)))
    for key in ("axis", "slow_axis", "fast_axis"):
        value = proposal.get(key)
        if isinstance(value, Mapping):
            axes.append(value)

    # High-level helper envelopes observed in the retained replay corpus.
    # Convert them to the same axis representation without interpreting fixed
    # setpoints as swept variables.
    repeated = proposal.get("repeated_sweep")
    if isinstance(repeated, Mapping):
        axis = dict(repeated)
        if "name" not in axis and axis.get("axis") is not None:
            axis["name"] = axis["axis"]
        axes.append(axis)
    field = proposal.get("field")
    if isinstance(field, Mapping) and any(key in field for key in ("start", "stop", "points")):
        axes.append({"name": "magnet.field", **field})
    temperatures = proposal.get("temperatures")
    if isinstance(temperatures, (list, tuple)):
        axes.append({"name": "temperature", "values": temperatures, "unit": "K"})
    heater_values = proposal.get("heater_setpoints_V")
    if isinstance(heater_values, (list, tuple)):
        axes.append({"name": "heater.volt", "values": heater_values, "unit": "V"})
    ladder = proposal.get("temperature_ladder")
    if isinstance(ladder, Mapping) and isinstance(ladder.get("heater_setpoints"), (list, tuple)):
        axes.append({"name": "heater.volt", "values": ladder["heater_setpoints"], "unit": "V"})
    return axes


def classify_tool_call(parsed: Mapping[str, Any] | None) -> MeasurementClassification:
    """Classify one parsed HERA tool-call envelope deterministically."""
    proposal: Mapping[str, Any] = parsed if isinstance(parsed, Mapping) else {}
    raw_callable = str(proposal.get("callable") or "")
    callable_text = raw_callable.lower()
    rationale = str(proposal.get("rationale") or "")
    intent_text = " ".join(
        (
            callable_text,
            rationale.lower(),
            json.dumps(proposal.get("kwargs") or {}, sort_keys=True).lower(),
        )
    )
    strong_bias_intent = bool(_STRONG_BIAS_INTENT_RE.search(intent_text))

    axes = _proposal_axes(proposal)
    raw_axis_labels: list[str] = []
    variables: set[str] = set()
    for index, axis in enumerate(axes):
        fragments = _axis_fragments(axis)
        raw_axis_labels.extend(fragments or [f"<unnamed-axis-{index + 1}>"])
        variables.update(
            _canonical_axis_variables(axis, strong_bias_intent=strong_bias_intent)
        )

    # Callable fallbacks handle valid high-level helpers that omit explicit
    # axes while preserving axis-derived classification whenever possible.
    temperature_callable = "temperature" in callable_text or "heater" in callable_text
    landau_callable = "landau_fan" in callable_text or "landaufan" in callable_text
    if temperature_callable:
        variables.add("T")
    landau_inferred_axes = landau_callable and not variables
    if landau_inferred_axes:
        variables.update(("B", "n"))

    evidence: list[str] = []
    if "I_dc" in variables:
        measurement_type = MeasurementType.BIAS_SPECTROSCOPY
        evidence.append("rule:I_dc-axis")
    elif "T" in variables:
        measurement_type = MeasurementType.TEMPERATURE_DEPENDENCE
        evidence.append("rule:T-axis-or-temperature-callable")
    elif landau_inferred_axes:
        measurement_type = MeasurementType.LANDAU_FAN_2D
        evidence.append("rule:landau-fan-callable")
    elif "B" in variables and variables.intersection({"n", "D", "V_tg", "V_bg"}):
        measurement_type = MeasurementType.LANDAU_FAN_2D
        evidence.append("rule:B-plus-density-or-gate")
    elif landau_callable:
        measurement_type = MeasurementType.LANDAU_FAN_2D
        variables.update(("B", "n"))
        evidence.append("rule:landau-fan-callable")
    elif variables == {"B"}:
        measurement_type = MeasurementType.FIELD_SWEEP_1D
        evidence.append("rule:B-only")
    elif "V_tg" in variables and "V_bg" in variables and "B" not in variables:
        measurement_type = MeasurementType.GATE_MAP
        evidence.append("rule:independent-top-and-back-gates")
    else:
        measurement_type = MeasurementType.OTHER_UNCLASSIFIABLE
        evidence.append("rule:no-declared-type-match")

    evidence.append("variables:" + ",".join(_ordered_variables(variables)))
    if strong_bias_intent:
        evidence.append("intent:strong-bias-spectroscopy")
    return MeasurementClassification(
        classifier_version=CLASSIFIER_VERSION,
        measurement_type=measurement_type.value,
        swept_variables=_ordered_variables(variables),
        raw_callable=raw_callable,
        raw_axis_labels=tuple(raw_axis_labels),
        evidence=tuple(evidence),
    )


def shannon_entropy_bits(values: Iterable[str]) -> float:
    items = list(values)
    if not items:
        return 0.0
    counts = Counter(items)
    total = len(items)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def _to_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _pair_range(axis: Mapping[str, Any]) -> tuple[float | None, float | None]:
    start = _to_float(axis.get("start"))
    stop = _to_float(axis.get("stop"))
    if start is not None and stop is not None:
        return start, stop
    for key in ("n_range", "n_window", "n_range_e12_cm2", "n_range_cm_minus_2",
                "range", "values", "vectors"):
        value = axis.get(key)
        if isinstance(value, (list, tuple)) and len(value) >= 2:
            first, last = _to_float(value[0]), _to_float(value[-1])
            if first is not None and last is not None:
                return first, last
    for start_key, stop_key in (("n_start", "n_stop"), ("n_start_cm2", "n_stop_cm2"),
                                ("density_start", "density_stop"),
                                ("density_start_cm2", "density_stop_cm2"),
                                ("T_start", "T_end"), ("T_start", "T_stop")):
        start, stop = _to_float(axis.get(start_key)), _to_float(axis.get(stop_key))
        if start is not None and stop is not None:
            return start, stop
    return None, None


def _points(axis: Mapping[str, Any]) -> float | None:
    for key in ("points", "n_points", "density_points", "T_points", "count"):
        value = _to_float(axis.get(key))
        if value is not None:
            return value
    for key in ("values", "vectors"):
        value = axis.get(key)
        if isinstance(value, (list, tuple)):
            return float(len(value))
    return None


_INVERSE_B_MARKERS = (
    "1/b", "1 / b", "invb", "inverse_b", "inverse b", "inverse-b", "inverse_b",
    "reciprocal", "uniform_in", "uniform in", "inv_b", "field_invb", "uniform-invB",
)


def _field_sampling(axis: Mapping[str, Any], proposal: Mapping[str, Any]) -> str:
    axis_text = json.dumps(axis, sort_keys=True).lower()
    if any(marker in axis_text for marker in _INVERSE_B_MARKERS):
        return "inverse_B"
    explicit_geometry = {
        key: proposal.get(key)
        for key in ("field_spacing", "spacing", "grid", "sampling", "field_invB",
                    "uniform_invB", "invB_uniform", "kwargs")
        if key in proposal
    }
    proposal_text = json.dumps(explicit_geometry, sort_keys=True).lower()
    if any(marker in proposal_text for marker in _INVERSE_B_MARKERS):
        return "inverse_B"
    return "linear_or_unspecified"


def _delay(delays: Mapping[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = _to_float(delays.get(key))
        if value is not None:
            return value
    return None


def extract_measurement_parameters(
    parsed: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Extract canonical physical quantities from a parsed tool-call proposal.

    Returns an exploratory, audit-friendly parameter vector that does not judge
    scientific quality. Field quantities are only extracted when a field axis is
    present; density quantities only when a density axis is present.
    """
    proposal: Mapping[str, Any] = parsed if isinstance(parsed, Mapping) else {}
    axes = _proposal_axes(proposal)
    delays = dict(proposal.get("delays")) if isinstance(proposal.get("delays"), dict) else {}
    measurement_config = proposal.get("measurement_config")
    if isinstance(measurement_config, Mapping) and "fast" not in delays:
        delays["fast"] = measurement_config.get("dwell")
    heater = proposal.get("heater")
    if isinstance(heater, Mapping) and "settle_s" not in delays:
        settle_minutes = _to_float(heater.get("settle_minutes"))
        if settle_minutes is not None:
            delays["settle_s"] = 60.0 * settle_minutes
    ladder = proposal.get("temperature_ladder")
    if isinstance(ladder, Mapping) and "settle_s" not in delays:
        delays["settle_s"] = ladder.get("thermalization_time_s")
    strong_bias_intent = bool(_STRONG_BIAS_INTENT_RE.search(
        json.dumps(proposal, sort_keys=True).lower()
    ))

    field_axis = density_axis = bias_axis = temp_axis = None
    for axis in axes:
        variables = _canonical_axis_variables(axis, strong_bias_intent=strong_bias_intent)
        if field_axis is None and "B" in variables:
            field_axis = axis
        elif density_axis is None and "n" in variables:
            density_axis = axis
        elif bias_axis is None and "I_dc" in variables:
            bias_axis = axis
        elif temp_axis is None and "T" in variables:
            temp_axis = axis

    result: dict[str, Any] = {}
    for axis, prefix in ((field_axis, "field"), (density_axis, "density"),
                         (bias_axis, "bias"), (temp_axis, "temperature")):
        if axis is None:
            continue
        start, stop = _pair_range(axis)
        points = _points(axis)
        span = abs(stop - start) if (start is not None and stop is not None) else None
        step = (span / (points - 1)) if (span is not None and points and points > 1) else None
        result[f"{prefix}_start"] = start
        result[f"{prefix}_stop"] = stop
        result[f"{prefix}_span"] = span
        result[f"{prefix}_points"] = points
        result[f"{prefix}_step"] = step
    if field_axis is not None:
        result["field_sampling"] = _field_sampling(field_axis, proposal)

    result["fast_delay"] = _delay(delays, "fast", "fast_delay", "dwell", "fast_B", "delay")
    result["slow_delay"] = _delay(delays, "slow", "slow_delay", "slow_gate", "default")
    result["settle_delay"] = _delay(delays, "settle_s", "settle", "thermal_settle", "slow_thermalize")
    return result


def summarize_tool_calls(
    parsed_calls: Iterable[Mapping[str, Any] | None],
) -> dict[str, Any]:
    """Return auditable counts and Shannon entropy for classified calls."""
    classifications = [classify_tool_call(parsed) for parsed in parsed_calls]
    type_values = [item.measurement_type for item in classifications]
    variable_values = ["{" + ",".join(item.swept_variables) + "}" for item in classifications]
    return {
        "classifier_version": CLASSIFIER_VERSION,
        "n": len(classifications),
        "measurement_type_counts": dict(sorted(Counter(type_values).items())),
        "measurement_type_entropy_bits": shannon_entropy_bits(type_values),
        "swept_variable_set_counts": dict(sorted(Counter(variable_values).items())),
        "swept_variable_set_entropy_bits": shannon_entropy_bits(variable_values),
        "classifications": [item.to_dict() for item in classifications],
    }
