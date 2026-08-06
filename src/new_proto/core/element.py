from new_proto.interface import Interface


class Element(Interface):
    pass


class Container(Element):
    @Interface.prop
    def children(self) -> tuple[Element, ...]: ...


class Entity(Element):
    @Interface.prop
    def id(self) -> str: ...
