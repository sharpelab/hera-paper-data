"""Markdown rendering for HERA Annotation output.

Build plan shape:

    ## Scan analysis: <scan_id> @ <timestamp>

    **Channels analyzed:** ...
    **Scan limits:** ...
    **Model:** ...

    **Scratchpad (raw observations):** <prose>

    **Findings:**

    ### F1 — <title>
    - Region: ...
    - Channels: ...
    - <description>

    **Coordinate guard:** ... (✓ or ✗ with offending finding ids)
    **Sidecar:** <path>

`brief=True` returns a single-paragraph summary instead.

The coordinate guard is a deterministic numpy/python check, NOT LLM-generated.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from hera.models import Annotation, Finding, RegionGate, ScanLimits


@dataclass(frozen=True)
class GuardViolation:
    finding_id: str
    detail: str


def _finding_label(idx: int, finding: Finding) -> str:
    return finding.id or f"F{idx + 1}"


def _format_region(rg: RegionGate) -> str:
    if rg.kind == "box":
        vbg = f"[{rg.vbg_range[0]}, {rg.vbg_range[1]}]" if rg.vbg_range else "?"
        vtg = f"[{rg.vtg_range[0]}, {rg.vtg_range[1]}]" if rg.vtg_range else "?"
        return f"box, Vbg ∈ {vbg}, Vtg ∈ {vtg}"
    if rg.kind == "point":
        return f"point, Vbg={rg.vbg}, Vtg={rg.vtg}"
    if rg.kind == "line_segment":
        return f"line, ({rg.vbg_start}, {rg.vtg_start}) → ({rg.vbg_end}, {rg.vtg_end})"
    if rg.kind == "vertical_band":
        if rg.vbg_range:
            return f"vertical band, Vbg ∈ [{rg.vbg_range[0]}, {rg.vbg_range[1]}]"
        return f"vertical band at Vbg={rg.vbg}"
    if rg.kind == "horizontal_band":
        if rg.vtg_range:
            return f"horizontal band, Vtg ∈ [{rg.vtg_range[0]}, {rg.vtg_range[1]}]"
        return f"horizontal band at Vtg={rg.vtg}"
    if rg.kind == "descriptive" and rg.description:
        return rg.description
    return rg.description or rg.kind or "unspecified"


def _check_range(value: Optional[float], lo: float, hi: float) -> bool:
    return value is not None and (value < lo or value > hi)


def _check_pair(rng: Optional[List[float]], lo: float, hi: float) -> bool:
    if rng is None:
        return False
    return rng[0] < lo or rng[1] > hi


def coordinate_guard(annotation: Annotation) -> List[GuardViolation]:
    """Walk every finding's region_gate and check it falls within scan_limits.

    Returns a list of violations; empty list = all clear.
    """
    sl = annotation.scan_limits
    out: List[GuardViolation] = []
    for i, finding in enumerate(annotation.findings):
        rg = finding.region_gate
        if rg is None:
            continue
        label = _finding_label(i, finding)
        problems: List[str] = []
        if _check_range(rg.vbg, sl.vbg_min, sl.vbg_max):
            problems.append(f"vbg={rg.vbg} outside [{sl.vbg_min}, {sl.vbg_max}]")
        if _check_range(rg.vtg, sl.vtg_min, sl.vtg_max):
            problems.append(f"vtg={rg.vtg} outside [{sl.vtg_min}, {sl.vtg_max}]")
        if _check_pair(rg.vbg_range, sl.vbg_min, sl.vbg_max):
            problems.append(
                f"vbg_range={rg.vbg_range} outside [{sl.vbg_min}, {sl.vbg_max}]"
            )
        if _check_pair(rg.vtg_range, sl.vtg_min, sl.vtg_max):
            problems.append(
                f"vtg_range={rg.vtg_range} outside [{sl.vtg_min}, {sl.vtg_max}]"
            )
        for vbg, vtg, tag in (
            (rg.vbg_start, rg.vtg_start, "start"),
            (rg.vbg_end, rg.vtg_end, "end"),
        ):
            if _check_range(vbg, sl.vbg_min, sl.vbg_max):
                problems.append(
                    f"{tag} vbg={vbg} outside [{sl.vbg_min}, {sl.vbg_max}]"
                )
            if _check_range(vtg, sl.vtg_min, sl.vtg_max):
                problems.append(
                    f"{tag} vtg={vtg} outside [{sl.vtg_min}, {sl.vtg_max}]"
                )
        for p in problems:
            out.append(GuardViolation(finding_id=label, detail=p))
    return out


def _format_guard(violations: List[GuardViolation]) -> str:
    if not violations:
        return "**Coordinate guard:** all findings within scan limits ✓"
    parts = [f"{v.finding_id}: {v.detail}" for v in violations]
    return "**Coordinate guard:** ✗ " + "; ".join(parts)


def _format_scan_limits(sl: ScanLimits) -> str:
    return f"Vbg ∈ [{sl.vbg_min}, {sl.vbg_max}], Vtg ∈ [{sl.vtg_min}, {sl.vtg_max}]"


def render_full(
    annotation: Annotation,
    *,
    timestamp: str,
    model: str,
    channels: Optional[List[str]] = None,
    sidecar_path: Optional[str] = None,
) -> str:
    lines: List[str] = []
    lines.append(f"## Scan analysis: {annotation.scan_id} @ {timestamp}")
    lines.append("")
    if channels:
        lines.append(f"**Channels analyzed:** {', '.join(channels)}")
    lines.append(f"**Scan limits:** {_format_scan_limits(annotation.scan_limits)}")
    lines.append(f"**Model:** {model}")
    lines.append("")

    if annotation.scratchpad:
        lines.append("**Scratchpad (raw observations):**")
        lines.append("")
        lines.append(annotation.scratchpad.strip())
        lines.append("")

    lines.append("**Findings:**")
    lines.append("")
    for i, finding in enumerate(annotation.findings):
        label = _finding_label(i, finding)
        heading = f"### {label} — {finding.title}"
        if finding.confidence is not None:
            heading += f" (confidence {finding.confidence:.2f})"
        lines.append(heading)
        if finding.region_gate is not None:
            lines.append(f"- Region: {_format_region(finding.region_gate)}")
        if finding.channels:
            lines.append(f"- Channels: {', '.join(finding.channels)}")
        lines.append(f"- {finding.description.strip()}")
        lines.append("")

    if annotation.follow_ups:
        lines.append("**Follow-ups:**")
        for f in annotation.follow_ups:
            lines.append(f"- {f}")
        lines.append("")

    lines.append(_format_guard(coordinate_guard(annotation)))
    if sidecar_path is not None:
        lines.append(f"**Sidecar:** {sidecar_path}")

    return "\n".join(lines).rstrip() + "\n"


def render_brief(annotation: Annotation) -> str:
    """One-paragraph summary for `--brief` mode polling."""
    n = len(annotation.findings)
    titles = []
    for finding in annotation.findings:
        t = finding.title
        if finding.confidence is not None:
            t = f"{t} (conf {finding.confidence:.2f})"
        titles.append(t)
    suffix = "; ".join(titles) if titles else "no findings"
    return f"{annotation.scan_id}: {n} finding{'s' if n != 1 else ''} — {suffix}.\n"


def render(
    annotation: Annotation,
    *,
    timestamp: str,
    model: str,
    brief: bool = False,
    channels: Optional[List[str]] = None,
    sidecar_path: Optional[str] = None,
) -> str:
    if brief:
        return render_brief(annotation)
    return render_full(
        annotation,
        timestamp=timestamp,
        model=model,
        channels=channels,
        sidecar_path=sidecar_path,
    )
