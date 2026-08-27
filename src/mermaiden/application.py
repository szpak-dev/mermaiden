from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from inspect import signature

from wireup import SyncContainer, create_sync_container

import mermaiden

from .core.constraint import ChangeReport
from .core.diagram import Diagram
from .diagrams.application import DiagramInfo, DiagramsApplication
from .diagrams.catalog import CommandPayload, DiagramCatalog, DiagramDescription
from .diagrams.configuration import MermaidDiagramConfiguration
from .diagrams.domain import DiagramModel
from .mermaid.application import MermaidApplication
from .mermaid.templates import MermaidTemplateOwnership
from .mermaid.validation import MermaidRenderReport, MermaidRenderValidator
from .runtime.snapshot import DiagramSnapshot, DiagramSnapshotCodec


class ApplicationError(RuntimeError):
    pass


class UnknownCommand(ApplicationError):
    pass


@dataclass(frozen=True, slots=True)
class DiagramCommand:
    operation: str
    arguments: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class Application:
    _container: SyncContainer
    _codec: DiagramSnapshotCodec = field(default_factory=DiagramSnapshotCodec)

    @classmethod
    def create(cls) -> "Application":
        container = create_sync_container(injectables=[mermaiden], config={})
        with container.enter_scope() as scope:
            scope.get(MermaidTemplateOwnership).validate()
        return cls(container)

    def available_diagrams(self) -> tuple[DiagramInfo, ...]:
        with self._container.enter_scope() as scope:
            return scope.get(DiagramsApplication).available()

    def diagram_info(self, diagram_id: str) -> DiagramInfo:
        with self._container.enter_scope() as scope:
            return scope.get(DiagramsApplication).get(diagram_id)

    def diagram_description(self, diagram_id: str) -> DiagramDescription:
        with self._container.enter_scope() as scope:
            return scope.get(DiagramCatalog).describe(diagram_id)

    def command_payload(
        self,
        diagram_id: str,
        command_name: str,
    ) -> type[CommandPayload] | type[MermaidDiagramConfiguration]:
        with self._container.enter_scope() as scope:
            return scope.get(DiagramCatalog).command_payload(diagram_id, command_name)

    def create_diagram(self, diagram_id: str) -> DiagramModel:
        with self._container.enter_scope() as scope:
            return scope.get(DiagramsApplication).get_diagram(diagram_id)

    def apply(self, diagram: DiagramModel, command: DiagramCommand) -> ChangeReport | None:
        operation = getattr(diagram, command.operation, None)
        if command.operation.startswith("_") or not callable(operation):
            raise UnknownCommand(f"Command '{command.operation}' is not supported for '{diagram.kind}'.")
        try:
            with self._container.enter_scope() as scope:
                payload = scope.get(DiagramCatalog).validate_command(diagram, command.operation, command.arguments)
        except (KeyError, ValueError) as error:
            raise UnknownCommand(f"Command '{command.operation}' has invalid arguments.") from error
        if isinstance(payload, MermaidDiagramConfiguration):
            diagram.configure(payload)
            return None
        result = self._invoke(operation, payload)
        return result

    def snapshot(self, diagram: DiagramModel) -> DiagramSnapshot:
        return self._codec.snapshot(diagram)

    def restore(self, payload: Mapping[str, object]) -> DiagramModel:
        snapshot = self._codec.restore(payload)
        diagram = self.create_diagram(snapshot.kind)
        data = self._codec.hydrate(snapshot, diagram)
        diagram.runtime.transaction.apply("restore snapshot", data, diagram, diagram.observer)
        return diagram

    def render(self, diagram: Diagram) -> str:
        with self._container.enter_scope() as scope:
            return scope.get(MermaidApplication).render(diagram)

    def validate_render(self, diagram: Diagram) -> MermaidRenderReport:
        with self._container.enter_scope() as scope:
            return scope.get(MermaidRenderValidator).validate(diagram)

    @staticmethod
    def _invoke(operation: Callable[..., object], payload: CommandPayload) -> ChangeReport | None:
        parameters = tuple(signature(operation).parameters.values())
        values = payload.model_dump()
        variadic = next((item for item in parameters if item.kind is item.VAR_POSITIONAL), None)
        positional = ()
        if variadic is not None:
            positional = tuple(
                values.pop(item.name)
                for item in parameters
                if item.kind in {item.POSITIONAL_ONLY, item.POSITIONAL_OR_KEYWORD}
            ) + tuple(values.pop(variadic.name))
        result = operation(*positional, **values)
        if result is not None and not isinstance(result, ChangeReport):
            raise UnknownCommand("Command is not a mutation.")
        return result
