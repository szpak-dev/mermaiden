from abc import ABC, abstractmethod


class Relation(ABC):
    """An independently identified relationship between diagram elements."""

    @property
    @abstractmethod
    def id(self) -> str: ...

    @property
    @abstractmethod
    def participant_ids(self) -> tuple[str, ...]: ...


class DirectedRelation(Relation, ABC):
    """A binary relation whose endpoints have source and target roles."""

    @property
    @abstractmethod
    def source_id(self) -> str: ...

    @property
    @abstractmethod
    def target_id(self) -> str: ...

    @property
    def participant_ids(self) -> tuple[str, str]:
        return self.source_id, self.target_id

