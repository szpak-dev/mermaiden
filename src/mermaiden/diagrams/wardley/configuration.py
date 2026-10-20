from typing import Annotated

from pydantic import Field

from ..domain import MermaidDiagramConfiguration


class WardleyDiagramConfiguration(MermaidDiagramConfiguration):
    width: Annotated[float, Field(alias="width", ge=1)] = 900
    height: Annotated[float, Field(alias="height", ge=1)] = 600
    padding: Annotated[float, Field(alias="padding", ge=0)] = 48
    node_radius: Annotated[float, Field(alias="nodeRadius", ge=0)] = 6
    node_label_offset: Annotated[float, Field(alias="nodeLabelOffset", ge=0)] = 8
    axis_font_size: Annotated[float, Field(alias="axisFontSize", ge=0)] = 12
    label_font_size: Annotated[float, Field(alias="labelFontSize", ge=0)] = 10
    show_grid: Annotated[bool, Field(alias="showGrid")] = False
