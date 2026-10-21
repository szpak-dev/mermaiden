from enum import StrEnum
from typing import Annotated

from pydantic import Field

from ...core.characters import NumberOrText, Text
from ..domain import (
    MermaidDiagramConfiguration,
    MermaidLook,
    MermaidLookField,
    MermaidTheme,
    MermaidThemeField,
    OmittableBoolean,
    OmittableLook,
    OmittableTheme,
)


class SequenceMessageAlignment(StrEnum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class SequenceNoteAlignment(StrEnum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class SequenceDiagramConfiguration(MermaidDiagramConfiguration):
    theme: MermaidThemeField = OmittableTheme(root=MermaidTheme.REDUX_COLOR)
    look: MermaidLookField = OmittableLook(root=MermaidLook.NEO)
    arrow_marker_absolute: Annotated[
        OmittableBoolean,
        Field(alias="arrowMarkerAbsolute", exclude_if=OmittableBoolean().excludes),
    ] = Field(default_factory=OmittableBoolean)
    hide_unused_participants: Annotated[bool, Field(alias="hideUnusedParticipants")] = False
    activation_width: Annotated[int, Field(alias="activationWidth", ge=0)] = 10
    diagram_margin_x: Annotated[int, Field(alias="diagramMarginX", ge=0)] = 50
    diagram_margin_y: Annotated[int, Field(alias="diagramMarginY", ge=0)] = 10
    actor_margin: Annotated[int, Field(alias="actorMargin", ge=0)] = 50
    width: Annotated[int, Field(alias="width", ge=0)] = 150
    height: Annotated[int, Field(alias="height", ge=0)] = 65
    box_margin: Annotated[int, Field(alias="boxMargin", ge=0)] = 10
    box_text_margin: Annotated[int, Field(alias="boxTextMargin", ge=0)] = 5
    note_margin: Annotated[int, Field(alias="noteMargin", ge=0)] = 10
    message_margin: Annotated[int, Field(alias="messageMargin", ge=0)] = 35
    message_align: Annotated[SequenceMessageAlignment, Field(alias="messageAlign")] = SequenceMessageAlignment.CENTER
    mirror_actors: Annotated[bool, Field(alias="mirrorActors")] = True
    force_menus: Annotated[bool, Field(alias="forceMenus")] = False
    bottom_margin_adj: Annotated[int, Field(alias="bottomMarginAdj", ge=0)] = 1
    right_angles: Annotated[bool, Field(alias="rightAngles")] = False
    show_sequence_numbers: Annotated[bool, Field(alias="showSequenceNumbers")] = False
    actor_font_size: Annotated[NumberOrText, Field(alias="actorFontSize")] = NumberOrText(root=14)
    actor_font_family: Annotated[
        str, Field(alias="actorFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"Open Sans", sans-serif'
    actor_font_weight: Annotated[
        NumberOrText,
        Field(alias="actorFontWeight"),
    ] = NumberOrText(root=400)
    note_font_size: Annotated[NumberOrText, Field(alias="noteFontSize")] = NumberOrText(root=14)
    note_font_family: Annotated[
        str, Field(alias="noteFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"trebuchet ms", verdana, arial, sans-serif'
    note_font_weight: Annotated[NumberOrText, Field(alias="noteFontWeight")] = NumberOrText(root=400)
    note_align: Annotated[SequenceNoteAlignment, Field(alias="noteAlign")] = SequenceNoteAlignment.CENTER
    message_font_size: Annotated[
        NumberOrText,
        Field(alias="messageFontSize"),
    ] = NumberOrText(root=16)
    message_font_family: Annotated[
        str, Field(alias="messageFontFamily", pattern=Text.pattern, description=Text.description)
    ] = '"trebuchet ms", verdana, arial, sans-serif'
    message_font_weight: Annotated[
        NumberOrText,
        Field(alias="messageFontWeight"),
    ] = NumberOrText(root=400)
    wrap_padding: Annotated[float, Field(alias="wrapPadding")] = 10
    label_box_width: Annotated[float, Field(alias="labelBoxWidth")] = 50
    label_box_height: Annotated[float, Field(alias="labelBoxHeight")] = 20
