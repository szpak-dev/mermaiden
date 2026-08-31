from ..domain import MermaidDiagramConfiguration


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
