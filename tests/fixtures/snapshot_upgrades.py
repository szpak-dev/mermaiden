from dataclasses import dataclass
from pathlib import Path

from pydantic import TypeAdapter


@dataclass(frozen=True, slots=True)
class SnapshotExamples:
    def load(self, name: str) -> dict[str, object]:
        path = Path(__file__).parent / "snapshots" / name
        return TypeAdapter(dict[str, object]).validate_json(path.read_text())

    def mapping(self, value: object) -> dict[str, object]:
        return TypeAdapter(dict[str, object]).validate_python(value, strict=True)

    def objects(self, value: object) -> list[dict[str, object]]:
        return TypeAdapter(list[dict[str, object]]).validate_python(value, strict=True)

    def configured(self, payload: dict[str, object], changes: dict[str, object]) -> dict[str, object]:
        configuration = self.mapping(payload["configuration"])
        fields = self.mapping(configuration["fields"])
        return {**payload, "configuration": {**configuration, "fields": {**fields, **changes}}}

    def packet(self, payload: dict[str, object], coordinates: dict[str, object]) -> dict[str, object]:
        return {
            **payload,
            "version": 11,
            "draft": False,
            "elements": [
                {
                    "$type": "mermaiden/element/packet/packet_field",
                    "fields": {"id": "field_example", "label": "Field example", **coordinates},
                }
            ],
        }
