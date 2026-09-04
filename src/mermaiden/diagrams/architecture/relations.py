from enum import StrEnum
from typing import Self

from pydantic import Field, model_validator

from ...core.domain import Relation


class Port(StrEnum):
    TOP = "top"
    RIGHT = "right"
    BOTTOM = "bottom"
    LEFT = "left"


class AlignmentAxis(StrEnum):
    ROW = "row"
    COLUMN = "column"


class Edge(Relation):
    source_port: Port = Port.RIGHT
    target_port: Port = Port.LEFT


class Alignment(Relation):
    element_ids: tuple[str, ...] = Field(min_length=2)
    axis: AlignmentAxis

    @property
    def member_ids(self) -> tuple[str, ...]:
        return self.element_ids

    @model_validator(mode="after")
    def require_unique_members(self) -> Self:
        if len(set(self.element_ids)) != len(self.element_ids):
            raise ValueError("Alignment members must be unique.")
        return self
