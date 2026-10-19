from typing import Annotated

from pydantic import Field

from ...core.characters import OptionalText
from ..domain import MermaidDiagramConfiguration


class KanbanDiagramConfiguration(MermaidDiagramConfiguration):
    padding: Annotated[float, Field(alias="padding")] = 8
    section_width: Annotated[float, Field(alias="sectionWidth")] = 200
    ticket_base_url: Annotated[
        str, Field(alias="ticketBaseUrl", pattern=OptionalText.pattern, description=OptionalText.description)
    ] = ""
