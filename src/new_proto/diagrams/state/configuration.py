from dataclasses import dataclass
from enum import StrEnum


class StateRenderer(StrEnum):
    DAGRE_D3 = "dagre-d3"
    DAGRE_WRAPPER = "dagre-wrapper"
    ELK = "elk"


@dataclass(frozen=True, slots=True)
class StateDiagramConfiguration:
    title_top_margin: int = 25
    use_max_width: bool = True
    default_renderer: StateRenderer = StateRenderer.DAGRE_WRAPPER

    def to_mermaid(self) -> dict[str, object]:
        return {
            "titleTopMargin": self.title_top_margin,
            "useMaxWidth": self.use_max_width,
            "defaultRenderer": self.default_renderer,
        }
