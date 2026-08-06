from abc import ABC, abstractmethod


class Annotatable(ABC):
    pass


class Element(ABC):
    pass


class Relation(ABC):
    pass


class Constraint(ABC):
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
