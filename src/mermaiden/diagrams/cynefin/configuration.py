from ..configuration import MermaidDiagramConfiguration


class CynefinDiagramConfiguration(MermaidDiagramConfiguration):
    width: float = 800
    height: float = 600
    padding: float = 40
    show_domain_descriptions: bool = True
    boundary_amplitude: float = 8
    seed: float = 1
