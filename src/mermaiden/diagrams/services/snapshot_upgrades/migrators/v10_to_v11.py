from dataclasses import dataclass, replace

from wireup import injectable

from .....runtime.snapshot.value_validator import SnapshotBoolean, SnapshotMapping
from ..domain import SnapshotChange, SnapshotMigrationState, SnapshotMigrator


@injectable(as_type=SnapshotMigrator, qualifier="v10_to_v11", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class SnapshotV10ToV11Migrator(SnapshotMigrator):
    def source_version(self) -> int:
        return 10

    def target_version(self) -> int:
        return 11

    def migrate(self, state: SnapshotMigrationState) -> SnapshotMigrationState:
        candidate = replace(state.current, version=11)
        changes = state.changes
        if candidate.kind == "classDiagram":
            fields = dict(SnapshotMapping.model_validate(candidate.configuration["fields"]).root)
            SnapshotBoolean.model_validate(fields["html_labels"])
            del fields["html_labels"]
            candidate = replace(candidate, configuration={**candidate.configuration, "fields": fields})
            original = SnapshotMapping.model_validate(state.original.configuration["fields"]).root
            if "html_labels" in original:
                value = SnapshotBoolean.model_validate(original["html_labels"]).root
                path = "/configuration/fields/html_labels"
                changes = (*changes, SnapshotChange((path,), "Retire class HTML labels.", {path: value}, value))
        return SnapshotMigrationState(state.original, candidate, changes)
