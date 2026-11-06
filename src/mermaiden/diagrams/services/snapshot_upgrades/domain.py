from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass

from ....runtime.snapshot.domain import DiagramSnapshot, SnapshotError


@dataclass(frozen=True, slots=True)
class SnapshotChange:
    """Describe changed JSON pointers and the original values discarded by an upgrade."""

    paths: tuple[str, ...]
    description: str
    discarded: Mapping[str, object]
    requires_loss_acceptance: bool


@dataclass(frozen=True, slots=True)
class SnapshotUpgradeResult:
    """Contain a current snapshot and its ordered original-to-final change report."""

    snapshot: DiagramSnapshot
    changes: tuple[SnapshotChange, ...]


class SnapshotUpgradeError(SnapshotError):
    """Report invalid input or refused loss through JSON pointers and proposed changes."""

    def __init__(self, message: str, paths: tuple[str, ...], changes: tuple[SnapshotChange, ...] = ()) -> None:
        super().__init__(message)
        self.paths: tuple[str, ...] = paths
        self.changes: tuple[SnapshotChange, ...] = changes


@dataclass(frozen=True, slots=True)
class SnapshotMigrationState:
    original: DiagramSnapshot
    current: DiagramSnapshot
    changes: tuple[SnapshotChange, ...]


class SnapshotMigrator(ABC):
    @abstractmethod
    def source_version(self) -> int: ...

    @abstractmethod
    def target_version(self) -> int: ...

    @abstractmethod
    def migrate(self, state: SnapshotMigrationState) -> SnapshotMigrationState: ...
