import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields
from decimal import Decimal

from pydantic import TypeAdapter, ValidationError
from wireup import injectable

from ....runtime.snapshot.domain import DiagramSnapshot, SnapshotError, SnapshotTypeRegistry
from ....runtime.snapshot.value_validator import SnapshotEncodedValue, SnapshotMapping, SnapshotString
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
            if self.comparable(candidate[name]) != self.comparable(encoded[name])
        )
        if normalized:
            raise SnapshotUpgradeError("Snapshot values require implicit normalization.", normalized, changes)
        return SnapshotUpgradeResult(state.current, changes)

    def comparable(self, value: object) -> object:
        return TypeAdapter(object).validate_python(
            json.loads(json.dumps(value, allow_nan=False), parse_int=self.number, parse_float=self.number)
        )

    def number(self, value: str) -> tuple[Decimal]:
        return (Decimal(value),)

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

    def validate(self, snapshot: DiagramSnapshot) -> None:
        contract = self.contracts.contract(snapshot.kind)
        if (
            "$type" not in snapshot.configuration
            or snapshot.configuration["$type"] != contract.configuration.discriminator
        ):
            raise SnapshotUpgradeError("Invalid configuration discriminator.", ("/configuration/$type",))
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
        differences = sorted(snapshot.properties.keys() ^ contract.properties.keys())
        if differences:
            raise SnapshotUpgradeError(
                "Invalid persisted properties.",
                tuple(f"/properties/{self.pointer_segment(name)}" for name in differences),
            )
        for name, annotation in contract.properties.items():
            path = f"/properties/{self.pointer_segment(name)}"
            try:
                decoded = SnapshotEncodedValue.model_validate(snapshot.properties[name]).decode(
                    self.contracts, contract
                )
                TypeAdapter[object](annotation).validate_json(TypeAdapter(object).dump_json(decoded), strict=True)
            except (ValidationError, SnapshotError, ValueError, TypeError):
                raise SnapshotUpgradeError("Invalid persisted property.", (path,)) from None
