from typing import Annotated

from pydantic import Field

from ..configuration import MermaidDiagramConfiguration


class C4ContextDiagramConfiguration(MermaidDiagramConfiguration):
    diagram_margin_x: int = Field(default=50, ge=0)
    diagram_margin_y: int = Field(default=10, ge=0)
    c4_shape_margin: int = Field(default=50, ge=0)
    c4_shape_padding: int = Field(default=20, ge=0)
    width: int = Field(default=216, ge=0)
    height: int = Field(default=60, ge=0)
    box_margin: int = Field(default=10, ge=0)
    use_max_width: bool = True
    c4_shape_in_row: int = Field(default=4, ge=0)
    next_line_padding_x: float = 0
    c4_boundary_in_row: int = Field(default=2, ge=0)
    message_font_size: Annotated[float, Field(gt=0)] | Annotated[str, Field(min_length=1)] = 12
