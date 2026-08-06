from abc import ABC, abstractmethod


class Behaviour(ABC):
    def __init__(self, owner: object) -> None:
        self._owner = owner

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def owner(self) -> object:
        return self._owner

    @abstractmethod
    def execute(self, **arguments: object) -> object:
        pass


class RemoveChild(Behaviour):
    @property
    def name(self) -> str:
        return "remove_child"

    def execute(self, *, child_id: str) -> object:
        from .model import Container

        owner = self.owner
        assert isinstance(owner, Container)
        return owner.remove(child_id)


class MoveChild(Behaviour):
    @property
    def name(self) -> str:
        return "move_child"

    def execute(self, *, child_id: str, after_id: str | None = None) -> None:
        from .model import Container

        owner = self.owner
        assert isinstance(owner, Container)
        owner.move(child_id, after_id=after_id)


class RemoveRelation(Behaviour):
    @property
    def name(self) -> str:
        return "remove_relation"

    def execute(self, *, relation_id: str) -> object:
        from .model import RelationHost

        owner = self.owner
        assert isinstance(owner, RelationHost)
        return owner.remove_relation(relation_id)


class RemoveAnnotation(Behaviour):
    @property
    def name(self) -> str:
        return "remove_annotation"

    def execute(self, *, annotation_id: str) -> object:
        from .model import AnnotationHost

        owner = self.owner
        assert isinstance(owner, AnnotationHost)
        return owner.remove_annotation(annotation_id)
