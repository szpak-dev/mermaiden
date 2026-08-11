from enum import StrEnum

from ..configuration import MermaidDiagramConfiguration


class StateRenderer(StrEnum):
    DAGRE_D3 = "dagre-d3"
    DAGRE_WRAPPER = "dagre-wrapper"
    ELK = "elk"


class StateDiagramConfiguration(MermaidDiagramConfiguration):
    title_top_margin: int = 25
    use_max_width: bool = True
    default_renderer: StateRenderer = StateRenderer.DAGRE_WRAPPER
