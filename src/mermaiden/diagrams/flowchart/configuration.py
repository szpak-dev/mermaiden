from enum import StrEnum
from typing import Annotated

from pydantic import Field

from ..domain import (
    BooleanOrUnconfigured,
    MermaidConfigurationModel,
    MermaidDiagramConfiguration,
    NonNegativeIntegerOrUnconfigured,
)


class FlowchartSubgraphTitleMargin(MermaidConfigurationModel):
    top: Annotated[
        NonNegativeIntegerOrUnconfigured,
        Field(alias="top", exclude_if=NonNegativeIntegerOrUnconfigured().excludes),
    ] = Field(default_factory=NonNegativeIntegerOrUnconfigured)
    bottom: Annotated[
        NonNegativeIntegerOrUnconfigured,
        Field(alias="bottom", exclude_if=NonNegativeIntegerOrUnconfigured().excludes),
    ] = Field(default_factory=NonNegativeIntegerOrUnconfigured)


class FlowchartCurve(StrEnum):
    BASIS = "basis"
    BUMP_X = "bumpX"
    BUMP_Y = "bumpY"
    CARDINAL = "cardinal"
    CATMULL_ROM = "catmullRom"
    LINEAR = "linear"
    MONOTONE_X = "monotoneX"
    MONOTONE_Y = "monotoneY"
    NATURAL = "natural"
    STEP = "step"
    STEP_AFTER = "stepAfter"
    STEP_BEFORE = "stepBefore"
    ROUNDED = "rounded"


class FlowchartRenderer(StrEnum):
    DAGRE_WRAPPER = "dagre-wrapper"
    ELK = "elk"


class FlowchartDiagramConfiguration(MermaidDiagramConfiguration):
    title_top_margin: Annotated[int, Field(alias="titleTopMargin", ge=0)] = 25
    sub_graph_title_margin: Annotated[FlowchartSubgraphTitleMargin, Field(alias="subGraphTitleMargin")] = (
        FlowchartSubgraphTitleMargin(top=0, bottom=0)
    )
    arrow_marker_absolute: Annotated[
        BooleanOrUnconfigured,
        Field(alias="arrowMarkerAbsolute", exclude_if=BooleanOrUnconfigured().excludes),
    ] = Field(default_factory=BooleanOrUnconfigured)
    diagram_padding: Annotated[int, Field(alias="diagramPadding", ge=0)] = 8
    node_spacing: Annotated[int, Field(alias="nodeSpacing", ge=0)] = 50
    rank_spacing: Annotated[int, Field(alias="rankSpacing", ge=0)] = 50
    curve: Annotated[FlowchartCurve, Field(alias="curve")] = FlowchartCurve.BASIS
    padding: Annotated[float, Field(alias="padding")] = 15
    default_renderer: Annotated[FlowchartRenderer, Field(alias="defaultRenderer")] = FlowchartRenderer.DAGRE_WRAPPER
    wrapping_width: Annotated[float, Field(alias="wrappingWidth")] = 200
    inherit_dir: Annotated[bool, Field(alias="inheritDir")] = False
