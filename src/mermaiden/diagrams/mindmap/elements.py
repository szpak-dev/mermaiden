from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container


@dataclass(frozen=True, slots=True)
class MindmapNode(Container):
    kind: ClassVar[str] = "mindmap_node"


@dataclass(frozen=True, slots=True)
class Square(MindmapNode):
    kind: ClassVar[str] = "square"


@dataclass(frozen=True, slots=True)
class RoundedSquare(MindmapNode):
    kind: ClassVar[str] = "rounded_square"


@dataclass(frozen=True, slots=True)
class Circle(MindmapNode):
    kind: ClassVar[str] = "circle"


@dataclass(frozen=True, slots=True)
class Bang(MindmapNode):
    kind: ClassVar[str] = "bang"


@dataclass(frozen=True, slots=True)
class Cloud(MindmapNode):
    kind: ClassVar[str] = "cloud"


@dataclass(frozen=True, slots=True)
class Hexagon(MindmapNode):
    kind: ClassVar[str] = "hexagon"
