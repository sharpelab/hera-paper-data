"""Prompt-assembly sanity tests. No live API calls."""

from __future__ import annotations

from pathlib import Path

from hera.prompt import EXEMPLAR_DIR, build_call_suffix, build_stable_prefix


def test_stable_prefix_has_exemplar_images_and_text() -> None:
    prefix = build_stable_prefix("RPL19")
    assert prefix.system_instruction
    assert len(prefix.text_blocks) >= 4  # glossary, prefs, device, exemplar intro, exemplar JSON
    assert len(prefix.images) == 5  # 5 channels in RPL19/18 exemplar
    # Content hash is hex, 16 chars.
    assert len(prefix.content_hash) == 16
    int(prefix.content_hash, 16)


def test_stable_prefix_content_hash_is_deterministic() -> None:
    a = build_stable_prefix("RPL19")
    b = build_stable_prefix("RPL19")
    assert a.content_hash == b.content_hash


def test_stable_prefix_changes_when_device_changes() -> None:
    a = build_stable_prefix("RPL19")
    b = build_stable_prefix("RPL10")
    assert a.content_hash != b.content_hash


def test_build_call_suffix_loads_image_bytes() -> None:
    target = EXEMPLAR_DIR / "plot.png"
    suffix = build_call_suffix(scan_id="18", device="RPL19", target_image_path=target)
    assert suffix.scan_id == "18"
    assert suffix.target_image.mime_type == "image/png"
    assert len(suffix.target_image.data) > 100


def test_unknown_device_does_not_crash() -> None:
    prefix = build_stable_prefix("UNKNOWN_DEVICE")
    # Falls back to a minimal device card.
    assert any("UNKNOWN_DEVICE" in tb for tb in prefix.text_blocks)
