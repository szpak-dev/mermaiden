from typing import Annotated

from pydantic import Field

from ..domain import MermaidDiagramConfiguration


class BlockDiagramConfiguration(MermaidDiagramConfiguration):
    padding: Annotated[float, Field(alias="padding", ge=0)] = 8
