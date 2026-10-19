from typing import Annotated

from pydantic import Field

from ..domain import MermaidDiagramConfiguration


class EventModelingDiagramConfiguration(MermaidDiagramConfiguration):
    padding: Annotated[float, Field(alias="padding")] = 30
    row_height: Annotated[float, Field(alias="rowHeight", ge=1)] = 32
