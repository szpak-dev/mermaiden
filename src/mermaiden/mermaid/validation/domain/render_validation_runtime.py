from abc import ABC, abstractmethod
from collections.abc import Mapping
from pathlib import Path

from .models import PngRenderOptions, RendererRuntimeResult


class RenderValidationRuntime(ABC):
    @abstractmethod
    def setup_renderer(self, prefix: Path) -> str: ...

    @property
    @abstractmethod
    def mermaid_version(self) -> str: ...

    @property
    @abstractmethod
    def mermaid_cli_version(self) -> str: ...

    @abstractmethod
    def render(self, sources: Mapping[str, str]) -> RendererRuntimeResult: ...

    @abstractmethod
    def render_png(self, source: str, options: PngRenderOptions) -> bytes: ...
