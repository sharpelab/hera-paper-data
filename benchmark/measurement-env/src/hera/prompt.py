"""Prompt assembly for HERA classifier.

Two halves:
- `StablePrefix` — cacheable across calls. System instruction + glossary +
  output prefs + device card + multi-channel exemplar (image bytes + JSON).
- `CallSuffix` — per-call. Target image + scan-context blob.

For v0 the device card defaults to RPL19; the exemplar defaults to RPL19/18
(5-channel set with 4-finding annotation). Workstream B will refine content.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

ASSETS = Path(__file__).resolve().parent / "assets"
EXEMPLAR_DIR = ASSETS / "exemplar_RPL19_18"
EXEMPLAR_CHANNELS = ("plot", "rxx_phase", "current", "current_phase", "rxx_nD")


@dataclass(frozen=True)
class ImagePart:
    label: str
    mime_type: str
    data: bytes


@dataclass(frozen=True)
class StablePrefix:
    """Content cached on the provider side; same for every call within a (device, exemplar) combo."""

    system_instruction: str
    text_blocks: Tuple[str, ...]
    images: Tuple[ImagePart, ...]
    content_hash: str


@dataclass(frozen=True)
class CallSuffix:
    """Per-call variable content."""

    scan_id: str
    device: str
    target_image: ImagePart
    scan_context_text: str  # may be empty


def _read_text(path: Path) -> str:
    return path.read_text().strip()


def _load_device_cards() -> dict:
    return json.loads((ASSETS / "device_cards.json").read_text())


def _format_device_card(device: str) -> str:
    cards = _load_device_cards()
    card = cards.get(device)
    if not card:
        return f"### Device Card\n- Device: {device}\n- (No vendored card for this device; HERA caller may pass extra context via --scan-context.)"
    lines = [f"### Device Card", f"- Device: {device}"]
    if "top_hbn_nm" in card and "bottom_hbn_nm" in card:
        lines.append(f"- Top hBN: {card['top_hbn_nm']:g} nm")
        lines.append(f"- Bottom hBN: {card['bottom_hbn_nm']:g} nm")
    if card.get("gate_coupling_note"):
        lines.append(f"- Gate coupling: {card['gate_coupling_note']}")
    if card.get("nd_transform_note"):
        lines.append(f"- n/D note: {card['nd_transform_note']}")
    return "\n".join(lines)


def _exemplar_images() -> Tuple[ImagePart, ...]:
    out: List[ImagePart] = []
    for name in EXEMPLAR_CHANNELS:
        p = EXEMPLAR_DIR / f"{name}.png"
        if not p.exists():
            continue
        out.append(ImagePart(label=f"exemplar_{name}", mime_type="image/png", data=p.read_bytes()))
    return tuple(out)


def _exemplar_annotation_text() -> str:
    p = EXEMPLAR_DIR / "annotations.json"
    if not p.exists():
        return ""
    parsed = json.loads(p.read_text())
    return json.dumps(parsed, indent=2)


def build_stable_prefix(device: str = "RPL19") -> StablePrefix:
    system = _read_text(ASSETS / "system_instruction.md")
    glossary = _read_text(ASSETS / "context_glossary.md")
    prefs = _read_text(ASSETS / "expert_output_preferences.md")
    device_card = _format_device_card(device)
    exemplar_json = _exemplar_annotation_text()

    text_blocks: List[str] = [
        glossary,
        prefs,
        device_card,
        (
            "### Exemplar (for shape only — do NOT copy coordinates)\n"
            "The following images are a single multi-channel scan from device RPL19, scan id 18.\n"
            "They are followed by the structured annotation an expert produced for THAT scan.\n"
            "Use it to calibrate your output style and finding-density. The TARGET image you classify\n"
            "below has its own coordinates; do not reuse the exemplar's."
        ),
    ]
    images = _exemplar_images()
    text_blocks.append("Exemplar annotation (RPL19/18):\n```json\n" + exemplar_json + "\n```")

    # Hash the assembled prefix content (text + image bytes + system instruction) for cache identity.
    h = hashlib.sha256()
    h.update(system.encode())
    for tb in text_blocks:
        h.update(b"\x00TEXT\x00")
        h.update(tb.encode())
    for img in images:
        h.update(b"\x00IMG\x00")
        h.update(img.label.encode())
        h.update(img.data)
    content_hash = h.hexdigest()[:16]

    return StablePrefix(
        system_instruction=system,
        text_blocks=tuple(text_blocks),
        images=images,
        content_hash=content_hash,
    )


def build_call_suffix(
    *,
    scan_id: str,
    device: str,
    target_image_path: Path,
    scan_context_text: str = "",
) -> CallSuffix:
    data = target_image_path.read_bytes()
    mime = "image/png" if target_image_path.suffix.lower() == ".png" else "image/jpeg"
    return CallSuffix(
        scan_id=scan_id,
        device=device,
        target_image=ImagePart(label="target", mime_type=mime, data=data),
        scan_context_text=scan_context_text or "",
    )


def call_intro_text(suffix: CallSuffix) -> str:
    """Header text that precedes the target image in the per-call payload."""
    parts = [
        "### Target scan",
        f"- Device: {suffix.device}",
        f"- Scan id: {suffix.scan_id}",
    ]
    if suffix.scan_context_text:
        parts.append("")
        parts.append("### Per-call scan context")
        parts.append(suffix.scan_context_text)
    parts.append("")
    parts.append(
        "Classify the TARGET image that follows. Populate `scan_limits` with the axis ranges "
        "you infer from the target image. Do not copy coordinates from the exemplar."
    )
    return "\n".join(parts)


def hash_image_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]
