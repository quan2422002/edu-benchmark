"""Lazy model-provider factory registry."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .contracts import ModelProvider


ProviderFactory = Callable[..., ModelProvider]


class ProviderRegistry:
    """Resolve provider factories without importing optional SDKs eagerly."""

    def __init__(self) -> None:
        self._factories: dict[str, ProviderFactory] = {}

    @staticmethod
    def normalize_backend(backend: str) -> str:
        normalized = backend.strip().lower().replace("-", "_")
        aliases = {
            "vertex": "vertex_ai",
            "google_vertex": "vertex_ai",
            "openai_api": "openai",
        }
        return aliases.get(normalized, normalized)

    def register(self, backend: str, factory: ProviderFactory) -> None:
        normalized = self.normalize_backend(backend)
        if not normalized:
            raise ValueError("backend must be non-empty")
        self._factories[normalized] = factory

    def create(self, backend: str, **kwargs: Any) -> ModelProvider:
        normalized = self.normalize_backend(backend)
        factory = self._factories.get(normalized)
        if factory is None:
            factory = _builtin_factory(normalized)
        return factory(**kwargs)


def _builtin_factory(backend: str) -> ProviderFactory:
    if backend == "vertex_ai":
        from .vertex_ai import VertexAIProvider

        return VertexAIProvider
    if backend == "openai":
        from .openai import OpenAIProvider

        return OpenAIProvider
    raise ValueError(f"unsupported model-provider backend: {backend}")


def create_provider(backend: str, **kwargs: Any) -> ModelProvider:
    """Create a built-in provider by normalized backend name."""

    return ProviderRegistry().create(backend, **kwargs)
