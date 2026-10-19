from typing import Annotated

from pydantic import Field

from ...core.characters import Text
from ..domain import MermaidDiagramConfiguration


class RailroadDiagramConfiguration(MermaidDiagramConfiguration):
    compact_mode: Annotated[bool, Field(alias="compactMode")] = False
    padding: Annotated[float, Field(alias="padding", ge=0)] = 10
    vertical_separation: Annotated[float, Field(alias="verticalSeparation", ge=0)] = 8
    horizontal_separation: Annotated[float, Field(alias="horizontalSeparation", ge=0)] = 10
    arc_radius: Annotated[float, Field(alias="arcRadius", ge=0)] = 10
    font_size: Annotated[float, Field(alias="fontSize", ge=0)] = 14
    font_family: Annotated[str, Field(alias="fontFamily", pattern=Text.pattern, description=Text.description)] = (
        "monospace"
    )
    terminal_fill: Annotated[str, Field(alias="terminalFill", pattern=Text.pattern, description=Text.description)] = (
        "#FFFFC0"
    )
    terminal_stroke: Annotated[
        str, Field(alias="terminalStroke", pattern=Text.pattern, description=Text.description)
    ] = "#000000"
    terminal_text_color: Annotated[
        str, Field(alias="terminalTextColor", pattern=Text.pattern, description=Text.description)
    ] = "#000000"
    non_terminal_fill: Annotated[
        str, Field(alias="nonTerminalFill", pattern=Text.pattern, description=Text.description)
    ] = "#FFFFFF"
    non_terminal_stroke: Annotated[
        str, Field(alias="nonTerminalStroke", pattern=Text.pattern, description=Text.description)
    ] = "#000000"
    non_terminal_text_color: Annotated[
        str, Field(alias="nonTerminalTextColor", pattern=Text.pattern, description=Text.description)
    ] = "#000000"
    line_color: Annotated[str, Field(alias="lineColor", pattern=Text.pattern, description=Text.description)] = "#000000"
    stroke_width: Annotated[float, Field(alias="strokeWidth", ge=0)] = 2
    marker_fill: Annotated[str, Field(alias="markerFill", pattern=Text.pattern, description=Text.description)] = (
        "#000000"
    )
    comment_fill: Annotated[str, Field(alias="commentFill", pattern=Text.pattern, description=Text.description)] = (
        "#E8E8E8"
    )
    comment_stroke: Annotated[str, Field(alias="commentStroke", pattern=Text.pattern, description=Text.description)] = (
        "#888888"
    )
    comment_text_color: Annotated[
        str, Field(alias="commentTextColor", pattern=Text.pattern, description=Text.description)
    ] = "#666666"
    special_fill: Annotated[str, Field(alias="specialFill", pattern=Text.pattern, description=Text.description)] = (
        "#F0E0FF"
    )
    special_stroke: Annotated[str, Field(alias="specialStroke", pattern=Text.pattern, description=Text.description)] = (
        "#8800CC"
    )
    rule_name_color: Annotated[
        str, Field(alias="ruleNameColor", pattern=Text.pattern, description=Text.description)
    ] = "#000066"
    show_markers: Annotated[bool, Field(alias="showMarkers")] = True
    marker_radius: Annotated[float, Field(alias="markerRadius", ge=0)] = 5
