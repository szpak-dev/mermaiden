from ..configuration import MermaidDiagramConfiguration


class VennConfiguration(MermaidDiagramConfiguration):
    width: float = 800
    height: float = 450
    padding: float = 8
    use_debug_layout: bool = False
