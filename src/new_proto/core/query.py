from new_proto.interface import Interface

from .element import Element
from .relation import Relation


class DiagramQuery(Interface):
    elements: tuple[Element, ...]
    relations: tuple[Relation, ...]
