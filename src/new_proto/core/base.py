from abc import ABC, abstractmethod


class Annotatable(ABC):
    pass


class Element(ABC):
    pass


class Relation(ABC):
    pass


class Annotation(ABC):
    @property
    @abstractmethod
    def targets(self) -> tuple[Annotatable, ...]:
        pass


class Diagram(ABC):
    pass
