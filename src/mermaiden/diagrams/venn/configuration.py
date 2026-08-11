from ..configuration import MermaidDiagramConfiguration


class VennConfiguration(MermaidDiagramConfiguration):
    width: int = 800
    height: int = 450
    padding: int = 8
    use_debug_layout: bool = False
