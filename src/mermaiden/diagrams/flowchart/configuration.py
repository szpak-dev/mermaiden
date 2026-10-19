from enum import StrEnum
from typing import Annotated

from pydantic import Field, InstanceOf
from pydantic.json_schema import SkipJsonSchema

from ..domain import MermaidConfigurationModel, MermaidDiagramConfiguration, Unconfigured


class FlowchartSubgraphTitleMargin(MermaidConfigurationModel):
    top: Annotated[
        Annotated[int, Field(ge=0)] | SkipJsonSchema[InstanceOf[Unconfigured]],
        Field(alias="top", exclude_if=Unconfigured().excludes),
    ] = Field(default_factory=Unconfigured)
    bottom: Annotated[
        Annotated[int, Field(ge=0)] | SkipJsonSchema[InstanceOf[Unconfigured]],
        Field(alias="bottom", exclude_if=Unconfigured().excludes),
    ] = Field(default_factory=Unconfigured)


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
    DAGRE_D3 = "dagre-d3"
    DAGRE_WRAPPER = "dagre-wrapper"
    ELK = "elk"


class FlowchartDiagramConfiguration(MermaidDiagramConfiguration):
    title_top_margin: Annotated[int, Field(alias="titleTopMargin", ge=0)] = 25
    sub_graph_title_margin: Annotated[FlowchartSubgraphTitleMargin, Field(alias="subGraphTitleMargin")] = (
        FlowchartSubgraphTitleMargin(top=0, bottom=0)
    )
    arrow_marker_absolute: Annotated[
        bool | SkipJsonSchema[InstanceOf[Unconfigured]],
        Field(alias="arrowMarkerAbsolute", exclude_if=Unconfigured().excludes),
    ] = Field(default_factory=Unconfigured)
    diagram_padding: Annotated[int, Field(alias="diagramPadding", ge=0)] = 8
    node_spacing: Annotated[int, Field(alias="nodeSpacing", ge=0)] = 50
    rank_spacing: Annotated[int, Field(alias="rankSpacing", ge=0)] = 50
    curve: Annotated[FlowchartCurve, Field(alias="curve")] = FlowchartCurve.BASIS
    padding: Annotated[float, Field(alias="padding")] = 15
    default_renderer: Annotated[FlowchartRenderer, Field(alias="defaultRenderer")] = FlowchartRenderer.DAGRE_WRAPPER
    wrapping_width: Annotated[float, Field(alias="wrappingWidth")] = 200
    inherit_dir: Annotated[bool, Field(alias="inheritDir")] = False
