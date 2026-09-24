from abc import ABC, abstractmethod
from collections.abc import Mapping

from ...core.domain import Annotation, CommandPayload, Element, Relation


class MutationPayloadFactory(ABC):
    @abstractmethod
    def element(
        self,
        diagram_name: str,
        object_types: Mapping[str, type[Element]],
    ) -> CommandPayload: ...

    @abstractmethod
    def relation(
        self,
        diagram_name: str,
        object_types: Mapping[str, type[Relation]],
    ) -> CommandPayload: ...

    @abstractmethod
    def annotation(
        self,
        diagram_name: str,
        object_types: Mapping[str, type[Annotation]],
    ) -> CommandPayload: ...

    @abstractmethod
    def move_element(
        self,
        diagram_name: str,
        object_types: Mapping[str, type[Element]],
    ) -> CommandPayload: ...
