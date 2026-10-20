from typing import Annotated

from pydantic import Field

from ..domain import MermaidDiagramConfiguration


class RadarConfiguration(MermaidDiagramConfiguration):
    width: Annotated[float, Field(alias="width", ge=1)] = 600
    height: Annotated[float, Field(alias="height", ge=1)] = 600
    margin_top: Annotated[float, Field(alias="marginTop", ge=0)] = 50
    margin_right: Annotated[float, Field(alias="marginRight", ge=0)] = 50
    margin_bottom: Annotated[float, Field(alias="marginBottom", ge=0)] = 50
    margin_left: Annotated[float, Field(alias="marginLeft", ge=0)] = 50
    axis_scale_factor: Annotated[float, Field(alias="axisScaleFactor", ge=0)] = 1
    axis_label_factor: Annotated[float, Field(alias="axisLabelFactor", ge=0)] = 1.05
    curve_tension: Annotated[float, Field(alias="curveTension", ge=0, le=1)] = 0.17
