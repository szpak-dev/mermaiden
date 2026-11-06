import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields
from functools import partial

from pydantic import TypeAdapter, ValidationError
from wireup import injectable

from ....runtime.snapshot.domain import DiagramSnapshot, SnapshotError, SnapshotTypeRegistry
from ....runtime.snapshot.value_validator import SnapshotMapping, SnapshotString
from ..persistence import DiagramPersistenceApplication
from .domain import (
    SnapshotChange,
    SnapshotMigrationState,
    SnapshotMigrator,
    SnapshotUpgradeError,
    SnapshotUpgradeResult,
)


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class SnapshotUpgradeService:
    migrators: Sequence[SnapshotMigrator]
    persistence: DiagramPersistenceApplication
    contracts: SnapshotTypeRegistry

    def upgrade_snapshot(self, payload: Mapping[str, object], *, allow_loss: bool = False) -> SnapshotUpgradeResult:
        try:
            boundary = SnapshotMapping.model_validate(payload).root
        except ValidationError:
            raise SnapshotUpgradeError("Snapshot must be an object with string keys.", ("",)) from None
        expected = {field.name for field in fields(DiagramSnapshot)}
        differences = sorted(boundary.keys() ^ expected)
        if differences:
            raise SnapshotUpgradeError(
                "Missing or unsupported snapshot envelope fields.",
                tuple(f"/{self.pointer_segment(name)}" for name in differences),
            )
        try:
            TypeAdapter(bool).validate_python(allow_loss, strict=True)
            original = TypeAdapter(DiagramSnapshot).validate_json(
                json.dumps(dict(boundary), allow_nan=False), strict=True
            )
            if set(original.configuration) != {"$type", "fields"}:
                raise SnapshotUpgradeError("Invalid encoded configuration.", ("/configuration",))
            SnapshotString.model_validate(original.configuration["$type"])
            SnapshotMapping.model_validate(original.configuration["fields"])
        except (ValidationError, ValueError, TypeError):
            raise SnapshotUpgradeError("Invalid JSON snapshot envelope or loss option.", ("",)) from None
        try:
            target = self.contracts.identity(original.kind).snapshot_version
        except SnapshotError:
            raise SnapshotUpgradeError("Unknown snapshot diagram kind.", ("/kind",)) from None
        route = self.route(original.version, target)
        state = SnapshotMigrationState(original, original, ())
        for migrator in route:
            try:
                state = migrator.migrate(state)
            except SnapshotUpgradeError:
                raise
            except (ValidationError, ValueError, TypeError, KeyError):
                raise SnapshotUpgradeError(
                    f"Invalid source values for snapshot version {migrator.source_version()}.", ("",)
                ) from None
            if state.current.version != migrator.target_version() or state.current.kind != original.kind:
                raise SnapshotUpgradeError("Migrator returned an invalid transition.", ("/version", "/kind"))
        changes = self.report(state)
        losses = tuple(path for change in changes if change.requires_loss_acceptance for path in change.paths)
        if losses and not allow_loss:
            raise SnapshotUpgradeError("Snapshot upgrade requires explicit loss acceptance.", losses, changes)
        self.validate(state.current)
        try:
            restored = self.persistence.restore(state.current.to_dict())
            encoded = self.persistence.snapshot(restored).to_dict()
        except (SnapshotError, ValidationError, ValueError, TypeError):
            raise SnapshotUpgradeError("Snapshot fails current diagram validation.", ("",), changes) from None
        candidate = state.current.to_dict()
        normalized = tuple(
            f"/{name}"
            for name in ("configuration", "elements", "relations", "annotations", "properties")
            if candidate[name] != encoded[name]
        )
        if normalized:
            raise SnapshotUpgradeError("Snapshot values require implicit normalization.", normalized, changes)
        return SnapshotUpgradeResult(state.current, changes)

    def pointer_segment(self, name: str) -> str:
        return name.replace("~", "~0").replace("/", "~1")

    def route(self, source: int, target: int) -> tuple[SnapshotMigrator, ...]:
        registrations: dict[int, SnapshotMigrator] = {}
        for migrator in self.migrators:
            version = migrator.source_version()
            if version in registrations or migrator.target_version() != version + 1:
                raise SnapshotUpgradeError("Invalid or duplicate snapshot migrator registration.", ("/version",))
            registrations[version] = migrator
        if source > target:
            raise SnapshotUpgradeError("Snapshot version is newer than the current contract.", ("/version",))
        route: list[SnapshotMigrator] = []
        while source < target:
            if source not in registrations:
                raise SnapshotUpgradeError("No complete upgrade path for this snapshot version.", ("/version",))
            migrator = registrations[source]
            route.append(migrator)
            source = migrator.target_version()
        return tuple(route)

    def report(self, state: SnapshotMigrationState) -> tuple[SnapshotChange, ...]:
        if state.original.version == state.current.version:
            return ()
        changes = [SnapshotChange(("/version",), "Advance the snapshot contract version.", {}, False), *state.changes]
        described = {path for change in changes for path in change.paths}
        before = SnapshotMapping.model_validate(state.original.configuration["fields"]).root
        after = SnapshotMapping.model_validate(state.current.configuration["fields"]).root
        for name in sorted(before.keys() | after.keys()):
            path = f"/configuration/fields/{self.pointer_segment(name)}"
            if path in described or (name in before and name in after and before[name] == after[name]):
                continue
            if name not in after:
                raise SnapshotUpgradeError("Configuration removal lacks a migration report.", (path,))
            description = (
                "Introduce an explicit configuration value." if name not in before else "Upgrade configuration."
            )
            changes.append(SnapshotChange((path,), description, {}, False))
        return tuple(changes)

    def decode_object(self, kind: str, value: dict[str, object]) -> object:
        if value.keys() == {"$type", "fields"}:
            discriminator = SnapshotString.model_validate(value["$type"]).root
            model = self.contracts.resolve_model(kind, discriminator)
            members = SnapshotMapping.model_validate(value["fields"]).root
            if members.keys() != model.model_fields.keys():
                raise SnapshotError("Invalid persisted model field set.")
            parameters: object = members["root"] if model.__pydantic_root_model__ else members
            return model.model_validate_json(TypeAdapter(object).dump_json(parameters), strict=True, by_name=True)
        if value.keys() == {"$enum", "value"}:
            discriminator = SnapshotString.model_validate(value["$enum"]).root
            member = SnapshotString.model_validate(value["value"]).root
            return self.contracts.resolve_enum(kind, discriminator)(member)
        return value

    def decode(self, kind: str, value: object, path: str) -> object:
        try:
            return TypeAdapter(object).validate_python(
                json.loads(json.dumps(value, allow_nan=False), object_hook=partial(self.decode_object, kind))
            )
        except (ValidationError, SnapshotError, ValueError, TypeError, KeyError):
            raise SnapshotUpgradeError("Invalid persisted value for the current contract.", (path,)) from None

    def validate(self, snapshot: DiagramSnapshot) -> None:
        contract = self.contracts.contract(snapshot.kind)
        if (
            "$type" not in snapshot.configuration
            or snapshot.configuration["$type"] != contract.configuration.discriminator
        ):
            raise SnapshotUpgradeError("Invalid configuration discriminator.", ("/configuration/$type",))
        self.decode(snapshot.kind, snapshot.configuration, "/configuration")
        for name, objects, registered in (
            ("elements", snapshot.elements, contract.elements),
            ("relations", snapshot.relations, contract.relations),
            ("annotations", snapshot.annotations, contract.annotations),
        ):
            allowed = {item.discriminator for item in registered}
            for index, value in enumerate(objects):
                path = f"/{name}/{index}"
                if "$type" not in value:
                    raise SnapshotUpgradeError("Missing persisted object discriminator.", (f"{path}/$type",))
                try:
                    discriminator = SnapshotString.model_validate(value["$type"]).root
                except ValidationError:
                    raise SnapshotUpgradeError("Invalid persisted object discriminator.", (f"{path}/$type",)) from None
                if discriminator not in allowed:
                    raise SnapshotUpgradeError("Unsupported persisted object type.", (f"{path}/$type",))
                self.decode(snapshot.kind, value, path)
        differences = sorted(snapshot.properties.keys() ^ contract.properties.keys())
        if differences:
            raise SnapshotUpgradeError(
                "Invalid persisted properties.",
                tuple(f"/properties/{self.pointer_segment(name)}" for name in differences),
            )
        for name, annotation in contract.properties.items():
            path = f"/properties/{self.pointer_segment(name)}"
            decoded = self.decode(snapshot.kind, snapshot.properties[name], path)
            try:
                TypeAdapter[object](annotation).validate_json(TypeAdapter(object).dump_json(decoded), strict=True)
            except ValidationError:
                raise SnapshotUpgradeError("Invalid persisted property.", (path,)) from None
