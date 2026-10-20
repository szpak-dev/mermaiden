from enum import StrEnum
from typing import Annotated

from pydantic import Field

from ...core.characters import Text
from ..domain import MermaidDiagramConfiguration, OmittableBoolean, OmittableNonNegativeInteger


class StateRenderer(StrEnum):
    DAGRE_D3 = "dagre-d3"
    DAGRE_WRAPPER = "dagre-wrapper"
    ELK = "elk"


class StateDiagramConfiguration(MermaidDiagramConfiguration):
    title_top_margin: Annotated[int, Field(alias="titleTopMargin", ge=0)] = 25
    arrow_marker_absolute: Annotated[
        OmittableBoolean,
        Field(alias="arrowMarkerAbsolute", exclude_if=OmittableBoolean().excludes),
    ] = Field(default_factory=OmittableBoolean)
    divider_margin: Annotated[float, Field(alias="dividerMargin")] = 10
    size_unit: Annotated[float, Field(alias="sizeUnit")] = 5
    padding: Annotated[float, Field(alias="padding")] = 8
    text_height: Annotated[float, Field(alias="textHeight")] = 10
    title_shift: Annotated[float, Field(alias="titleShift")] = -15
    note_margin: Annotated[float, Field(alias="noteMargin")] = 10
    node_spacing: Annotated[
        OmittableNonNegativeInteger,
        Field(alias="nodeSpacing", exclude_if=OmittableNonNegativeInteger().excludes),
    ] = Field(default_factory=OmittableNonNegativeInteger)
    rank_spacing: Annotated[
        OmittableNonNegativeInteger,
        Field(alias="rankSpacing", exclude_if=OmittableNonNegativeInteger().excludes),
    ] = Field(default_factory=OmittableNonNegativeInteger)
    fork_width: Annotated[float, Field(alias="forkWidth")] = 70
    fork_height: Annotated[float, Field(alias="forkHeight")] = 7
    mini_padding: Annotated[float, Field(alias="miniPadding")] = 2
    font_size_factor: Annotated[float, Field(alias="fontSizeFactor")] = 5.02
    font_size: Annotated[float, Field(alias="fontSize")] = 24
    label_height: Annotated[float, Field(alias="labelHeight")] = 16
    edge_length_factor: Annotated[
        str, Field(alias="edgeLengthFactor", pattern=Text.pattern, description=Text.description)
    ] = "20"
    composit_title_size: Annotated[float, Field(alias="compositTitleSize")] = 35
    radius: Annotated[float, Field(alias="radius")] = 5
    default_renderer: Annotated[StateRenderer, Field(alias="defaultRenderer")] = StateRenderer.DAGRE_WRAPPER
