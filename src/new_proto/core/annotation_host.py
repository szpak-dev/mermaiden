from .annotation import Annotation
from .base import Element
from abc import abstractmethod


class AnnotationHost(Element):
    @property
    @abstractmethod
    def annotations(self) -> tuple[Annotation, ...]:
        pass

    @abstractmethod
    def add_annotation(self, annotation: Annotation) -> None:
        pass

    @abstractmethod
    def remove_annotation(self, annotation_id: str) -> Annotation:
        pass
