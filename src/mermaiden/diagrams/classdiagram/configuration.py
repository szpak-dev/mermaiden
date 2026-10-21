from typing import Annotated

from pydantic import Field

from ..domain import (
    MermaidDiagramConfiguration,
    MermaidLook,
    MermaidLookField,
    MermaidTheme,
    MermaidThemeField,
    OmittableLook,
    OmittableNonNegativeInteger,
    OmittableTheme,
)


class ClassDiagramConfiguration(MermaidDiagramConfiguration):
    theme: MermaidThemeField = OmittableTheme(root=MermaidTheme.REDUX_COLOR)
    look: MermaidLookField = OmittableLook(root=MermaidLook.NEO)
    title_top_margin: Annotated[int, Field(alias="titleTopMargin", ge=0)] = 25
    arrow_marker_absolute: Annotated[bool, Field(alias="arrowMarkerAbsolute")] = False
    divider_margin: Annotated[float, Field(alias="dividerMargin")] = 10
    padding: Annotated[float, Field(alias="padding")] = 5
    text_height: Annotated[float, Field(alias="textHeight")] = 10
    node_spacing: Annotated[
        OmittableNonNegativeInteger,
        Field(alias="nodeSpacing", exclude_if=OmittableNonNegativeInteger().excludes),
    ] = Field(default_factory=OmittableNonNegativeInteger)
    rank_spacing: Annotated[
        OmittableNonNegativeInteger,
        Field(alias="rankSpacing", exclude_if=OmittableNonNegativeInteger().excludes),
    ] = Field(default_factory=OmittableNonNegativeInteger)
    diagram_padding: Annotated[int, Field(alias="diagramPadding", ge=0)] = 20
    html_labels: Annotated[bool, Field(alias="htmlLabels")] = False
    hide_empty_members_box: Annotated[bool, Field(alias="hideEmptyMembersBox")] = False
    hierarchical_namespaces: Annotated[bool, Field(alias="hierarchicalNamespaces")] = True
