from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


class Annotatable(ABC):
    pass


class Annotation(ABC):
    @property
    @abstractmethod
    def targets(self) -> tuple[Annotatable, ...]:
        pass
