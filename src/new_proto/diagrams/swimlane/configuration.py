from dataclasses import dataclass
from enum import StrEnum


class LineHops(StrEnum):
    ARC = "arc"
    GAP = "gap"


@dataclass(frozen=True, slots=True)
class SwimlaneConfiguration:
    line_hops: LineHops | bool = LineHops.ARC
    ignore_cross_lane_edges: bool = True
    optimize_ranks_by_crossings: bool = True
    automatic_lane_ordering: bool = False

    def to_mermaid(self) -> dict[str, object]:
        return {
            "lineHops": self.line_hops,
            "ignoreCrossLaneEdges": self.ignore_cross_lane_edges,
            "optimizeRanksByCrossings": self.optimize_ranks_by_crossings,
            "automaticLaneOrdering": self.automatic_lane_ordering,
        }
