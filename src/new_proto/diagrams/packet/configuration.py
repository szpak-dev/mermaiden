from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PacketConfiguration:
    row_height: float = 32
    bit_width: float = 32
    bits_per_row: float = 32
    show_bits: bool = True
    padding_x: float = 5
    padding_y: float = 5

    def to_mermaid(self) -> dict[str, object]:
        return {
            "rowHeight": self.row_height,
            "bitWidth": self.bit_width,
            "bitsPerRow": self.bits_per_row,
            "showBits": self.show_bits,
            "paddingX": self.padding_x,
            "paddingY": self.padding_y,
        }
