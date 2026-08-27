from collections.abc import Mapping
from typing import Protocol

from .domain import MermaidCliResult


class MermaidCli(Protocol):
    @property
    def version(self) -> str: ...

    def render(self, sources: Mapping[str, str]) -> MermaidCliResult: ...
