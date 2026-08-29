from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any, cast

from pydantic import BaseModel
from wireup import injectable


@injectable
class SnapshotValueEncoder:
    def encode(self, value: object) -> Any:
        if isinstance(value, Enum):
            return {"$enum": self.reference(type(value)), "value": value.value}
        if isinstance(value, BaseModel):
            return {
                "$type": self.reference(type(value)),
                "fields": {name: self.encode(getattr(value, name)) for name in type(value).model_fields},
            }
        if is_dataclass(value) and not isinstance(value, type):
            return {
                "$type": self.reference(type(value)),
                "fields": {field.name: self.encode(getattr(value, field.name)) for field in fields(value)},
            }
        if isinstance(value, Mapping):
            mapping = cast(Mapping[Any, Any], value)
            return {str(key): self.encode(item) for key, item in mapping.items()}
        if isinstance(value, tuple | list):
            items = cast(list[Any] | tuple[Any, ...], value)
            return [self.encode(item) for item in items]
        return value

    def reference(self, item_type: type[object]) -> str:
        return f"{item_type.__module__}:{item_type.__qualname__}"
