from ..configuration import MermaidDiagramConfiguration


class KanbanDiagramConfiguration(MermaidDiagramConfiguration):
    padding: float = 8
    section_width: float = 200
    ticket_base_url: str = ""
