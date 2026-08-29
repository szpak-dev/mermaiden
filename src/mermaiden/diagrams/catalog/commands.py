from collections.abc import Callable, Mapping
from dataclasses import dataclass
from inspect import Parameter, signature
from typing import Annotated, cast, get_args, get_origin, get_type_hints

from pydantic import ValidationError
from wireup import injectable

from ...core.constraint import ChangeReport
from ...domain import CommandPayloadType, ValidatedCommandPayload
from ...mutations.domain import MutationPayloadFactory
from ..application import DiagramInfo, DiagramsApplication
from ..domain import DiagramModel
from .models import CommandPayload
from .objects import DiagramObjectCatalog


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramCommandCatalog:
    registry: DiagramsApplication
    objects: DiagramObjectCatalog
    mutation_payloads: MutationPayloadFactory

    def names(self, info: DiagramInfo) -> tuple[str, ...]:
        return tuple(sorted(self._methods(info)))

    def payload(self, diagram_id: str, command_name: str) -> CommandPayloadType:
        info = self.registry.get(diagram_id)
        method = self._methods(info).get(command_name)
        if method is None:
            raise KeyError(f"Unknown command '{command_name}' for diagram '{diagram_id}'.")
        if method is DiagramModel.configure:
            return cast(CommandPayloadType, type(self.registry.get_diagram(diagram_id).configuration))
        if method is DiagramModel.update_element:
            return self.mutation_payloads.element(info.diagram_type.__name__, self.objects.elements(info))
        if method is DiagramModel.update_relation:
            return self.mutation_payloads.relation(info.diagram_type.__name__, self.objects.relations(info))
        if method is DiagramModel.update_annotation:
            return self.mutation_payloads.annotation(info.diagram_type.__name__, self.objects.annotations(info))
        annotations, defaults = self._payload_fields(method)
        name = f"{info.diagram_type.__name__}{self._pascal_case(command_name)}Payload"
        namespace: dict[str, object] = {
            "__module__": __name__,
            "__annotations__": annotations,
            **defaults,
        }
        payload_type = cast(
            type[CommandPayload],
            type(name, (CommandPayload,), namespace),
        )
        return cast(CommandPayloadType, payload_type)

    def validate(
        self,
        diagram: DiagramModel,
        command_name: str,
        payload: Mapping[str, object],
    ) -> ValidatedCommandPayload:
        try:
            return self.payload(diagram.kind, command_name).model_validate(payload)
        except ValidationError as error:
            raise ValueError(f"Command '{command_name}' has an invalid payload.") from error

    def _methods(self, info: DiagramInfo) -> dict[str, Callable[..., ChangeReport | None]]:
        commands = {
            name: cast(Callable[..., ChangeReport | None], method)
            for name, method in info.diagram_type.__dict__.items()
            if not name.startswith("_")
            if callable(method)
            if self._is_command(cast(Callable[..., ChangeReport | None], method))
        }
        commands[DiagramModel.configure.__name__] = DiagramModel.configure
        if self.objects.elements(info):
            commands[DiagramModel.update_element.__name__] = DiagramModel.update_element
            commands[DiagramModel.remove_element.__name__] = DiagramModel.remove_element
        if self.objects.relations(info):
            commands[DiagramModel.update_relation.__name__] = DiagramModel.update_relation
            commands[DiagramModel.remove_relation.__name__] = DiagramModel.remove_relation
        if self.objects.annotations(info):
            commands[DiagramModel.update_annotation.__name__] = DiagramModel.update_annotation
            commands[DiagramModel.remove_annotation.__name__] = DiagramModel.remove_annotation
        return commands

    def _is_command(self, method: Callable[..., ChangeReport | None]) -> bool:
        return_type = get_type_hints(method).get("return")
        return return_type in {ChangeReport, type(None)}

    def _payload_fields(
        self,
        method: Callable[..., ChangeReport | None],
    ) -> tuple[dict[str, object], dict[str, object]]:
        hints = get_type_hints(method, include_extras=True)
        annotations: dict[str, object] = {}
        defaults: dict[str, object] = {}
        for parameter in signature(method).parameters.values():
            if parameter.name == "self":
                continue
            annotation, default = self._payload_field(parameter, hints)
            annotations[parameter.name] = annotation
            defaults[parameter.name] = default
        return annotations, defaults

    def _payload_field(
        self,
        parameter: Parameter,
        hints: Mapping[str, object],
    ) -> tuple[object, object]:
        annotation = hints.get(parameter.name)
        if annotation is None:
            raise TypeError(f"Command parameter '{parameter.name}' has no type annotation.")
        if parameter.kind is Parameter.VAR_POSITIONAL:
            if get_origin(annotation) is Annotated:
                item, *metadata = get_args(annotation)
                annotation = Annotated[tuple[item, ...], *metadata]
            else:
                annotation = tuple[annotation, ...]
            return annotation, ...
        default = ... if parameter.default is Parameter.empty else parameter.default
        return annotation, default

    def _pascal_case(self, value: str) -> str:
        return "".join(part.capitalize() for part in value.split("_"))
