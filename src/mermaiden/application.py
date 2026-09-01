from collections.abc import Mapping
from dataclasses import dataclass

from wireup import create_sync_container

import mermaiden

from .core.domain import ChangeRejected, ChangeReport, Diagram
from .diagrams.application import DiagramsApplication
from .diagrams.catalog.models import DiagramDescription
from .diagrams.catalog.service import DiagramCatalog
from .diagrams.domain import DiagramInfo, DiagramModel
from .diagrams.services.diagram_factory import DiagramFactory
from .diagrams.services.persistence import DiagramPersistenceApplication
from .domain import CommandPayload, DiagramCommand, UnknownCommand
from .mermaid.application import MermaidApplication
from .mermaid.templates import MermaidTemplateOwnership
from .mermaid.validation import MermaidRenderReport, MermaidRenderValidator
from .mutations.commands.application import DiagramCommandApplication
from .runtime.snapshot import DiagramSnapshot

__all__ = ["Application", "ChangeRejected", "DiagramCommand", "UnknownCommand"]


@dataclass(frozen=True, slots=True)
class Application:
    diagrams: DiagramsApplication
    catalog: DiagramCatalog
    commands: DiagramCommandApplication
    diagram_factory: DiagramFactory
    persistence: DiagramPersistenceApplication
    renderer: MermaidApplication
    render_validator: MermaidRenderValidator
    template_ownership: MermaidTemplateOwnership

    def initialize(self) -> None:
        self.template_ownership.validate()
        self.catalog.validate()

    def available_diagrams(self) -> tuple[DiagramInfo, ...]:
        return self.diagrams.available()

    def diagram_info(self, diagram_id: str) -> DiagramInfo:
        return self.diagrams.get(diagram_id)

    def diagram_description(self, diagram_id: str) -> DiagramDescription:
        return self.catalog.describe(diagram_id)

    def command_payload(
        self,
        diagram_id: str,
        command_name: str,
    ) -> CommandPayload:
        return self.catalog.command_payload(diagram_id, command_name)

    def create_diagram(self, diagram_id: str) -> DiagramModel:
        return self.diagram_factory.create(diagram_id)

    def apply(self, diagram: DiagramModel, command: DiagramCommand) -> ChangeReport | None:
        return self.commands.apply(diagram, command)

    def execute(
        self,
        diagram: DiagramModel,
        operation: str,
        arguments: Mapping[str, object],
    ) -> ChangeReport | None:
        return self.apply(diagram, DiagramCommand(operation, arguments))

    def snapshot(self, diagram: DiagramModel) -> DiagramSnapshot:
        return self.persistence.snapshot(diagram)

    def restore(self, payload: Mapping[str, object]) -> DiagramModel:
        return self.persistence.restore(payload)

    def render(self, diagram: Diagram) -> str:
        report = diagram.validate()
        if not report.can_commit:
            details = "; ".join(item.message for item in report.blocking)
            raise RuntimeError(f"Cannot render invalid diagram '{diagram.kind}': {details}")
        return self.renderer.render(diagram)

    def validate_render(self, diagram: Diagram) -> MermaidRenderReport:
        return self.render_validator.validate(diagram)

    @classmethod
    def create(cls) -> "Application":
        container = create_sync_container(injectables=[mermaiden], config={})
        with container.enter_scope() as scope:
            application = cls(
                diagrams=scope.get(DiagramsApplication),
                catalog=scope.get(DiagramCatalog),
                commands=scope.get(DiagramCommandApplication),
                diagram_factory=scope.get(DiagramFactory),
                persistence=scope.get(DiagramPersistenceApplication),
                renderer=scope.get(MermaidApplication),
                render_validator=scope.get(MermaidRenderValidator),
                template_ownership=scope.get(MermaidTemplateOwnership),
            )
            application.initialize()
            return application
