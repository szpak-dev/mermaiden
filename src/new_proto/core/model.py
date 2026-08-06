from abc import ABC, abstractmethod
from uuid import uuid4

from .behaviours import Behaviour


class Element(ABC):
    def __init__(self) -> None:
        self._parent: Element | None = None

    @property
    @abstractmethod
    def kind(self) -> str:
        pass

    @property
    def parent(self) -> Element | None:
        return self._parent

    def behaviours(self) -> tuple[Behaviour, ...]:
        return ()

    def root(self) -> Diagram:
        current: Element = self
        while current.parent is not None:
            current = current.parent
        if not isinstance(current, Diagram):
            raise ValueError(f"{self.kind} is not attached to a diagram")
        return current

    def new_id(self, prefix: str) -> str:
        return f"{prefix}:{uuid4().hex}"


class Entity(Element, ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        pass


class Occurrence(Element, ABC):
    pass


class Container(Element, ABC):
    def _init_container(self) -> None:
        self._children: list[Element] = []

    @property
    def elements(self) -> tuple[Element, ...]:
        return tuple(self._children)

    @abstractmethod
    def accepts(self, child: Element) -> bool:
        pass

    def add(self, child: Element, *, after_id: str | None = None) -> None:
        if not self.accepts(child):
            raise TypeError(f"{self.kind} cannot contain {child.kind}")
        if child.parent is not None:
            raise ValueError(f"{child.kind} is already owned by {child.parent.kind}")
        self._insert(child, after_id=after_id)
        child._parent = self

    def remove(self, child_id: str) -> Element:
        child = self._direct_entity(child_id)
        self._children.remove(child)
        child._parent = None
        return child

    def move(self, child_id: str, *, after_id: str | None = None) -> None:
        child = self._direct_entity(child_id)
        self._children.remove(child)
        self._insert(child, after_id=after_id)

    def _insert(self, child: Element, *, after_id: str | None) -> None:
        if after_id is None:
            self._children.insert(0, child)
            return
        sibling = self._direct_entity(after_id)
        self._children.insert(self._children.index(sibling) + 1, child)

    def _direct_entity(self, element_id: str) -> Entity:
        for child in self._children:
            if isinstance(child, Entity) and child.id == element_id:
                return child
        raise KeyError(f"{self.kind} has no direct child {element_id!r}")

    def behaviours(self) -> tuple[Behaviour, ...]:
        from .behaviours import MoveChild, RemoveChild

        return (*super().behaviours(), RemoveChild(self), MoveChild(self))


class Relation(Element, ABC):
    @property
    @abstractmethod
    def endpoints(self) -> tuple[str, ...]:
        pass


class RelationHost(Element, ABC):
    def _init_relation_host(self) -> None:
        self._relations: list[Relation] = []

    @property
    def relations(self) -> tuple[Relation, ...]:
        return tuple(self._relations)

    def add_relation(self, relation: Relation) -> None:
        if relation.parent is not None:
            raise ValueError("Relation already belongs to a host")
        self._relations.append(relation)
        relation._parent = self

    def remove_relation(self, relation_id: str) -> Relation:
        for relation in self._relations:
            if isinstance(relation, Entity) and relation.id == relation_id:
                self._relations.remove(relation)
                relation._parent = None
                return relation
        raise KeyError(f"No relation {relation_id!r}")

    def behaviours(self) -> tuple[Behaviour, ...]:
        from .behaviours import RemoveRelation

        return (*super().behaviours(), RemoveRelation(self))


class Annotation(Element, ABC):
    @property
    @abstractmethod
    def targets(self) -> tuple[str, ...]:
        pass


class AnnotationHost(Element, ABC):
    def _init_annotation_host(self) -> None:
        self._annotations: list[Annotation] = []

    @property
    def annotations(self) -> tuple[Annotation, ...]:
        return tuple(self._annotations)

    def add_annotation(self, annotation: Annotation) -> None:
        if annotation.parent is not None:
            raise ValueError("Annotation already belongs to a host")
        self._annotations.append(annotation)
        annotation._parent = self

    def remove_annotation(self, annotation_id: str) -> Annotation:
        for annotation in self._annotations:
            if isinstance(annotation, Entity) and annotation.id == annotation_id:
                self._annotations.remove(annotation)
                annotation._parent = None
                return annotation
        raise KeyError(f"No annotation {annotation_id!r}")

    def behaviours(self) -> tuple[Behaviour, ...]:
        from .behaviours import RemoveAnnotation

        return (*super().behaviours(), RemoveAnnotation(self))


class Diagram(Container, RelationHost, AnnotationHost, ABC):
    def __init__(self, *, title: str = "") -> None:
        Element.__init__(self)
        self._init_container()
        self._init_relation_host()
        self._init_annotation_host()
        self.title = title

    @property
    def kind(self) -> str:
        return "diagram"

    @property
    @abstractmethod
    def diagram_type(self) -> str:
        pass

    @property
    def elements(self) -> tuple[Element, ...]:
        return (*Container.elements.fget(self), *self.relations, *self.annotations)

    def find(self, element_id: str) -> Entity:
        for element in self._walk(self.elements):
            if isinstance(element, Entity) and element.id == element_id:
                return element
        raise KeyError(f"{self.diagram_type} has no element {element_id!r}")

    def _walk(self, elements: tuple[Element, ...]):
        for element in elements:
            yield element
            if isinstance(element, Container):
                yield from self._walk(element.elements)


__all__ = [
    "Annotation",
    "AnnotationHost",
    "Container",
    "Diagram",
    "Element",
    "Entity",
    "Occurrence",
    "Relation",
    "RelationHost",
]
