from typing import Annotated

from pydantic import Field

from ..domain import MermaidDiagramConfiguration


class CynefinDiagramConfiguration(MermaidDiagramConfiguration):
    width: Annotated[float, Field(alias="width", ge=1)] = 800
    height: Annotated[float, Field(alias="height", ge=1)] = 600
    padding: Annotated[float, Field(alias="padding", ge=0)] = 40
    show_domain_descriptions: Annotated[bool, Field(alias="showDomainDescriptions")] = True
    boundary_amplitude: Annotated[float, Field(alias="boundaryAmplitude", ge=0, le=50)] = 8
    seed: Annotated[float, Field(alias="seed")] = 1
