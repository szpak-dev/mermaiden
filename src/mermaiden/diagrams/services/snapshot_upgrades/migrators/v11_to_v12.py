from dataclasses import dataclass, replace

from pydantic import BaseModel, ConfigDict
from wireup import injectable

from .....runtime.snapshot.value_validator import SnapshotMapping
from ..domain import SnapshotChange, SnapshotMigrationState, SnapshotMigrator, SnapshotUpgradeError


class LegacyPacketFields(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    id: str
    label: str
    start: int | None
    end: int | None
    bits: int | None


@injectable(as_type=SnapshotMigrator, qualifier="v11_to_v12", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class SnapshotV11ToV12Migrator(SnapshotMigrator):
    def source_version(self) -> int:
        return 11

    def target_version(self) -> int:
        return 12

    def migrate(self, state: SnapshotMigrationState) -> SnapshotMigrationState:
        candidate = replace(state.current, version=12)
        changes = list(state.changes)
        if candidate.kind == "packet":
            elements: list[dict[str, object]] = []
            for index, element in enumerate(candidate.elements):
                path = f"/elements/{index}"
                if set(element) != {"$type", "fields"} or element["$type"] != "mermaiden/element/packet/packet_field":
                    raise SnapshotUpgradeError("Unsupported legacy Packet element.", (path,))
                fields = LegacyPacketFields.model_validate(element["fields"])
                position = self.position(fields, path)
                elements.append(
                    {
                        "$type": element["$type"],
                        "fields": {"id": fields.id, "label": fields.label, "position": position},
                    }
                )
                changes.append(SnapshotChange((path,), "Convert Packet coordinates to a tagged position.", {}, False))
            candidate = replace(candidate, elements=tuple(elements))
        if candidate.kind == "flowchart":
            fields = dict(SnapshotMapping.model_validate(candidate.configuration["fields"]).root)
            unexpected = sorted(fields.keys() & {"step_duration", "step_numbers"})
            if unexpected:
                raise SnapshotUpgradeError(
                    "Source configuration contains fields introduced in v12.",
                    tuple(f"/configuration/fields/{name}" for name in unexpected),
                )
            fields.update({"step_duration": 1, "step_numbers": False})
            candidate = replace(candidate, configuration={**candidate.configuration, "fields": fields})
        return SnapshotMigrationState(state.original, candidate, tuple(changes))

    def position(self, fields: LegacyPacketFields, path: str) -> dict[str, object]:
        if fields.bits is not None and fields.start is None and fields.end is None and fields.bits > 0:
            value: dict[str, object] = {
                "$type": "mermaiden/value/packet/packet_bit_count",
                "fields": {"kind": "bits", "bits": fields.bits},
            }
        elif fields.start is not None and fields.start >= 0 and fields.bits is None:
            end = fields.start if fields.end is None else fields.end
            if end < fields.start:
                raise SnapshotUpgradeError("Packet range end precedes its start.", (path,))
            value = {
                "$type": "mermaiden/value/packet/packet_range",
                "fields": {"kind": "range", "start": fields.start, "end": end},
            }
        else:
            raise SnapshotUpgradeError(
                "Packet position must select exactly one valid range or bit-count mode.", (path,)
            )
        return {"$type": "mermaiden/value/packet/packet_position", "fields": {"root": value}}
