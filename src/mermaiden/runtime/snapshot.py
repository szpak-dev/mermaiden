from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from importlib import import_module
from types import UnionType
from typing import get_args, get_origin, get_type_hints

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
    elements: tuple[Mapping[str, object], ...]
    relations: tuple[Mapping[str, object], ...]
    annotations: tuple[Mapping[str, object], ...]
    properties: Mapping[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "kind": self.kind,
            "elements": list(self.elements),
            "relations": list(self.relations),
            "annotations": list(self.annotations),
            "properties": dict(self.properties),
        }


class DiagramSnapshotCodec:
    version = 1

    def snapshot(self, diagram: Diagram) -> DiagramSnapshot:
        return DiagramSnapshot(
            self.version,
            diagram.kind,
            tuple(self._encode(item) for item in diagram.root_elements),
            tuple(self._encode(item) for item in diagram.find_relations()),
            tuple(self._encode(item) for item in diagram.find_annotations()),
            {
                field.name: self._encode(getattr(diagram, field.name))
                for field in fields(diagram)
                if field.name not in {"runtime", "structure", "constraints", "configuration"}
            },
        )

    def restore(self, payload: Mapping[str, object]) -> DiagramSnapshot:
        try:
            snapshot = DiagramSnapshot(
                int(payload["version"]),
                self._string(payload["kind"], "kind"),
                self._objects(payload["elements"], "elements"),
                self._objects(payload["relations"], "relations"),
                self._objects(payload["annotations"], "annotations"),
                self._mapping(payload.get("properties", {}), "properties"),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise SnapshotError("Snapshot is malformed.") from error
        if snapshot.version != self.version:
            raise SnapshotError(f"Unsupported snapshot version '{snapshot.version}'.")
        return snapshot

    def hydrate(self, snapshot: DiagramSnapshot, diagram: Diagram) -> DiagramData:
        elements = tuple(self.decode_value(item, Element) for item in snapshot.elements)
        relations = tuple(self.decode_value(item, Relation) for item in snapshot.relations)
        annotations = tuple(self.decode_value(item, Annotation) for item in snapshot.annotations)
        for name, value in snapshot.properties.items():
            field = next((item for item in fields(diagram) if item.name == name), None)
            if field is None or name in {"runtime", "structure", "constraints", "configuration"}:
                raise SnapshotError(f"Snapshot property '{name}' is not supported.")
            object.__setattr__(diagram, name, self.decode_value(value, field.type))
        return DiagramData(elements, relations, annotations)

    def decode_value(self, value: object, expected: object = object) -> object:
        if isinstance(value, Mapping) and "$enum" in value:
            enum = self._resolve(self._string(value["$enum"], "$enum"), Enum)
            return enum(value["value"])
        if isinstance(value, Mapping) and "$type" in value:
            item_type = self._resolve(self._string(value["$type"], "$type"), expected)
            values = self._mapping(value.get("fields"), "fields")
            hints = get_type_hints(item_type)
            parameters = {name: self.decode_value(item, hints.get(name, object)) for name, item in values.items()}
            return item_type(**parameters)
        origin = get_origin(expected)
        arguments = get_args(expected)
        if origin in (tuple, list):
            if not isinstance(value, list):
                raise SnapshotError("Snapshot collection is malformed.")
            item_type = arguments[0] if arguments else object
            items = [self.decode_value(item, item_type) for item in value]
            return tuple(items) if origin is tuple else items
        if origin is not None and issubclass(origin, Mapping):
            if not isinstance(value, Mapping):
                raise SnapshotError("Snapshot mapping is malformed.")
            value_type = arguments[1] if len(arguments) > 1 else object
            return {str(key): self.decode_value(item, value_type) for key, item in value.items()}
        if origin is UnionType:
            for item_type in arguments:
                if item_type is type(None) and value is None:
                    return None
                try:
                    return self.decode_value(value, item_type)
                except (TypeError, ValueError, SnapshotError):
                    continue
            raise SnapshotError("Snapshot value does not match its declared type.")
        if isinstance(expected, type) and issubclass(expected, Enum):
            return expected(value)
        return value

    def _encode(self, value: object) -> object:
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
            return {str(key): self._encode(item) for key, item in value.items()}
        if isinstance(value, tuple | list):
            return [self._encode(item) for item in value]
        return value

    @staticmethod
    def _reference(item_type: type[object]) -> str:
        return f"{item_type.__module__}:{item_type.__qualname__}"

    def _resolve(self, reference: str, expected: object) -> type[object]:
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
        return item

    @staticmethod
    def _mapping(value: object, name: str) -> Mapping[str, object]:
        if not isinstance(value, Mapping):
            raise SnapshotError(f"Snapshot '{name}' must be an object.")
        return value

    def _objects(self, value: object, name: str) -> tuple[Mapping[str, object], ...]:
        if not isinstance(value, list) or not all(isinstance(item, Mapping) for item in value):
            raise SnapshotError(f"Snapshot '{name}' must be an array of objects.")
        return tuple(value)

    @staticmethod
    def _string(value: object, name: str) -> str:
        if not isinstance(value, str):
            raise SnapshotError(f"Snapshot '{name}' must be a string.")
        return value
