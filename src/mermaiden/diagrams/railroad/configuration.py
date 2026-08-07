from ..configuration import MermaidDiagramConfiguration


class RailroadDiagramConfiguration(MermaidDiagramConfiguration):
    compact_mode: bool = False
    padding: float = 10
    vertical_separation: float = 8
    horizontal_separation: float = 10
    arc_radius: float = 10
    font_size: float = 14
    font_family: str = "monospace"

    def to_mermaid(self) -> dict[str, object]:
        return {
            "compactMode": self.compact_mode,
            "padding": self.padding,
            "verticalSeparation": self.vertical_separation,
            "horizontalSeparation": self.horizontal_separation,
            "arcRadius": self.arc_radius,
            "fontSize": self.font_size,
            "fontFamily": self.font_family,
        }
