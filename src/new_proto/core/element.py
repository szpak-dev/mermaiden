from typing import runtime_checkable

from .base import Element


@runtime_checkable
class Container(Element):
    children: tuple[Element, ...]


@runtime_checkable
class Entity(Element):
    id: str
