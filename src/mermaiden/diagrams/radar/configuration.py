from ..configuration import MermaidDiagramConfiguration


class RadarConfiguration(MermaidDiagramConfiguration):
    width: float = 600
    height: float = 600
    margin_top: float = 50
    margin_right: float = 50
    margin_bottom: float = 50
    margin_left: float = 50
    axis_scale_factor: float = 1
    axis_label_factor: float = 1.05
    curve_tension: float = 0.17

    def to_mermaid(self) -> dict[str, object]:
        return {
            "width": self.width,
            "height": self.height,
            "marginTop": self.margin_top,
            "marginRight": self.margin_right,
            "marginBottom": self.margin_bottom,
            "marginLeft": self.margin_left,
            "axisScaleFactor": self.axis_scale_factor,
            "axisLabelFactor": self.axis_label_factor,
            "curveTension": self.curve_tension,
        }
