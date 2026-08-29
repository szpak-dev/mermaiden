from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence

from ..core.annotation import Annotation
from ..core.constraint import ChangeReport
from ..core.element import Element
from ..core.relation import Relation
from ..domain import CommandPayloadType
from ..runtime.diagrams.aggregate import DiagramAggregate


class MutationPayloadFactory(ABC):
    @abstractmethod
    def element(
        self,
        diagram_name: str,
        object_types: Mapping[str, type[Element]],
    ) -> CommandPayloadType: ...

    @abstractmethod
    def relation(
        self,
        diagram_name: str,
        object_types: Mapping[str, type[Relation]],
    ) -> CommandPayloadType: ...

    @abstractmethod
    def annotation(
        self,
        diagram_name: str,
        object_types: Mapping[str, type[Annotation]],
    ) -> CommandPayloadType: ...


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
