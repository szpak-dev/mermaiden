from typing import Annotated

from pydantic import Field

from ...core.characters import NumberOrText, PositiveNumberOrNumericText, Text
from ..domain import MermaidDiagramConfiguration


class C4ContextDiagramConfiguration(MermaidDiagramConfiguration):
    diagram_margin_x: Annotated[int, Field(alias="diagramMarginX", ge=0)] = 50
    diagram_margin_y: Annotated[int, Field(alias="diagramMarginY", ge=0)] = 10
    c4_shape_margin: Annotated[int, Field(alias="c4ShapeMargin", ge=0)] = 50
    c4_shape_padding: Annotated[int, Field(alias="c4ShapePadding", ge=0)] = 20
    width: Annotated[int, Field(alias="width", ge=0)] = 216
    height: Annotated[int, Field(alias="height", ge=0)] = 60
    box_margin: Annotated[int, Field(alias="boxMargin", ge=0)] = 10
    c4_shape_in_row: Annotated[int, Field(alias="c4ShapeInRow", ge=0)] = 4
    next_line_padding_x: Annotated[float, Field(alias="nextLinePaddingX")] = 0
    c4_boundary_in_row: Annotated[int, Field(alias="c4BoundaryInRow", ge=0)] = 2
    person_font_size: Annotated[
        NumberOrText, Field(alias="personFontSize")
    ] = 14
    person_font_family: Annotated[
        str, Field(alias="personFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    person_font_weight: Annotated[
        NumberOrText,
        Field(alias="personFontWeight"),
    ] = "normal"
    external_person_font_size: Annotated[
        NumberOrText,
        Field(alias="external_personFontSize"),
    ] = 14
    external_person_font_family: Annotated[
        str, Field(alias="external_personFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    external_person_font_weight: Annotated[
        NumberOrText,
        Field(alias="external_personFontWeight"),
    ] = "normal"
    system_font_size: Annotated[
        NumberOrText, Field(alias="systemFontSize")
    ] = 14
    system_font_family: Annotated[
        str, Field(alias="systemFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    system_font_weight: Annotated[
        NumberOrText,
        Field(alias="systemFontWeight"),
    ] = "normal"
    external_system_font_size: Annotated[
        NumberOrText,
        Field(alias="external_systemFontSize"),
    ] = 14
    external_system_font_family: Annotated[
        str, Field(alias="external_systemFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    external_system_font_weight: Annotated[
        NumberOrText,
        Field(alias="external_systemFontWeight"),
    ] = "normal"
    system_db_font_size: Annotated[
        NumberOrText,
        Field(alias="system_dbFontSize"),
    ] = 14
    system_db_font_family: Annotated[
        str, Field(alias="system_dbFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    system_db_font_weight: Annotated[
        NumberOrText,
        Field(alias="system_dbFontWeight"),
    ] = "normal"
    external_system_db_font_size: Annotated[
        NumberOrText,
        Field(alias="external_system_dbFontSize"),
    ] = 14
    external_system_db_font_family: Annotated[
        str, Field(alias="external_system_dbFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    external_system_db_font_weight: Annotated[
        NumberOrText,
        Field(alias="external_system_dbFontWeight"),
    ] = "normal"
    system_queue_font_size: Annotated[
        NumberOrText,
        Field(alias="system_queueFontSize"),
    ] = 14
    system_queue_font_family: Annotated[
        str, Field(alias="system_queueFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    system_queue_font_weight: Annotated[
        NumberOrText,
        Field(alias="system_queueFontWeight"),
    ] = "normal"
    external_system_queue_font_size: Annotated[
        NumberOrText,
        Field(alias="external_system_queueFontSize"),
    ] = 14
    external_system_queue_font_family: Annotated[
        str, Field(alias="external_system_queueFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    external_system_queue_font_weight: Annotated[
        NumberOrText,
        Field(alias="external_system_queueFontWeight"),
    ] = "normal"
    boundary_font_size: Annotated[
        PositiveNumberOrNumericText, Field(alias="boundaryFontSize")
    ] = PositiveNumberOrNumericText(root=14)
    boundary_font_family: Annotated[
        str, Field(alias="boundaryFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    boundary_font_weight: Annotated[
        NumberOrText,
        Field(alias="boundaryFontWeight"),
    ] = "normal"
    message_font_size: Annotated[
        PositiveNumberOrNumericText, Field(alias="messageFontSize")
    ] = PositiveNumberOrNumericText(root=12)
    message_font_family: Annotated[
        str, Field(alias="messageFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    message_font_weight: Annotated[
        NumberOrText,
        Field(alias="messageFontWeight"),
    ] = "normal"
    container_font_size: Annotated[
        NumberOrText,
        Field(alias="containerFontSize"),
    ] = 14
    container_font_family: Annotated[
        str, Field(alias="containerFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    container_font_weight: Annotated[
        NumberOrText,
        Field(alias="containerFontWeight"),
    ] = "normal"
    external_container_font_size: Annotated[
        NumberOrText,
        Field(alias="external_containerFontSize"),
    ] = 14
    external_container_font_family: Annotated[
        str, Field(alias="external_containerFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    external_container_font_weight: Annotated[
        NumberOrText,
        Field(alias="external_containerFontWeight"),
    ] = "normal"
    container_db_font_size: Annotated[
        NumberOrText,
        Field(alias="container_dbFontSize"),
    ] = 14
    container_db_font_family: Annotated[
        str, Field(alias="container_dbFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    container_db_font_weight: Annotated[
        NumberOrText,
        Field(alias="container_dbFontWeight"),
    ] = "normal"
    external_container_db_font_size: Annotated[
        NumberOrText,
        Field(alias="external_container_dbFontSize"),
    ] = 14
    external_container_db_font_family: Annotated[
        str, Field(alias="external_container_dbFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    external_container_db_font_weight: Annotated[
        NumberOrText,
        Field(alias="external_container_dbFontWeight"),
    ] = "normal"
    container_queue_font_size: Annotated[
        NumberOrText,
        Field(alias="container_queueFontSize"),
    ] = 14
    container_queue_font_family: Annotated[
        str, Field(alias="container_queueFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    container_queue_font_weight: Annotated[
        NumberOrText,
        Field(alias="container_queueFontWeight"),
    ] = "normal"
    external_container_queue_font_size: Annotated[
        NumberOrText,
        Field(alias="external_container_queueFontSize"),
    ] = 14
    external_container_queue_font_family: Annotated[
        str, Field(alias="external_container_queueFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    external_container_queue_font_weight: Annotated[
        NumberOrText,
        Field(alias="external_container_queueFontWeight"),
    ] = "normal"
    component_font_size: Annotated[
        NumberOrText,
        Field(alias="componentFontSize"),
    ] = 14
    component_font_family: Annotated[
        str, Field(alias="componentFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    component_font_weight: Annotated[
        NumberOrText,
        Field(alias="componentFontWeight"),
    ] = "normal"
    external_component_font_size: Annotated[
        NumberOrText,
        Field(alias="external_componentFontSize"),
    ] = 14
    external_component_font_family: Annotated[
        str, Field(alias="external_componentFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    external_component_font_weight: Annotated[
        NumberOrText,
        Field(alias="external_componentFontWeight"),
    ] = "normal"
    component_db_font_size: Annotated[
        NumberOrText,
        Field(alias="component_dbFontSize"),
    ] = 14
    component_db_font_family: Annotated[
        str, Field(alias="component_dbFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    component_db_font_weight: Annotated[
        NumberOrText,
        Field(alias="component_dbFontWeight"),
    ] = "normal"
    external_component_db_font_size: Annotated[
        NumberOrText,
        Field(alias="external_component_dbFontSize"),
    ] = 14
    external_component_db_font_family: Annotated[
        str, Field(alias="external_component_dbFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    external_component_db_font_weight: Annotated[
        NumberOrText,
        Field(alias="external_component_dbFontWeight"),
    ] = "normal"
    component_queue_font_size: Annotated[
        NumberOrText,
        Field(alias="component_queueFontSize"),
    ] = 14
    component_queue_font_family: Annotated[
        str, Field(alias="component_queueFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    component_queue_font_weight: Annotated[
        NumberOrText,
        Field(alias="component_queueFontWeight"),
    ] = "normal"
    external_component_queue_font_size: Annotated[
        NumberOrText,
        Field(alias="external_component_queueFontSize"),
    ] = 14
    external_component_queue_font_family: Annotated[
        str, Field(alias="external_component_queueFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    external_component_queue_font_weight: Annotated[
        NumberOrText,
        Field(alias="external_component_queueFontWeight"),
    ] = "normal"
    wrap_padding: Annotated[float, Field(alias="wrapPadding")] = 10
    person_bg_color: Annotated[
        str, Field(alias="person_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#08427B"
    person_border_color: Annotated[
        str, Field(alias="person_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#073B6F"
    external_person_bg_color: Annotated[
        str, Field(alias="external_person_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#686868"
    external_person_border_color: Annotated[
        str, Field(alias="external_person_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#8A8A8A"
    system_bg_color: Annotated[
        str, Field(alias="system_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#1168BD"
    system_border_color: Annotated[
        str, Field(alias="system_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#3C7FC0"
    system_db_bg_color: Annotated[
        str, Field(alias="system_db_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#1168BD"
    system_db_border_color: Annotated[
        str, Field(alias="system_db_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#3C7FC0"
    system_queue_bg_color: Annotated[
        str, Field(alias="system_queue_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#1168BD"
    system_queue_border_color: Annotated[
        str, Field(alias="system_queue_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#3C7FC0"
    external_system_bg_color: Annotated[
        str, Field(alias="external_system_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#999999"
    external_system_border_color: Annotated[
        str, Field(alias="external_system_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#8A8A8A"
    external_system_db_bg_color: Annotated[
        str, Field(alias="external_system_db_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#999999"
    external_system_db_border_color: Annotated[
        str, Field(alias="external_system_db_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#8A8A8A"
    external_system_queue_bg_color: Annotated[
        str, Field(alias="external_system_queue_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#999999"
    external_system_queue_border_color: Annotated[
        str, Field(alias="external_system_queue_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#8A8A8A"
    container_bg_color: Annotated[
        str, Field(alias="container_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#438DD5"
    container_border_color: Annotated[
        str, Field(alias="container_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#3C7FC0"
    container_db_bg_color: Annotated[
        str, Field(alias="container_db_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#438DD5"
    container_db_border_color: Annotated[
        str, Field(alias="container_db_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#3C7FC0"
    container_queue_bg_color: Annotated[
        str, Field(alias="container_queue_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#438DD5"
    container_queue_border_color: Annotated[
        str, Field(alias="container_queue_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#3C7FC0"
    external_container_bg_color: Annotated[
        str, Field(alias="external_container_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#B3B3B3"
    external_container_border_color: Annotated[
        str, Field(alias="external_container_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#A6A6A6"
    external_container_db_bg_color: Annotated[
        str, Field(alias="external_container_db_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#B3B3B3"
    external_container_db_border_color: Annotated[
        str, Field(alias="external_container_db_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#A6A6A6"
    external_container_queue_bg_color: Annotated[
        str, Field(alias="external_container_queue_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#B3B3B3"
    external_container_queue_border_color: Annotated[
        str, Field(alias="external_container_queue_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#A6A6A6"
    component_bg_color: Annotated[
        str, Field(alias="component_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#85BBF0"
    component_border_color: Annotated[
        str, Field(alias="component_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#78A8D8"
    component_db_bg_color: Annotated[
        str, Field(alias="component_db_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#85BBF0"
    component_db_border_color: Annotated[
        str, Field(alias="component_db_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#78A8D8"
    component_queue_bg_color: Annotated[
        str, Field(alias="component_queue_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#85BBF0"
    component_queue_border_color: Annotated[
        str, Field(alias="component_queue_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#78A8D8"
    external_component_bg_color: Annotated[
        str, Field(alias="external_component_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#CCCCCC"
    external_component_border_color: Annotated[
        str, Field(alias="external_component_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#BFBFBF"
    external_component_db_bg_color: Annotated[
        str, Field(alias="external_component_db_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#CCCCCC"
    external_component_db_border_color: Annotated[
        str, Field(alias="external_component_db_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#BFBFBF"
    external_component_queue_bg_color: Annotated[
        str, Field(alias="external_component_queue_bg_color", pattern=Text.pattern, description=Text.description)
    ] = "#CCCCCC"
    external_component_queue_border_color: Annotated[
        str, Field(alias="external_component_queue_border_color", pattern=Text.pattern, description=Text.description)
    ] = "#BFBFBF"
