from typing import Annotated

from pydantic import Field

from ..domain import MermaidDiagramConfiguration


class ArchitectureDiagramConfiguration(MermaidDiagramConfiguration):
    padding: Annotated[float, Field(alias="padding")] = 40
    icon_size: Annotated[float, Field(alias="iconSize")] = 80
    font_size: Annotated[float, Field(alias="fontSize")] = 16
    randomize: Annotated[bool, Field(alias="randomize")] = False
    node_separation: Annotated[float, Field(alias="nodeSeparation")] = 75
    ideal_edge_length_multiplier: Annotated[float, Field(alias="idealEdgeLengthMultiplier")] = 1.5
    edge_elasticity: Annotated[float, Field(alias="edgeElasticity")] = 0.45
    num_iter: Annotated[float, Field(alias="numIter")] = 2500
    seed: Annotated[float, Field(alias="seed")] = 1
