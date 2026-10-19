from typing import Annotated

from pydantic import Field

from ..domain import MermaidDiagramConfiguration


class PacketConfiguration(MermaidDiagramConfiguration):
    row_height: Annotated[float, Field(alias="rowHeight", ge=1)] = 32
    bit_width: Annotated[float, Field(alias="bitWidth", ge=1)] = 32
    bits_per_row: Annotated[float, Field(alias="bitsPerRow", ge=1)] = 32
    show_bits: Annotated[bool, Field(alias="showBits")] = True
    padding_x: Annotated[float, Field(alias="paddingX", ge=0)] = 5
    padding_y: Annotated[float, Field(alias="paddingY", ge=0)] = 5
