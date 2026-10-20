from typing import Annotated

from pydantic import Field

from ..domain import MermaidDiagramConfiguration


class IshikawaDiagramConfiguration(MermaidDiagramConfiguration):
    use_max_width: Annotated[bool, Field(alias="useMaxWidth")] = False
    diagram_padding: Annotated[int, Field(alias="diagramPadding", ge=0)] = 20
