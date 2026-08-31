from ..domain import MermaidDiagramConfiguration


class GanttConfiguration(MermaidDiagramConfiguration):
    title_top_margin: int = 25
    bar_height: int = 20
    top_padding: int = 50
    right_padding: int = 75
    left_padding: int = 75
    grid_line_start_padding: int = 35
    font_size: int = 11
    section_font_size: int = 11
    number_section_styles: int = 4
    axis_format: str = "%Y-%m-%d"
    use_max_width: bool = True
    top_axis: bool = False
    weekday: str = "sunday"
