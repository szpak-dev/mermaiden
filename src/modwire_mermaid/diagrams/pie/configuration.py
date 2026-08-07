from dataclasses import dataclass
from enum import StrEnum


class LegendPosition(StrEnum):
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


@dataclass(frozen=True, slots=True)
class PieDiagramConfiguration:
    text_position: float = 0.75
    donut_hole: float = 0
    legend_position: LegendPosition = LegendPosition.RIGHT
    highlight_slice: str = ""

    def to_mermaid(self) -> dict[str, object]:
        return {
            "textPosition": self.text_position,
            "donutHole": self.donut_hole,
            "legendPosition": self.legend_position,
            "highlightSlice": self.highlight_slice,
        }
