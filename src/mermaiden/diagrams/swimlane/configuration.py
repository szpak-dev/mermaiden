from enum import StrEnum

from ..domain import MermaidDiagramConfiguration


class LineHops(StrEnum):
    ARC = "arc"
    GAP = "gap"


class SwimlaneConfiguration(MermaidDiagramConfiguration):
    line_hops: LineHops | bool = LineHops.ARC
    ignore_cross_lane_edges: bool = True
    optimize_ranks_by_crossings: bool = True
    automatic_lane_ordering: bool = False
