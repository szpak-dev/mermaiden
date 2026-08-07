from ..configuration import MermaidDiagramConfiguration


class KanbanDiagramConfiguration(MermaidDiagramConfiguration):
    padding: float = 8
    section_width: float = 200
    ticket_base_url: str = ""

    def to_mermaid(self) -> dict[str, object]:
        return {
            "padding": self.padding,
            "sectionWidth": self.section_width,
            "ticketBaseUrl": self.ticket_base_url,
        }
