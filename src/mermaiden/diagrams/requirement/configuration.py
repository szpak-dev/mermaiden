from ..domain import MermaidDiagramConfiguration


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
