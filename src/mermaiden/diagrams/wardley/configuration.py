from ..configuration import MermaidDiagramConfiguration


class WardleyDiagramConfiguration(MermaidDiagramConfiguration):
    def to_mermaid(self) -> dict[str, object]:
        return {}
