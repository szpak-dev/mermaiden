from ..configuration import MermaidDiagramConfiguration


class RequirementDiagramConfiguration(MermaidDiagramConfiguration):
    use_max_width: bool = True
    rect_fill: str = "#f9f9f9"
    text_color: str = "#333"
    rect_border_size: str = "0.5px"
    rect_border_color: str = "#bbb"
    rect_min_width: int = 200
    rect_min_height: int = 200
    font_size: int = 14
    rect_padding: int = 10
    line_height: int = 20

    def to_mermaid(self) -> dict[str, object]:
        return {
            "useMaxWidth": self.use_max_width,
            "rect_fill": self.rect_fill,
            "text_color": self.text_color,
            "rect_border_size": self.rect_border_size,
            "rect_border_color": self.rect_border_color,
            "rect_min_width": self.rect_min_width,
            "rect_min_height": self.rect_min_height,
            "fontSize": self.font_size,
            "rect_padding": self.rect_padding,
            "line_height": self.line_height,
        }
