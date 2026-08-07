from ..configuration import MermaidDiagramConfiguration


class IshikawaDiagramConfiguration(MermaidDiagramConfiguration):
    def to_mermaid(self) -> dict[str, object]:
        return {}
