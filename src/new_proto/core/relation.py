from typing import Protocol, runtime_checkable


@runtime_checkable
class Relation(Protocol):
    pass



@runtime_checkable
class DirectedRelation(Relation):
   source  Element
   target: Element


@runtime_checkable
class Association(Relation):
    participants: tuple[Element, ...]
