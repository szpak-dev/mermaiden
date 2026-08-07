from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BlockDiagramConfiguration:
    padding: float = 8

    def to_mermaid(self) -> dict[str, object]:
        return {"padding": self.padding}
