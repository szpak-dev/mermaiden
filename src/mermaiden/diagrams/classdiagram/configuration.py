from enum import StrEnum
from typing import Annotated

from pydantic import Field, InstanceOf
from pydantic.json_schema import SkipJsonSchema

from ..domain import MermaidDiagramConfiguration, Unconfigured


class ClassRenderer(StrEnum):
    DAGRE_D3 = "dagre-d3"
    DAGRE_WRAPPER = "dagre-wrapper"
    ELK = "elk"


class ClassDiagramConfiguration(MermaidDiagramConfiguration):
    title_top_margin: Annotated[int, Field(alias="titleTopMargin", ge=0)] = 25
    arrow_marker_absolute: Annotated[bool, Field(alias="arrowMarkerAbsolute")] = False
    divider_margin: Annotated[float, Field(alias="dividerMargin")] = 10
    padding: Annotated[float, Field(alias="padding")] = 5
    text_height: Annotated[float, Field(alias="textHeight")] = 10
    default_renderer: Annotated[ClassRenderer, Field(alias="defaultRenderer")] = ClassRenderer.DAGRE_WRAPPER
    node_spacing: Annotated[
        Annotated[int, Field(ge=0)] | SkipJsonSchema[InstanceOf[Unconfigured]],
        Field(alias="nodeSpacing", exclude_if=Unconfigured().excludes),
    ] = Field(default_factory=Unconfigured)
    rank_spacing: Annotated[
        Annotated[int, Field(ge=0)] | SkipJsonSchema[InstanceOf[Unconfigured]],
        Field(alias="rankSpacing", exclude_if=Unconfigured().excludes),
    ] = Field(default_factory=Unconfigured)
    diagram_padding: Annotated[int, Field(alias="diagramPadding", ge=0)] = 20
    html_labels: Annotated[bool, Field(alias="htmlLabels")] = False
    hide_empty_members_box: Annotated[bool, Field(alias="hideEmptyMembersBox")] = False
    hierarchical_namespaces: Annotated[bool, Field(alias="hierarchicalNamespaces")] = True
