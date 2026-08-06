from new_proto.interface import Interface

from .element import Element


class Relation(Interface):
    pass


class DirectedRelation(Relation):
    @Interface.prop
    def source(self) -> Element: ...

    @Interface.prop
    def target(self) -> Element: ...


class Association(Relation):
    @Interface.prop
    def participants(self) -> tuple[Element, ...]: ...
