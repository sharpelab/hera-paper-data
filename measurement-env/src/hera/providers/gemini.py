"""Gemini implementation of the HERA Provider interface.

Uses google-genai with CachedContent for the stable prefix. The cache stores
the system instruction + glossary + output prefs + device card + multi-channel
exemplar; per-call we send only the target image and a small scan-context blob.
"""

from __future__ import annotations

import datetime as _dt
import sys
from typing import Optional

from google.genai import Client, errors as genai_errors, types

from hera import cache as cache_mod
from hera.cache import CacheHandle
from hera.models import Annotation
from hera.prompt import CallSuffix, StablePrefix, call_intro_text
from hera.provider import ClassifyResult, Provider


def _prefix_to_parts(prefix: StablePrefix) -> list[types.Part]:
    parts: list[types.Part] = []
    text_blocks = list(prefix.text_blocks)
    images = list(prefix.images)
    # Interleave: glossary/prefs/device, then exemplar text-then-images, then exemplar annotation.
    # The text_blocks order from build_stable_prefix() is:
    #   [glossary, prefs, device_card, exemplar_intro, exemplar_annotation_json].
    # Insert images between exemplar_intro (idx 3) and exemplar_annotation_json (idx 4).
    intro_split = min(4, len(text_blocks))
    for tb in text_blocks[:intro_split]:
        parts.append(types.Part.from_text(text=tb))
    for img in images:
        parts.append(types.Part.from_text(text=f"[{img.label}]"))
        parts.append(types.Part.from_bytes(data=img.data, mime_type=img.mime_type))
    for tb in text_blocks[intro_split:]:
        parts.append(types.Part.from_text(text=tb))
    return parts


def _suffix_to_parts(suffix: CallSuffix) -> list[types.Part]:
    intro = call_intro_text(suffix)
    return [
        types.Part.from_text(text=intro),
        types.Part.from_text(text=f"[target image: {suffix.target_image.label}]"),
        types.Part.from_bytes(
            data=suffix.target_image.data,
            mime_type=suffix.target_image.mime_type,
        ),
    ]


class GeminiProvider(Provider):
    DEFAULT_TTL = 3600  # 1 hour

    def __init__(self, *, api_key: str, model: str, use_cache: bool = True, ttl_seconds: int = DEFAULT_TTL):
        if not api_key:
            raise ValueError("GeminiProvider requires an api_key")
        self._client = Client(api_key=api_key)
        self._model = model if model.startswith("models/") else f"models/{model}"
        self._use_cache = use_cache
        self._ttl_seconds = ttl_seconds

    def model_name(self) -> str:
        return self._model

    # --- caching ---------------------------------------------------------

    def prepare_cache(self, prefix: StablePrefix) -> Optional[CacheHandle]:
        if not self._use_cache:
            return None
        existing = cache_mod.load(prefix.content_hash)
        if existing and existing.model == self._model:
            # Optimistic: assume still valid. classify() will catch NotFound and recreate.
            return existing
        return self._create_cache(prefix)

    def _create_cache(self, prefix: StablePrefix) -> Optional[CacheHandle]:
        parts = _prefix_to_parts(prefix)
        contents = [types.Content(role="user", parts=parts)]
        config = types.CreateCachedContentConfig(
            ttl=f"{self._ttl_seconds}s",
            display_name=f"hera-classify-{prefix.content_hash}",
            contents=contents,
            system_instruction=prefix.system_instruction,
        )
        try:
            cached = self._client.caches.create(model=self._model, config=config)
        except genai_errors.ClientError as e:
            # Common failure: prefix smaller than the model's cache minimum.
            print(
                f"[hera] caches.create failed ({e}); falling back to inline prefix.",
                file=sys.stderr,
            )
            return None
        if not cached.name:
            print("[hera] caches.create returned no name; falling back to inline.", file=sys.stderr)
            return None
        handle = CacheHandle(
            cache_name=cached.name,
            content_hash=prefix.content_hash,
            model=self._model,
            created_at=_dt.datetime.now(_dt.timezone.utc).isoformat(),
            ttl_seconds=self._ttl_seconds,
        )
        cache_mod.save(handle)
        return handle

    # --- classify --------------------------------------------------------

    def classify(
        self,
        prefix: StablePrefix,
        suffix: CallSuffix,
        *,
        cache: Optional[CacheHandle],
        dry_run: bool = False,
    ) -> ClassifyResult:
        suffix_parts = _suffix_to_parts(suffix)
        if cache is not None:
            generate_config = types.GenerateContentConfig(
                cached_content=cache.cache_name,
                response_mime_type="application/json",
                response_schema=Annotation,
            )
            contents = [types.Content(role="user", parts=suffix_parts)]
        else:
            prefix_parts = _prefix_to_parts(prefix)
            generate_config = types.GenerateContentConfig(
                system_instruction=prefix.system_instruction,
                response_mime_type="application/json",
                response_schema=Annotation,
            )
            contents = [types.Content(role="user", parts=prefix_parts + suffix_parts)]

        if dry_run:
            return ClassifyResult(
                annotation=_stub_annotation(suffix),
                raw_response="(dry-run: no API call)",
                cache_name=cache.cache_name if cache else None,
            )

        try:
            resp = self._client.models.generate_content(
                model=self._model,
                contents=contents,
                config=generate_config,
            )
        except genai_errors.ClientError as e:
            # If the cache was the issue, retry once with inline prefix.
            if cache is not None and "not found" in str(e).lower():
                print(
                    f"[hera] cache {cache.cache_name} not found; retrying with inline prefix.",
                    file=sys.stderr,
                )
                cache_mod.discard(cache.content_hash)
                return self.classify(prefix, suffix, cache=None, dry_run=False)
            raise

        text = resp.text or ""
        annotation = Annotation.model_validate_json(text)
        return ClassifyResult(
            annotation=annotation,
            raw_response=text,
            cache_name=cache.cache_name if cache else None,
        )


def _stub_annotation(suffix: CallSuffix) -> Annotation:
    """Placeholder Annotation for --dry-run."""
    from hera.models import Finding, ScanLimits

    return Annotation(
        scratchpad="(dry-run: no API call was made)",
        scan_limits=ScanLimits(vbg_min=-1.0, vbg_max=1.0, vtg_min=-1.0, vtg_max=1.0),
        device=suffix.device,
        scan_id=suffix.scan_id,
        findings=[
            Finding(
                id="dry_run_stub",
                title="(dry-run stub finding)",
                description="No API call performed; this is a placeholder.",
            )
        ],
    )
