from typing import runtime_checkable

from .base import Element, Relation


@runtime_checkable
class DirectedRelation(Relation):
   source: Element
   target: Element


@runtime_checkable
class Association(Relation):
    participants: tuple[Element, ...]
