from typing import Annotated

from pydantic import Field

from ...core.characters import Text
from ..domain import (
    MermaidDiagramConfiguration,
    MermaidLook,
    MermaidLookField,
    MermaidTheme,
    MermaidThemeField,
    OmittableLook,
    OmittableTheme,
)


class RequirementDiagramConfiguration(MermaidDiagramConfiguration):
    theme: MermaidThemeField = OmittableTheme(root=MermaidTheme.REDUX_COLOR)
    look: MermaidLookField = OmittableLook(root=MermaidLook.NEO)
    rect_fill: Annotated[str, Field(alias="rect_fill", pattern=Text.pattern, description=Text.description)] = "#f9f9f9"
    text_color: Annotated[str, Field(alias="text_color", pattern=Text.pattern, description=Text.description)] = "#333"
    rect_border_size: Annotated[
        str, Field(alias="rect_border_size", pattern=Text.pattern, description=Text.description)
    ] = "0.5px"
    rect_border_color: Annotated[
        str, Field(alias="rect_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#bbb"
    rect_min_width: Annotated[float, Field(alias="rect_min_width")] = 200
    rect_min_height: Annotated[float, Field(alias="rect_min_height")] = 200
    font_size: Annotated[float, Field(alias="fontSize")] = 14
    rect_padding: Annotated[float, Field(alias="rect_padding")] = 10
    line_height: Annotated[float, Field(alias="line_height")] = 20
