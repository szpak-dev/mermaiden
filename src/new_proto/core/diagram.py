from abc import ABC, abstractmethod

from .annotation_host import AnnotationHost
from .container import Container
from .relation_host import RelationHost


class Diagram(Container, RelationHost, AnnotationHost, ABC):
    @property
    @abstractmethod
    def diagram_type(self) -> str:
        pass
