from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


class Annotatable(ABC):
    pass


@runtime_checkable
class Element(Protocol):
    pass


class Relation(Protocol):
    pass


class Annotation(ABC):
    @property
    @abstractmethod
    def targets(self) -> tuple[Annotatable, ...]:
        pass


class Diagram(ABC):
    @property
    @abstractmethod
    def elements(self) -> tuple[Element, ...]:
        pass

    @property
    @abstractmethod
    def relations(self) -> tuple[Relation, ...]:
        pass


@runtime_checkable
class Constraint(Protocol):
    @abstractmethod
    def is_satisfied_by(self, diagram: Diagram) -> bool:
        raise NotImplementedError
