from dataclasses import dataclass, replace

from wireup import injectable

from .....runtime.snapshot.value_validator import SnapshotMapping, SnapshotString
from ..domain import SnapshotChange, SnapshotMigrationState, SnapshotMigrator, SnapshotUpgradeError


@injectable(as_type=SnapshotMigrator, qualifier="v8_to_v9", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class SnapshotV8ToV9Migrator(SnapshotMigrator):
    def source_version(self) -> int:
        return 8

    def target_version(self) -> int:
        return 9

    def migrate(self, state: SnapshotMigrationState) -> SnapshotMigrationState:
        snapshot = state.current
        kind = snapshot.kind
        fields = dict(SnapshotMapping.model_validate(snapshot.configuration["fields"]).root)
        additions = self.additions(kind)
        unexpected = sorted(fields.keys() & additions.keys())
        if unexpected:
            raise SnapshotUpgradeError(
                "Source configuration contains fields introduced in v9.",
                tuple(f"/configuration/fields/{name}" for name in unexpected),
            )
        changes = state.changes
        if kind in ("classDiagram", "flowchart", "stateDiagram-v2"):
            renderer = SnapshotMapping.model_validate(fields["default_renderer"]).root
            enum_names = {
                "classDiagram": "class_renderer",
                "flowchart": "flowchart_renderer",
                "stateDiagram-v2": "state_renderer",
            }
            expected = f"mermaiden/enum/{kind}/{enum_names[kind]}"
            value = SnapshotString.model_validate(renderer["value"]).root
            allowed = ("dagre-wrapper", "elk") if kind == "flowchart" else ("dagre-d3", "dagre-wrapper", "elk")
            if set(renderer) != {"$enum", "value"} or renderer["$enum"] != expected or value not in allowed:
                raise SnapshotUpgradeError(
                    "Unsupported historical renderer.", ("/configuration/fields/default_renderer",)
                )
            layout = "elk" if value == "elk" else "dagre"
            additions["layout"] = self.wrapper(kind, "layout", layout)
            del fields["default_renderer"]
            path = "/configuration/fields/default_renderer"
            original = SnapshotMapping.model_validate(state.original.configuration["fields"]).root
            discarded: dict[str, object] = (
                {path: original["default_renderer"]} if "default_renderer" in original else {}
            )
            changes = (
                *changes,
                SnapshotChange(
                    (path, "/configuration/fields/layout"),
                    "Translate renderer selection into layout.",
                    discarded,
                    False,
                ),
            )
        candidate = replace(
            snapshot, version=9, configuration={**snapshot.configuration, "fields": {**fields, **additions}}
        )
        return SnapshotMigrationState(state.original, candidate, changes)

    def wrapper(self, kind: str, name: str, value: object) -> dict[str, object]:
        return {"$type": f"mermaiden/value/{kind}/omittable_{name}", "fields": {"root": value}}

    def additions(self, kind: str) -> dict[str, object]:
        unconfigured: dict[str, object] = {"$type": f"mermaiden/value/{kind}/unconfigured", "fields": {}}
        fields: dict[str, object] = {
            "theme": self.wrapper(kind, "theme", unconfigured),
            "look": self.wrapper(kind, "look", unconfigured),
            "layout": self.wrapper(kind, "layout", unconfigured),
        }
        if kind in (
            "classDiagram",
            "erDiagram",
            "flowchart",
            "requirementDiagram",
            "sequenceDiagram",
            "stateDiagram-v2",
            "swimlane-beta",
            "venn-beta",
        ):
            fields["theme"] = self.wrapper(
                kind, "theme", {"$enum": f"mermaiden/enum/{kind}/mermaid_theme", "value": "redux-color"}
            )
            fields["look"] = self.wrapper(
                kind, "look", {"$enum": f"mermaiden/enum/{kind}/mermaid_look", "value": "neo"}
            )
        if kind == "swimlane-beta":
            fields["layout"] = self.wrapper(kind, "layout", "swimlane")
        if kind in ("flowchart", "stateDiagram-v2"):
            fields["min_node_width"] = 120.0
        if kind == "stateDiagram-v2":
            fields["wrapping_width"] = 120.0
        if kind == "mindmap":
            fields["color_by"] = {"$enum": "mermaiden/enum/mindmap/mindmap_color_by", "value": "branch"}
        if kind == "packet":
            fields["bit_order"] = {"$enum": "mermaiden/enum/packet/packet_bit_order", "value": "ascending"}
        return fields
