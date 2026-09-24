from abc import ABC, abstractmethod
from collections.abc import Mapping

from .domain import MermaidCliResult


class MermaidCli(ABC):
    @property
    @abstractmethod
    def version(self) -> str: ...

    @abstractmethod
    def render(self, sources: Mapping[str, str]) -> MermaidCliResult: ...
