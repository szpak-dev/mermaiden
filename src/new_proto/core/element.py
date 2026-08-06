from typing import Protocol, runtime_checkable


@runtime_checkable
class Element(Protocol):
    pass


@runtime_checkable
class Container(Element):
    children: tuple[Element, ...]


@runtime_checkable
class Entity(Element):
    id: str
