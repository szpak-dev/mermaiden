from pydantic import Field

from ..domain import MermaidDiagramConfiguration


class ArchitectureDiagramConfiguration(MermaidDiagramConfiguration):
    use_max_width: bool = True
    padding: float = Field(default=40, ge=0)
    icon_size: float = Field(default=80, gt=0)
    font_size: float = Field(default=16, gt=0)
    randomize: bool = False
    node_separation: float = Field(default=75, ge=0)
    ideal_edge_length_multiplier: float = Field(default=1.5, gt=0)
    edge_elasticity: float = Field(default=0.45, ge=0, le=1)
    num_iter: int = Field(default=2500, gt=0)
    seed: float = 1
