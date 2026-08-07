from ..configuration import MermaidDiagramConfiguration


class BlockDiagramConfiguration(MermaidDiagramConfiguration):
    padding: float = 8

    def to_mermaid(self) -> dict[str, object]:
        return {"padding": self.padding}
