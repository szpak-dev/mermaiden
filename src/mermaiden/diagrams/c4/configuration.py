from ..configuration import MermaidDiagramConfiguration


class C4ContextDiagramConfiguration(MermaidDiagramConfiguration):
    def to_mermaid(self) -> dict[str, object]:
        return {}
