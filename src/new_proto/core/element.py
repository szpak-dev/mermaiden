from new_proto.interface import Interface


class Element(Interface):
    pass


class Container(Element):
    children: tuple[Element, ...]


class Entity(Element):
    id: str
