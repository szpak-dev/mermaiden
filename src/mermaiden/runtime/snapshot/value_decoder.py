from dataclasses import dataclass

from wireup import injectable

from .domain import SnapshotContract, SnapshotTypeRegistry
from .value_validator import SnapshotValueValidator


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class SnapshotValueDecoder:
    types: SnapshotTypeRegistry
    values: SnapshotValueValidator

    def decode(self, value: object, contract: SnapshotContract) -> object:
        return self.values.encoded(value).decode(self.types, contract)
