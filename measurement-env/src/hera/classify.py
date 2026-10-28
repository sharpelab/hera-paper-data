"""hera-classify CLI entrypoint.

Usage:
    hera-classify <image_path> [--scan-context FILE] [--device DEVICE]
                  [--brief] [--no-cache] [--model MODEL] [--dry-run]
                  [--sidecar PATH] [--scan-id SCAN_ID]

One-shot: Reads an image, calls Gemini (or `--dry-run` stubs), writes a sidecar
JSON, prints structured markdown to stdout. HERA's parent Claude reads only
the markdown.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path
from typing import Optional

from hera import cache as cache_mod
from hera.models import Annotation, Provenance
from hera.prompt import build_call_suffix, build_stable_prefix
from hera.providers.gemini import GeminiProvider
from hera.render import render
from hera.sidecar import default_sidecar_path, utc_timestamp, write_sidecar


def _resolve_api_key(cli_key: Optional[str]) -> str:
    if cli_key:
        return cli_key
    env = os.getenv("GEMINI_API_KEY")
    if env:
        return env
    try:
        from core.config import load_config
    except ImportError:
        sys.exit(
            "error: GEMINI_API_KEY not set and core.config not importable. "
            "Set GEMINI_API_KEY in env or [hera].gemini_api_key in toploader.toml."
        )
    try:
        cfg = load_config()
    except Exception as e:
        sys.exit(f"error: failed to load toploader.toml ({e}). Set GEMINI_API_KEY in env to override.")
    if cfg.hera and cfg.hera.gemini_api_key:
        return cfg.hera.gemini_api_key
    sys.exit(
        "error: no Gemini API key found. Set GEMINI_API_KEY in env, "
        "or [hera].gemini_api_key in toploader.toml."
    )


def _resolve_model(cli_model: Optional[str]) -> str:
    if cli_model:
        return cli_model
    try:
        from core.config import load_config
        cfg = load_config()
        if cfg.hera and cfg.hera.classifier_model:
            return cfg.hera.classifier_model
    except Exception:
        pass
    return "gemini-2.5-flash"


def _resolve_scan_id(cli_value: Optional[str], image_path: Path) -> str:
    if cli_value:
        return cli_value
    # Default: parent dir name (matches Nathan's "device/scan_id" layout).
    return image_path.resolve().parent.name


def _read_optional_file(path: Optional[str]) -> str:
    if not path:
        return ""
    p = Path(path)
    if not p.exists():
        sys.exit(f"error: --scan-context file does not exist: {path}")
    return p.read_text()


def _run_main(argv: list[str] | None = None) -> int:
    """Core classify logic, testable without subprocess. Returns exit code."""
    # Windows consoles default to cp1252; the rendered output uses '∈' and
    # other unicode glyphs. Reconfigure stdout to utf-8 if possible — no-op
    # on Linux where it's already utf-8.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(
        prog="hera-classify",
        description="Classify a 2D gate-map image. Returns structured markdown for HERA.",
    )
    parser.add_argument("image", type=Path, help="Path to the gate-map plot image (PNG or JPEG).")
    parser.add_argument("--scan-context", help="Path to a markdown/text file with per-scan biasing context.")
    parser.add_argument("--device", default="RPL19", help="Device id; selects the device card (default RPL19).")
    parser.add_argument("--scan-id", help="Scan id to embed in output. Defaults to image's parent dir name.")
    parser.add_argument("--brief", action="store_true", help="One-paragraph summary mode.")
    parser.add_argument("--no-cache", action="store_true", help="Disable provider-side prefix caching.")
    parser.add_argument("--model", help="Override model id (default: [hera].classifier_model or gemini-2.5-flash).")
    parser.add_argument("--api-key", help="Override Gemini API key.")
    parser.add_argument("--dry-run", action="store_true", help="Skip API call; emit a stub annotation.")
    parser.add_argument("--sidecar", help="Override sidecar path (default: <image_dir>/hera/<stem>__<ts>.json).")
    parser.add_argument(
        "--no-sidecar",
        action="store_true",
        help="Skip writing a sidecar file (rendered markdown still goes to stdout).",
    )
    args = parser.parse_args(argv)

    image_path: Path = args.image
    if not image_path.exists():
        print(f"error: image does not exist: {image_path}", file=sys.stderr)
        return 1
    if not image_path.is_file():
        print(f"error: not a file: {image_path}", file=sys.stderr)
        return 1

    model = _resolve_model(args.model)
    api_key = "" if args.dry_run else _resolve_api_key(args.api_key)
    scan_id = _resolve_scan_id(args.scan_id, image_path)
    scan_context_text = _read_optional_file(args.scan_context)

    prefix = build_stable_prefix(args.device)
    suffix = build_call_suffix(
        scan_id=scan_id,
        device=args.device,
        target_image_path=image_path,
        scan_context_text=scan_context_text,
    )

    provider = GeminiProvider(
        api_key=api_key or "dry-run",
        model=model,
        use_cache=not args.no_cache,
    )

    cache_handle = None
    if not args.no_cache and not args.dry_run:
        cache_handle = provider.prepare_cache(prefix)

    try:
        result = provider.classify(prefix, suffix, cache=cache_handle, dry_run=args.dry_run)
    except Exception as e:
        print(f"error: classify call failed: {e}", file=sys.stderr)
        return 1

    # Sidecar
    timestamp = utc_timestamp()
    sidecar_str: Optional[str] = None
    if not args.no_sidecar:
        sidecar_path = (
            Path(args.sidecar) if args.sidecar else default_sidecar_path(image_path, timestamp)
        )
        provenance = Provenance(
            model=model,
            prompt_hash=prefix.content_hash,
            image_hash=hashlib.sha256(suffix.target_image.data).hexdigest()[:16],
            image_path=str(image_path.resolve()),
            cache_name=result.cache_name,
            raw_response=result.raw_response,
        )
        write_sidecar(sidecar_path, result.annotation, provenance)
        sidecar_str = str(sidecar_path)

    md = render(
        result.annotation,
        timestamp=timestamp,
        model=model,
        brief=args.brief,
        sidecar_path=sidecar_str,
    )
    print(md, end="")
    return 0


def main() -> None:
    """CLI entrypoint."""
    sys.exit(_run_main())
