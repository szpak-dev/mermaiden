from ..configuration import MermaidDiagramConfiguration


class MindmapDiagramConfiguration(MermaidDiagramConfiguration):
    use_max_width: bool = True
    padding: int = 10
    max_node_width: int = 200
    layout_algorithm: str = "cose-bilkent"

    def to_mermaid(self) -> dict[str, object]:
        return {
            "useMaxWidth": self.use_max_width,
            "padding": self.padding,
            "maxNodeWidth": self.max_node_width,
            "layoutAlgorithm": self.layout_algorithm,
        }
