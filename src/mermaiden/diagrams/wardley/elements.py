from enum import StrEnum
from typing import Annotated

from pydantic import Field

from ...core.domain import Container, Entity


class ComponentDecorator(StrEnum):
    INERTIA = "inertia"
    BUILD = "build"
    BUY = "buy"
    OUTSOURCE = "outsource"
    MARKET = "market"


class Component(Entity):
    visibility: float = 0
    evolution: float = 0
    decorators: Annotated[tuple[ComponentDecorator, ...], Field(max_length=1)] = ()
    anchor: bool = False


class Evolution(Entity):
    target: float = 0


class Pipeline(Container):
    pass
