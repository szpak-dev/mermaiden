from dataclasses import dataclass, field

from .annotations import Annotations
from .elements import Elements
from .relations import Relations
from .state import DiagramState
from .transaction import ChangeTransaction


@dataclass(frozen=True, slots=True)
class DiagramRuntime:
    state: DiagramState = field(default_factory=DiagramState)
    elements: Elements = field(init=False)
    relations: Relations = field(init=False)
    annotations: Annotations = field(init=False)
    transaction: ChangeTransaction = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "elements", Elements(self.state))
        object.__setattr__(self, "relations", Relations(self.state))
        object.__setattr__(self, "annotations", Annotations(self.state))
        object.__setattr__(self, "transaction", ChangeTransaction(self.state))
