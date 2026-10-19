from enum import StrEnum
from typing import Annotated

from pydantic import ConfigDict, Field, RootModel

from ...core.characters import OptionalText, Text
from ..domain import MermaidDiagramConfiguration


class JourneyColourPalette(
    RootModel[tuple[Annotated[str, Field(pattern=Text.pattern, description=Text.description)], ...]]
):
    model_config = ConfigDict(frozen=True)


class JourneyMessageAlignment(StrEnum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class JourneyDiagramConfiguration(MermaidDiagramConfiguration):
    diagram_margin_x: Annotated[int, Field(alias="diagramMarginX", ge=0)] = 50
    diagram_margin_y: Annotated[int, Field(alias="diagramMarginY", ge=0)] = 10
    left_margin: Annotated[int, Field(alias="leftMargin", ge=0)] = 150
    max_label_width: Annotated[int, Field(alias="maxLabelWidth")] = 360
    width: Annotated[int, Field(alias="width", ge=0)] = 150
    height: Annotated[int, Field(alias="height", ge=0)] = 50
    box_margin: Annotated[int, Field(alias="boxMargin", ge=0)] = 10
    box_text_margin: Annotated[int, Field(alias="boxTextMargin", ge=0)] = 5
    note_margin: Annotated[int, Field(alias="noteMargin", ge=0)] = 10
    message_margin: Annotated[int, Field(alias="messageMargin", ge=0)] = 35
    message_align: Annotated[JourneyMessageAlignment, Field(alias="messageAlign")] = JourneyMessageAlignment.CENTER
    bottom_margin_adj: Annotated[int, Field(alias="bottomMarginAdj", ge=0)] = 1
    right_angles: Annotated[bool, Field(alias="rightAngles")] = False
    task_font_size: Annotated[
        Annotated[str, Field(pattern=Text.pattern, description=Text.description)] | float, Field(alias="taskFontSize")
    ] = 14
    task_font_family: Annotated[
        str, Field(alias="taskFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    task_margin: Annotated[float, Field(alias="taskMargin")] = 50
    activation_width: Annotated[float, Field(alias="activationWidth")] = 10
    text_placement: Annotated[str, Field(alias="textPlacement", pattern=Text.pattern, description=Text.description)] = (
        "fo"
    )
    actor_colours: Annotated[JourneyColourPalette, Field(alias="actorColours")] = JourneyColourPalette(
        root=("#8FBC8F", "#7CFC00", "#00FFFF", "#20B2AA", "#B0E0E6", "#FFFFE0")
    )
    section_fills: Annotated[JourneyColourPalette, Field(alias="sectionFills")] = JourneyColourPalette(
        root=("#191970", "#8B008B", "#4B0082", "#2F4F4F", "#800000", "#8B4513", "#00008B")
    )
    section_colours: Annotated[JourneyColourPalette, Field(alias="sectionColours")] = JourneyColourPalette(
        root=("#fff",)
    )
    title_color: Annotated[
        str, Field(alias="titleColor", pattern=OptionalText.pattern, description=OptionalText.description)
    ] = ""
    title_font_family: Annotated[
        str, Field(alias="titleFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"trebuchet ms", verdana, arial, sans-serif'
    title_font_size: Annotated[
        str, Field(alias="titleFontSize", pattern=Text.pattern, description=Text.description)
    ] = "4ex"
