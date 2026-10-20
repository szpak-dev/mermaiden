from typing import Annotated

from pydantic import Field

from ...core.characters import Text
from ..domain import MermaidDiagramConfiguration


class RequirementDiagramConfiguration(MermaidDiagramConfiguration):
    rect_fill: Annotated[str, Field(alias="rectFill", pattern=Text.pattern, description=Text.description)] = "#f9f9f9"
    text_color: Annotated[str, Field(alias="textColor", pattern=Text.pattern, description=Text.description)] = "#333"
    rect_border_size: Annotated[
        str, Field(alias="rectBorderSize", pattern=Text.pattern, description=Text.description)
    ] = "0.5px"
    rect_border_color: Annotated[
        str, Field(alias="rectBorderColor", pattern=Text.pattern, description=Text.description)
    ] = "#bbb"
    rect_min_width: Annotated[float, Field(alias="rectMinWidth")] = 200
    rect_min_height: Annotated[float, Field(alias="rectMinHeight")] = 200
    font_size: Annotated[float, Field(alias="fontSize")] = 14
    rect_padding: Annotated[float, Field(alias="rectPadding")] = 10
    line_height: Annotated[float, Field(alias="lineHeight")] = 20
