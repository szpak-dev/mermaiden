from collections.abc import Mapping
from typing import Any, cast

from wireup import injectable

from .domain import SnapshotError


@injectable
class SnapshotValueValidator:
    def mapping(self, value: object, name: str) -> Mapping[str, object]:
        if not isinstance(value, Mapping):
            raise SnapshotError(f"Snapshot '{name}' must be an object.")
        return cast(Mapping[str, object], value)

    def objects(self, value: object, name: str) -> tuple[Mapping[str, object], ...]:
        items = cast(list[Any], value)
        if not isinstance(value, list) or not all(isinstance(item, Mapping) for item in items):
            raise SnapshotError(f"Snapshot '{name}' must be an array of objects.")
        return tuple(cast(Mapping[str, object], item) for item in items)

    def string(self, value: object, name: str) -> str:
        if not isinstance(value, str):
            raise SnapshotError(f"Snapshot '{name}' must be a string.")
        return value
