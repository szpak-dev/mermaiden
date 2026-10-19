from enum import StrEnum
from typing import Annotated

from pydantic import Field

from ...core.characters import OptionalText
from ..domain import MermaidDiagramConfiguration


class LegendPosition(StrEnum):
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class PieDiagramConfiguration(MermaidDiagramConfiguration):
    text_position: Annotated[float, Field(alias="textPosition", ge=0, le=1)] = 0.75
    donut_hole: Annotated[float, Field(alias="donutHole", ge=0, le=0.9)] = 0
    legend_position: Annotated[LegendPosition, Field(alias="legendPosition")] = LegendPosition.RIGHT
    highlight_slice: Annotated[
        str, Field(alias="highlightSlice", pattern=OptionalText.pattern, description=OptionalText.description)
    ] = ""
