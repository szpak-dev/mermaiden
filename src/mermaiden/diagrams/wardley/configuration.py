from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WardleyDiagramConfiguration:
    def to_mermaid(self) -> dict[str, object]:
        return {}
