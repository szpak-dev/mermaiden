from ..domain import MermaidDiagramConfiguration


class MindmapDiagramConfiguration(MermaidDiagramConfiguration):
    use_max_width: bool = True
    padding: int = 10
    max_node_width: int = 200
    layout_algorithm: str = "cose-bilkent"
