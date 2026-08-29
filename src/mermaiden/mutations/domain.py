from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence

from ..core.constraint import ChangeReport
from ..runtime.diagrams.aggregate import DiagramAggregate


class MutationKernel(ABC):
    @abstractmethod
    def update_element(
        self,
        diagram: DiagramAggregate,
        id: str,
        kind: str,
        changes: Mapping[str, object],
    ) -> ChangeReport: ...

    @abstractmethod
    def update_relation(
        self,
        diagram: DiagramAggregate,
        id: str,
        kind: str,
        changes: Mapping[str, object],
    ) -> ChangeReport: ...

    @abstractmethod
    def update_annotation(
        self,
        diagram: DiagramAggregate,
        id: str,
        kind: str,
        changes: Mapping[str, object],
    ) -> ChangeReport: ...

    @abstractmethod
    def move_element(
        self,
        diagram: DiagramAggregate,
        id: str,
        kind: str,
        parent_id: str,
        position: int | None,
    ) -> ChangeReport: ...

    @abstractmethod
    def reorder_elements(
        self,
        diagram: DiagramAggregate,
        parent_id: str,
        element_ids: Sequence[str],
    ) -> ChangeReport: ...
