from ..configuration import MermaidDiagramConfiguration


class VennConfiguration(MermaidDiagramConfiguration):
    width: float = 800
    height: float = 450
    padding: float = 8
    use_debug_layout: bool = False

    def to_mermaid(self) -> dict[str, object]:
        return {
            "width": self.width,
            "height": self.height,
            "padding": self.padding,
            "useDebugLayout": self.use_debug_layout,
        }
