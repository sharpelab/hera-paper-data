"""Provider abstraction for HERA classifier.

A `Provider` knows how to:
- prepare a stable prefix on its side (e.g. Gemini CachedContent), returning a
  CacheHandle that can be reused across calls;
- run a one-shot classification call given the cache (or inlined prefix as
  fallback) plus a per-call suffix, returning a validated `Annotation`.

Gemini is the only implementation for v0. The ABC exists so adding an
Anthropic / OpenAI backend later is mechanical.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from hera.cache import CacheHandle
from hera.models import Annotation
from hera.prompt import CallSuffix, StablePrefix


@dataclass(frozen=True)
class ClassifyResult:
    annotation: Annotation
    raw_response: str
    cache_name: Optional[str]


class Provider(ABC):
    @abstractmethod
    def model_name(self) -> str: ...

    @abstractmethod
    def prepare_cache(self, prefix: StablePrefix) -> Optional[CacheHandle]:
        """Create or load a server-side cache for `prefix`. Returns None if caching is disabled or unavailable."""

    @abstractmethod
    def classify(
        self,
        prefix: StablePrefix,
        suffix: CallSuffix,
        *,
        cache: Optional[CacheHandle],
        dry_run: bool = False,
    ) -> ClassifyResult:
        """Run the classification call. If `cache` is None, inline the prefix."""
