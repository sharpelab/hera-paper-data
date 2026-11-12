"""Pydantic models for HERA gate-map classifier output.

Field names match Nathan's measure4me schema so dataset/*/annotations.json
files validate against this model — gives us free test fixtures.

Provenance is a separate sub-model so the LLM-emitted Annotation stays clean;
HERA writes Provenance into the sidecar wrapper after the call returns.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ScanLimits(BaseModel):
    vbg_min: float
    vbg_max: float
    vtg_min: float
    vtg_max: float


class RegionGate(BaseModel):
    kind: Optional[str] = None
    vbg: Optional[float] = None
    vtg: Optional[float] = None
    vbg_range: Optional[List[float]] = None
    vtg_range: Optional[List[float]] = None
    vbg_start: Optional[float] = None
    vtg_start: Optional[float] = None
    vbg_end: Optional[float] = None
    vtg_end: Optional[float] = None
    description: Optional[str] = None

    @field_validator("vbg_range", "vtg_range")
    @classmethod
    def _validate_range(cls, v):
        if v is None:
            return v
        if len(v) != 2:
            raise ValueError("range must have exactly two values [min, max]")
        return v

    @model_validator(mode="after")
    def _validate_and_infer_kind(self):
        has_vbg = self.vbg is not None or self.vbg_range is not None
        has_vtg = self.vtg is not None or self.vtg_range is not None
        has_line = (
            self.vbg_start is not None
            and self.vtg_start is not None
            and self.vbg_end is not None
            and self.vtg_end is not None
        )
        if not has_vbg and not has_vtg and not has_line and not self.description:
            raise ValueError("region_gate must include coordinates, ranges, or a description")
        if self.kind is None:
            if self.vbg is not None and self.vtg is not None:
                self.kind = "point"
            elif has_line:
                self.kind = "line_segment"
            elif self.vbg_range is not None and self.vtg_range is not None:
                self.kind = "box"
            elif has_vbg and not has_vtg:
                self.kind = "vertical_band"
            elif has_vtg and not has_vbg:
                self.kind = "horizontal_band"
            else:
                self.kind = "descriptive"
        elif self.kind == "line_segment" and not has_line:
            raise ValueError("line_segment requires vbg_start, vtg_start, vbg_end, and vtg_end")
        return self


class Context(BaseModel):
    temperature_mK: Optional[float] = None
    magnetic_field_T: Optional[float] = None
    bias_nA: Optional[float] = None
    notes: Optional[str] = None


class Finding(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    category: Optional[str] = None
    confidence: Optional[float] = None
    region_gate: Optional[RegionGate] = None
    channels: Optional[List[str]] = None

    @field_validator("region_gate", mode="before")
    @classmethod
    def _normalize_region_gate(cls, value):
        if value is None:
            return value
        if isinstance(value, str):
            return {"kind": "descriptive", "description": value}
        return value


class Annotation(BaseModel):
    """The structured payload the LLM returns. Matches Nathan's shape."""

    scratchpad: Optional[str] = None
    scan_limits: ScanLimits
    device: str
    scan_id: str
    plot_kind: Optional[str] = None
    x_axis_name: Optional[str] = None
    y_axis_name: Optional[str] = None
    context: Optional[Context] = None
    findings: List[Finding]
    follow_ups: Optional[List[str]] = None


class Provenance(BaseModel):
    """Sidecar metadata about how the annotation was produced.

    Kept off Annotation so the LLM doesn't see / fill these fields.
    """

    model_config = ConfigDict(protected_namespaces=())

    model: str
    prompt_hash: str
    image_hash: str
    image_path: str
    cache_name: Optional[str] = None
    raw_response: Optional[str] = None
    channels: Optional[List[str]] = None


class Sidecar(BaseModel):
    """What gets written to <image_dir>/hera/<image_stem>__<timestamp>.json."""

    annotation: Annotation
    provenance: Provenance
