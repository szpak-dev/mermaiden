from collections.abc import Mapping
from dataclasses import dataclass

from wireup import injectable

from ...domain import CommandPayload, ValidatedCommandPayload
from ..application import DiagramsApplication
from ..domain import DiagramInfo, DiagramModel
from .commands import DiagramCommandCatalog
from .models import DiagramDescription
from .objects import DiagramObjectCatalog


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramCatalog:
    registry: DiagramsApplication
    objects: DiagramObjectCatalog
    commands: DiagramCommandCatalog

    def describe(self, diagram_id: str) -> DiagramDescription:
        info = self.registry.get(diagram_id)
        return DiagramDescription(
            id=info.id,
            name=info.name,
            elements=self.objects.schemas(self.objects.elements(info)),
            relations=self.objects.schemas(self.objects.relations(info)),
            annotations=self.objects.schemas(self.objects.annotations(info)),
            commands={
                name: self.commands.payload(info.id, name).model_json_schema() for name in self.commands.names(info)
            },
        )

    def command_names(self, info: DiagramInfo) -> tuple[str, ...]:
        return self.commands.names(info)

    def command_payload(self, diagram_id: str, command_name: str) -> CommandPayload:
        return self.commands.payload(diagram_id, command_name)

    def validate_command(
        self,
        diagram: DiagramModel,
        command_name: str,
        payload: Mapping[str, object],
    ) -> ValidatedCommandPayload:
        return self.commands.validate(diagram, command_name, payload)
