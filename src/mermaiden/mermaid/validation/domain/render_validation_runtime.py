from abc import ABC, abstractmethod
from collections.abc import Mapping

from .models import RendererRuntimeResult


class RenderValidationRuntime(ABC):
    @property
    @abstractmethod
    def mermaid_version(self) -> str: ...

    @property
    @abstractmethod
    def mermaid_cli_version(self) -> str: ...

    @abstractmethod
    def render(self, sources: Mapping[str, str]) -> RendererRuntimeResult: ...
