from enum import StrEnum
from typing import Annotated

from pydantic import ConfigDict, Field, RootModel

from ..domain import MermaidDiagramConfiguration


class LineHops(StrEnum):
    ARC = "arc"
    GAP = "gap"


class LineHopsValue(RootModel[bool | LineHops]):
    model_config = ConfigDict(frozen=True)


class SwimlaneConfiguration(MermaidDiagramConfiguration):
    line_hops: Annotated[LineHopsValue, Field(alias="lineHops")] = LineHopsValue(root=LineHops.ARC)
    ignore_cross_lane_edges: Annotated[bool, Field(alias="ignoreCrossLaneEdges")] = True
    optimize_ranks_by_crossings: Annotated[bool, Field(alias="optimizeRanksByCrossings")] = True
    automatic_lane_ordering: Annotated[bool, Field(alias="automaticLaneOrdering")] = False
