from ..configuration import MermaidDiagramConfiguration


class EntityRelationshipDiagramConfiguration(MermaidDiagramConfiguration):
    title_top_margin: int = 25
    diagram_padding: int = 20
    layout_direction: str = "TB"
    min_entity_width: int = 100
    min_entity_height: int = 75
    entity_padding: int = 15
    stroke: str = "gray"
    fill: str = "honeydew"
    use_max_width: bool = True

    def to_mermaid(self) -> dict[str, object]:
        return {
            "titleTopMargin": self.title_top_margin,
            "diagramPadding": self.diagram_padding,
            "layoutDirection": self.layout_direction,
            "minEntityWidth": self.min_entity_width,
            "minEntityHeight": self.min_entity_height,
            "entityPadding": self.entity_padding,
            "stroke": self.stroke,
            "fill": self.fill,
            "useMaxWidth": self.use_max_width,
        }
