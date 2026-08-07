from collections.abc import Mapping
from dataclasses import dataclass
from importlib import import_module
from inspect import Parameter, getmembers, isclass, signature
from typing import Any, get_type_hints

from pydantic import ValidationError, create_model
from wireup import injectable

from ..core.annotation import Annotation
from ..core.constraint import ChangeReport
from ..core.element import Element
from ..core.model import ValueModel
from ..core.relation import Relation
from .application import DiagramInfo, DiagramsApplication
from .domain import DiagramModel


class CommandPayload(ValueModel):
    pass


class DiagramDescription(ValueModel):
    id: str
    name: str
    elements: Mapping[str, Mapping[str, object]]
    relations: Mapping[str, Mapping[str, object]]
    annotations: Mapping[str, Mapping[str, object]]
    commands: Mapping[str, Mapping[str, object]]


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramCatalog:
    registry: DiagramsApplication

    def describe(self, diagram_id: str) -> DiagramDescription:
        info = self.registry.get(diagram_id)
        return DiagramDescription(
            id=info.id,
            name=info.name,
            elements=self._models(info, "elements", Element),
            relations=self._models(info, "relations", Relation),
            annotations=self._models(info, "annotations", Annotation),
            commands={
                name: self.command_payload(info.id, name).model_json_schema()
                for name in self.command_names(info)
            },
        )

    def command_names(self, info: DiagramInfo) -> tuple[str, ...]:
        return tuple(
            sorted(
                name
                for name, method in info.diagram_type.__dict__.items()
                if not name.startswith("_")
                if callable(method)
                if self._is_command(method)
            )
        )

    def command_payload(self, diagram_id: str, command_name: str) -> type[CommandPayload]:
        info = self.registry.get(diagram_id)
        method = getattr(info.diagram_type, command_name, None)
        if command_name not in self.command_names(info) or not callable(method):
            raise KeyError(f"Unknown command '{command_name}' for diagram '{diagram_id}'.")
        fields = self._payload_fields(method)
        return create_model(
            f"{info.diagram_type.__name__}{self._pascal_case(command_name)}Payload",
            __base__=CommandPayload,
            **fields,
        )

    def validate_command(
        self,
        diagram: DiagramModel,
        command_name: str,
        payload: Mapping[str, object],
    ) -> CommandPayload:
        try:
            return self.command_payload(diagram.kind, command_name).model_validate(payload)
        except ValidationError as error:
            raise ValueError(f"Command '{command_name}' has an invalid payload.") from error

    def _models(
        self,
        info: DiagramInfo,
        module_name: str,
        parent: type[Element] | type[Relation] | type[Annotation],
    ) -> dict[str, Mapping[str, object]]:
        module = self._module(info, module_name)
        if module is None:
            return {}
        return {
            item.kind_for(): item.model_json_schema()
            for _, item in getmembers(module, isclass)
            if item.__module__ == module.__name__
            if issubclass(item, parent)
            if item is not parent
        }

    @staticmethod
    def _module(info: DiagramInfo, name: str) -> object | None:
        package = info.diagram_type.__module__.removesuffix(".diagram")
        try:
            return import_module(f"{package}.{name}")
        except ModuleNotFoundError:
            return None

    @staticmethod
    def _is_command(method: object) -> bool:
        return_type = get_type_hints(method).get("return")
        return return_type in {ChangeReport, type(None)}

    @staticmethod
    def _payload_fields(method: object) -> dict[str, tuple[object, object]]:
        hints = get_type_hints(method)
        return {
            parameter.name: DiagramCatalog._payload_field(parameter, hints)
            for parameter in signature(method).parameters.values()
            if parameter.name != "self"
        }

    @staticmethod
    def _payload_field(parameter: Parameter, hints: Mapping[str, object]) -> tuple[object, object]:
        annotation = hints.get(parameter.name, Any)
        if parameter.kind is Parameter.VAR_POSITIONAL:
            return tuple[annotation, ...], ()
        default = ... if parameter.default is Parameter.empty else parameter.default
        return annotation, default

    @staticmethod
    def _pascal_case(value: str) -> str:
        return "".join(part.capitalize() for part in value.split("_"))
