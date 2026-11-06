import json
from dataclasses import dataclass, replace

from pydantic import TypeAdapter
from wireup import injectable

from .....runtime.snapshot.value_validator import SnapshotMapping, SnapshotString
from ..domain import SnapshotMigrationState, SnapshotMigrator, SnapshotUpgradeError


@injectable(as_type=SnapshotMigrator, qualifier="v6_to_v7", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class SnapshotV6ToV7Migrator(SnapshotMigrator):
    def source_version(self) -> int:
        return 6

    def target_version(self) -> int:
        return 7

    def migrate(self, state: SnapshotMigrationState) -> SnapshotMigrationState:
        if state.current.kind == "classDiagram":
            for index, element in enumerate(state.current.elements):
                try:
                    json.loads(json.dumps(element), object_hook=self.validate_type)
                except (ValueError, KeyError):
                    raise SnapshotUpgradeError("Invalid v6 class type.", (f"/elements/{index}",)) from None
        return SnapshotMigrationState(state.original, replace(state.current, version=7), state.changes)

    def validate_type(self, value: dict[str, object]) -> dict[str, object]:
        if "$type" in value and value["$type"] == "mermaiden/value/classDiagram/class_type":
            fields = SnapshotMapping.model_validate(value["fields"]).root
            if value.keys() != {"$type", "fields"} or set(fields) != {"name", "arguments"}:
                raise ValueError("Invalid class type fields.")
            SnapshotString.model_validate(fields["name"])
            arguments = TypeAdapter(list[object]).validate_python(fields["arguments"], strict=True)
            if len(arguments) > 1:
                raise ValueError("The v6 contract permits at most one generic argument.")
        return value
