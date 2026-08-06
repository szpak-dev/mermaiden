from new_proto.interface import Interface

from .element import Element


class Relation(Interface):
    pass


class DirectedRelation(Relation):
   source: Element
   target: Element


class Association(Relation):
    participants: tuple[Element, ...]
