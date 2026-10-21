from enum import StrEnum
from typing import Annotated

from pydantic import ConfigDict, Field

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


class EntityRelationshipDirection(StrEnum):
    TOP_BOTTOM = "TB"
    BOTTOM_TOP = "BT"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"


class EntityRelationshipDiagramConfiguration(MermaidDiagramConfiguration):
    model_config = ConfigDict(use_enum_values=True)

    theme: MermaidThemeField = OmittableTheme(root=MermaidTheme.REDUX_COLOR)
    look: MermaidLookField = OmittableLook(root=MermaidLook.NEO)
    title_top_margin: Annotated[int, Field(alias="titleTopMargin", ge=0)] = 25
    diagram_padding: Annotated[int, Field(alias="diagramPadding", ge=0)] = 20
    layout_direction: Annotated[EntityRelationshipDirection, Field(alias="layoutDirection")] = (
        EntityRelationshipDirection.TOP_BOTTOM
    )
    min_entity_width: Annotated[int, Field(alias="minEntityWidth", ge=0)] = 100
    min_entity_height: Annotated[int, Field(alias="minEntityHeight", ge=0)] = 75
    entity_padding: Annotated[int, Field(alias="entityPadding", ge=0)] = 15
    node_spacing: Annotated[int, Field(alias="nodeSpacing", ge=0)] = 140
    rank_spacing: Annotated[int, Field(alias="rankSpacing", ge=0)] = 80
    stroke: Annotated[str, Field(alias="stroke", pattern=Text.pattern, description=Text.description)] = "gray"
    fill: Annotated[str, Field(alias="fill", pattern=Text.pattern, description=Text.description)] = "honeydew"
    font_size: Annotated[int, Field(alias="fontSize", ge=0)] = 12
