from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ...core.domain import DiagramSnapshotContractIdentity

SNAPSHOT_VERSION = 7


class SnapshotError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class DiagramSnapshot:
    version: int
    kind: str
    draft: bool
    configuration: Mapping[str, object]
    elements: tuple[Mapping[str, object], ...]
    relations: tuple[Mapping[str, object], ...]
    annotations: tuple[Mapping[str, object], ...]
    properties: Mapping[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "kind": self.kind,
            "draft": self.draft,
            "configuration": dict(self.configuration),
            "elements": list(self.elements),
            "relations": list(self.relations),
            "annotations": list(self.annotations),
            "properties": dict(self.properties),
        }


@dataclass(frozen=True, slots=True)
class SnapshotType:
    discriminator: str
    value_type: type[Any]


@dataclass(frozen=True, slots=True)
class SnapshotContract:
    owner: str
    configuration: SnapshotType
    elements: tuple[SnapshotType, ...]
    relations: tuple[SnapshotType, ...]
    annotations: tuple[SnapshotType, ...]
    values: tuple[SnapshotType, ...]
    enums: tuple[SnapshotType, ...]
    properties: Mapping[str, object]

    @property
    def types(self) -> tuple[SnapshotType, ...]:
        return (
            self.configuration,
            *self.elements,
            *self.relations,
            *self.annotations,
            *self.values,
            *self.enums,
        )


class SnapshotTypeRegistry(ABC):
    @abstractmethod
    def contract(self, owner: str) -> SnapshotContract: ...

    def identity(self, owner: str) -> DiagramSnapshotContractIdentity:
        contract = self.contract(owner)
        return DiagramSnapshotContractIdentity(
            kind=contract.owner,
            snapshot_version=SNAPSHOT_VERSION,
            registry_fingerprint=self.fingerprint,
        )

    @abstractmethod
    def reference(self, owner: str, value_type: type[object]) -> str: ...

    @abstractmethod
    def resolve(self, owner: str, discriminator: str, expected: Any) -> type[Any]: ...

    @property
    @abstractmethod
    def fingerprint(self) -> str: ...
