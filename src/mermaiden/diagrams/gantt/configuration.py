from ..configuration import MermaidDiagramConfiguration


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

    def to_mermaid(self) -> dict[str, object]:
        return {
            "titleTopMargin": self.title_top_margin,
            "barHeight": self.bar_height,
            "topPadding": self.top_padding,
            "rightPadding": self.right_padding,
            "leftPadding": self.left_padding,
            "gridLineStartPadding": self.grid_line_start_padding,
            "fontSize": self.font_size,
            "sectionFontSize": self.section_font_size,
            "numberSectionStyles": self.number_section_styles,
            "axisFormat": self.axis_format,
            "useMaxWidth": self.use_max_width,
            "topAxis": self.top_axis,
            "weekday": self.weekday,
        }
