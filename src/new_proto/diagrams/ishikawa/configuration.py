from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IshikawaDiagramConfiguration:
    def to_mermaid(self) -> dict[str, object]:
        return {}
