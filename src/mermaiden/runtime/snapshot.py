from collections.abc import Callable, Mapping
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from importlib import import_module
from types import UnionType
from typing import Any, cast, get_args, get_origin, get_type_hints

from pydantic import BaseModel

from ..core.annotation import Annotation
from ..core.diagram import Diagram
from ..core.element import Element
from ..core.relation import Relation
from .diagrams.state import DiagramData


class SnapshotError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class DiagramSnapshot:
    version: int
    kind: str
    configuration: Mapping[str, object]
    elements: tuple[Mapping[str, object], ...]
    relations: tuple[Mapping[str, object], ...]
    annotations: tuple[Mapping[str, object], ...]
    properties: Mapping[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "kind": self.kind,
            "configuration": dict(self.configuration),
            "elements": list(self.elements),
            "relations": list(self.relations),
            "annotations": list(self.annotations),
            "properties": dict(self.properties),
        }


class DiagramSnapshotCodec:
    version = 2

    def snapshot(self, diagram: Diagram) -> DiagramSnapshot:
        return DiagramSnapshot(
            version=self.version,
            kind=diagram.kind,
            configuration=cast(Mapping[str, object], self._encode(self._configuration(diagram))),
            elements=tuple(cast(Mapping[str, object], self._encode(item)) for item in diagram.root_elements),
            relations=tuple(cast(Mapping[str, object], self._encode(item)) for item in diagram.find_relations()),
            annotations=tuple(cast(Mapping[str, object], self._encode(item)) for item in diagram.find_annotations()),
            properties={
                field.name: self._encode(getattr(diagram, field.name))
                for field in fields(cast(Any, diagram))
                if field.name not in {"runtime", "structure", "constraints", "configuration"}
            },
        )

    def restore(self, payload: Mapping[str, object]) -> DiagramSnapshot:
        try:
            version = int(cast(Any, payload["version"]))
        except (KeyError, TypeError, ValueError) as error:
            raise SnapshotError("Snapshot is malformed.") from error
        if version != self.version:
            raise SnapshotError(f"Unsupported snapshot version '{version}'; expected version '{self.version}'.")
        try:
            snapshot = DiagramSnapshot(
                version=version,
                kind=self._string(payload["kind"], "kind"),
                configuration=self._mapping(payload["configuration"], "configuration"),
                elements=self._objects(payload["elements"], "elements"),
                relations=self._objects(payload["relations"], "relations"),
                annotations=self._objects(payload["annotations"], "annotations"),
                properties=self._mapping(payload.get("properties", {}), "properties"),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise SnapshotError("Snapshot is malformed.") from error
        return snapshot

    def hydrate(self, snapshot: DiagramSnapshot, diagram: Diagram) -> DiagramData:
        current_configuration = self._configuration(diagram)
        configuration = self.decode_value(snapshot.configuration, type(current_configuration))
        if type(configuration) is not type(current_configuration):
            raise SnapshotError(f"Snapshot configuration is not valid for diagram '{diagram.kind}'.")
        object.__setattr__(diagram, "configuration", configuration)
        elements = tuple(self.decode_value(item, Element) for item in snapshot.elements)
        relations = tuple(self.decode_value(item, Relation) for item in snapshot.relations)
        annotations = tuple(self.decode_value(item, Annotation) for item in snapshot.annotations)
        for name, value in snapshot.properties.items():
            field = next((item for item in fields(cast(Any, diagram)) if item.name == name), None)
            if field is None or name in {"runtime", "structure", "constraints", "configuration"}:
                raise SnapshotError(f"Snapshot property '{name}' is not supported.")
            object.__setattr__(diagram, name, self.decode_value(value, field.type))
        return DiagramData(elements, relations, annotations)

    def decode_value(self, value: object, expected: Any = object) -> Any:
        if isinstance(value, Mapping) and "$enum" in value:
            enum_value = cast(Mapping[str, Any], value)
            enum = self._resolve(self._string(enum_value["$enum"], "$enum"), Enum)
            return cast(Callable[[object], Enum], enum)(enum_value["value"])
        if isinstance(value, Mapping) and "$type" in value:
            typed_value = cast(Mapping[str, Any], value)
            item_type = self._resolve(self._string(typed_value["$type"], "$type"), expected)
            values: dict[str, Any] = dict(self._mapping(typed_value.get("fields"), "fields"))
            hints: dict[str, Any] = get_type_hints(item_type)
            parameters = {name: self.decode_value(item, hints.get(name, object)) for name, item in values.items()}
            return item_type(**parameters)
        origin = get_origin(expected)
        arguments = get_args(expected)
        if origin in (tuple, list):
            if not isinstance(value, list):
                raise SnapshotError("Snapshot collection is malformed.")
            item_type = arguments[0] if arguments else object
            items = [self.decode_value(item, item_type) for item in cast(list[Any], value)]
            return tuple(items) if origin is tuple else items
        if origin is not None and issubclass(origin, Mapping):
            if not isinstance(value, Mapping):
                raise SnapshotError("Snapshot mapping is malformed.")
            value_type = arguments[1] if len(arguments) > 1 else object
            mapping = cast(Mapping[Any, Any], value)
            return {str(key): self.decode_value(item, value_type) for key, item in mapping.items()}
        if origin is UnionType:
            for item_type in arguments:
                if item_type is type(None) and value is None:
                    return None
                try:
                    return self.decode_value(cast(Any, value), item_type)
                except (TypeError, ValueError, SnapshotError):
                    continue
            raise SnapshotError("Snapshot value does not match its declared type.")
        if isinstance(expected, type) and issubclass(expected, Enum):
            return expected(value)
        return cast(Any, value)

    def _encode(self, value: object) -> Any:
        if isinstance(value, Enum):
            return {"$enum": self._reference(type(value)), "value": value.value}
        if isinstance(value, BaseModel):
            return {
                "$type": self._reference(type(value)),
                "fields": {
                    name: self._encode(getattr(value, name)) for name in type(value).model_fields
                },
            }
        if is_dataclass(value) and not isinstance(value, type):
            return {
                "$type": self._reference(type(value)),
                "fields": {field.name: self._encode(getattr(value, field.name)) for field in fields(value)},
            }
        if isinstance(value, Mapping):
            mapping = cast(Mapping[Any, Any], value)
            return {str(key): self._encode(item) for key, item in mapping.items()}
        if isinstance(value, tuple | list):
            items = cast(list[Any] | tuple[Any, ...], value)
            return [self._encode(item) for item in items]
        return value

    @staticmethod
    def _reference(item_type: type[object]) -> str:
        return f"{item_type.__module__}:{item_type.__qualname__}"

    @staticmethod
    def _configuration(diagram: Diagram) -> BaseModel:
        configuration = getattr(diagram, "configuration", None)
        if not isinstance(configuration, BaseModel):
            raise SnapshotError(f"Diagram '{diagram.kind}' has no persistable configuration.")
        return configuration

    def _resolve(self, reference: str, expected: Any) -> type[Any]:
        module_name, separator, qualified_name = reference.partition(":")
        if not separator or not module_name.startswith("mermaiden."):
            raise SnapshotError(f"Snapshot type '{reference}' is not supported.")
        try:
            item: object = import_module(module_name)
            for name in qualified_name.split("."):
                item = getattr(item, name)
        except (AttributeError, ImportError) as error:
            raise SnapshotError(f"Snapshot type '{reference}' is not available.") from error
        if not isinstance(item, type) or (expected is not object and not issubclass(item, expected)):
            raise SnapshotError(f"Snapshot type '{reference}' is not valid here.")
        return cast(type[Any], item)

    @staticmethod
    def _mapping(value: object, name: str) -> Mapping[str, object]:
        if not isinstance(value, Mapping):
            raise SnapshotError(f"Snapshot '{name}' must be an object.")
        return cast(Mapping[str, object], value)

    def _objects(self, value: object, name: str) -> tuple[Mapping[str, object], ...]:
        items = cast(list[Any], value)
        if not isinstance(value, list) or not all(isinstance(item, Mapping) for item in items):
            raise SnapshotError(f"Snapshot '{name}' must be an array of objects.")
        return tuple(cast(Mapping[str, object], item) for item in items)

    @staticmethod
    def _string(value: object, name: str) -> str:
        if not isinstance(value, str):
            raise SnapshotError(f"Snapshot '{name}' must be a string.")
        return value
