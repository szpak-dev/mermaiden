from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast

from wireup import injectable

from .domain import SNAPSHOT_VERSION, DiagramSnapshot, SnapshotError
from .value_validator import SnapshotValueValidator


@injectable
@dataclass(frozen=True, slots=True)
class DiagramSnapshotParser:
    values: SnapshotValueValidator

    version = SNAPSHOT_VERSION

    def parse(self, payload: Mapping[str, object]) -> DiagramSnapshot:
        try:
            version = int(cast(Any, payload["version"]))
        except (KeyError, TypeError, ValueError) as error:
            raise SnapshotError("Snapshot is malformed.") from error
        if version != self.version:
            raise SnapshotError(f"Unsupported snapshot version '{version}'; expected version '{self.version}'.")
        try:
            snapshot = DiagramSnapshot(
                version=version,
                kind=self.values.string(payload["kind"], "kind"),
                draft=self.values.boolean(payload.get("draft", False), "draft"),
                configuration=self.values.mapping(payload["configuration"], "configuration"),
                elements=self.values.objects(payload["elements"], "elements"),
                relations=self.values.objects(payload["relations"], "relations"),
                annotations=self.values.objects(payload["annotations"], "annotations"),
                properties=self.values.mapping(payload.get("properties", {}), "properties"),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise SnapshotError("Snapshot is malformed.") from error
        return snapshot
