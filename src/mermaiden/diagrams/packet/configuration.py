from ..configuration import MermaidDiagramConfiguration


class PacketConfiguration(MermaidDiagramConfiguration):
    row_height: float = 32
    bit_width: float = 32
    bits_per_row: float = 32
    show_bits: bool = True
    padding_x: float = 5
    padding_y: float = 5
