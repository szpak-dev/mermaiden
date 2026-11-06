from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from wireup import injectable

from .....core.characters import Identifier, OptionalText, Text
from .....runtime.snapshot.value_validator import SnapshotMapping, SnapshotMappings, SnapshotString
from ..domain import SnapshotChange, SnapshotMigrationState, SnapshotMigrator, SnapshotUpgradeError


class LegacyTargetKind(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    discriminator: str = Field(alias="$enum")
    value: Literal["element"]


class LegacyTargetFields(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    kind: LegacyTargetKind
    id: str = Field(pattern=Identifier.pattern)


class LegacyTarget(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    discriminator: str = Field(alias="$type")
    fields: LegacyTargetFields


class LegacyAnnotationFields(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    id: str = Field(pattern=Identifier.pattern)
    targets: list[LegacyTarget] = Field(min_length=1, max_length=1)


class LegacyClassNoteFields(LegacyAnnotationFields):
    text: str = Field(pattern=Text.pattern)


class LegacyTreeAnnotationFields(LegacyAnnotationFields):
    highlight: bool
    icon: str = Field(pattern=r"^[\w-]*(?::[\w-]+)?$")
    description: str = Field(pattern=OptionalText.pattern)


@injectable(as_type=SnapshotMigrator, qualifier="v9_to_v10", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class SnapshotV9ToV10Migrator(SnapshotMigrator):
    def source_version(self) -> int:
        return 9

    def target_version(self) -> int:
        return 10

    def migrate(self, state: SnapshotMigrationState) -> SnapshotMigrationState:
        candidate = replace(state.current, version=10)
        if candidate.kind not in ("classDiagram", "treeView-beta"):
            return SnapshotMigrationState(state.original, candidate, state.changes)
        names = {"classDiagram": "class_note", "treeView-beta": "tree_annotation"}
        discriminator = f"mermaiden/annotation/{candidate.kind}/{names[candidate.kind]}"
        targets = self.element_ids(candidate.elements, candidate.kind)
        ids: set[str] = set()
        changes = list(state.changes)
        for index, annotation in enumerate(candidate.annotations):
            path = f"/annotations/{index}"
            if set(annotation) != {"$type", "fields"} or annotation["$type"] != discriminator:
                raise SnapshotUpgradeError("Unsupported historical annotation.", (path,))
            fields: LegacyAnnotationFields
            if candidate.kind == "classDiagram":
                fields = LegacyClassNoteFields.model_validate(annotation["fields"])
            else:
                fields = LegacyTreeAnnotationFields.model_validate(annotation["fields"])
            if fields.id in ids:
                raise SnapshotUpgradeError("Duplicate historical annotation identifier.", (f"{path}/fields/id",))
            ids.add(fields.id)
            for target in fields.targets:
                if (
                    target.discriminator != f"mermaiden/value/{candidate.kind}/target_ref"
                    or target.fields.kind.discriminator != f"mermaiden/enum/{candidate.kind}/target_kind"
                    or target.fields.id not in targets
                ):
                    raise SnapshotUpgradeError("Invalid historical annotation target.", (f"{path}/fields/targets",))
            changes.append(
                SnapshotChange(
                    (path,),
                    "Remove unsupported standalone annotation.",
                    {path: state.original.annotations[index]},
                    True,
                )
            )
        return SnapshotMigrationState(state.original, replace(candidate, annotations=()), tuple(changes))

    def element_ids(self, elements: Sequence[Mapping[str, object]], kind: str) -> set[str]:
        ids: set[str] = set()
        for element in elements:
            discriminator = SnapshotString.model_validate(element["$type"]).root
            fields = SnapshotMapping.model_validate(element["fields"]).root
            if discriminator in ("mermaiden/element/classDiagram/class", "mermaiden/element/treeView-beta/tree_item"):
                ids.add(SnapshotString.model_validate(fields["id"]).root)
            if kind == "classDiagram" and discriminator == "mermaiden/element/classDiagram/class_namespace":
                children = SnapshotMappings.model_validate(fields["elements"]).root
                ids.update(self.element_ids(children, kind))
        return ids
