from enum import StrEnum

from ..domain import MermaidDiagramConfiguration


class LegendPosition(StrEnum):
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class PieDiagramConfiguration(MermaidDiagramConfiguration):
    text_position: float = 0.75
    donut_hole: float = 0
    legend_position: LegendPosition = LegendPosition.RIGHT
    highlight_slice: str = ""
