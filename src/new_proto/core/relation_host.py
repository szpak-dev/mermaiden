from .base import Element
from .relation import Relation
from abc import abstractmethod


class RelationHost(Element):
    @property
    @abstractmethod
    def relations(self) -> tuple[Relation, ...]:
        pass

    @abstractmethod
    def add_relation(self, relation: Relation) -> None:
        pass

    @abstractmethod
    def remove_relation(self, relation_id: str) -> Relation:
        pass
