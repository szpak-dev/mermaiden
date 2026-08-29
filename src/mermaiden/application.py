from collections.abc import Callable, Mapping
from dataclasses import dataclass
from inspect import signature

from wireup import create_sync_container, injectable

import mermaiden

from .core.constraint import ChangeReport
from .core.diagram import Diagram
from .diagrams.application import DiagramFactory, DiagramInfo, DiagramPersistenceApplication, DiagramsApplication
from .diagrams.catalog.models import DiagramDescription
from .diagrams.catalog.service import DiagramCatalog
from .diagrams.configuration import MermaidDiagramConfiguration
from .diagrams.domain import DiagramModel
from .domain import CommandPayload, ValidatedCommandPayload
from .mermaid.application import MermaidApplication
from .mermaid.templates import MermaidTemplateOwnership
from .mermaid.validation import MermaidRenderReport, MermaidRenderValidator
from .runtime.snapshot import DiagramSnapshot


class ApplicationError(RuntimeError):
    pass


class UnknownCommand(ApplicationError):
    pass


@dataclass(frozen=True, slots=True)
class DiagramCommand:
    operation: str
    arguments: Mapping[str, object]


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Application:
    diagrams: DiagramsApplication
    catalog: DiagramCatalog
    diagram_factory: DiagramFactory
    persistence: DiagramPersistenceApplication
    renderer: MermaidApplication
    render_validator: MermaidRenderValidator
    template_ownership: MermaidTemplateOwnership

    def initialize(self) -> None:
        self.template_ownership.validate()

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
        operation = getattr(diagram, command.operation, None)
        if command.operation.startswith("_") or not callable(operation):
            raise UnknownCommand(f"Command '{command.operation}' is not supported for '{diagram.kind}'.")
        try:
            payload = self.catalog.validate_command(diagram, command.operation, command.arguments)
        except (KeyError, ValueError) as error:
            raise UnknownCommand(f"Command '{command.operation}' has invalid arguments.") from error
        if isinstance(payload, MermaidDiagramConfiguration):
            diagram.configure(payload)
            return None
        return self._invoke(operation, payload)

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
        return self.renderer.render(diagram)

    def validate_render(self, diagram: Diagram) -> MermaidRenderReport:
        return self.render_validator.validate(diagram)

    def _invoke(
        self,
        operation: Callable[..., object],
        payload: ValidatedCommandPayload,
    ) -> ChangeReport | None:
        parameters = tuple(signature(operation).parameters.values())
        values = payload.model_dump(exclude_unset=True)
        variadic = next((item for item in parameters if item.kind is item.VAR_POSITIONAL), None)
        positional = ()
        if variadic is not None:
            variadic_values = values.pop(variadic.name)
            if not isinstance(variadic_values, tuple):
                raise UnknownCommand("Variadic command arguments must be a tuple.")
            positional = (
                tuple(
                    values.pop(item.name)
                    for item in parameters
                    if item.kind in {item.POSITIONAL_ONLY, item.POSITIONAL_OR_KEYWORD}
                )
                + variadic_values
            )
        result = operation(*positional, **values)
        if result is not None and not isinstance(result, ChangeReport):
            raise UnknownCommand("Command is not a mutation.")
        return result

    @classmethod
    def create(cls) -> "Application":
        container = create_sync_container(injectables=[mermaiden], config={})
        with container.enter_scope() as scope:
            application = scope.get(cls)
            application.initialize()
            return application
