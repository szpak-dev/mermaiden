from enum import StrEnum

from ...core.relation import Relation


class Port(StrEnum):
    TOP = "T"
    RIGHT = "R"
    BOTTOM = "B"
    LEFT = "L"


class Edge(Relation):
    source_port: Port = Port.RIGHT
    target_port: Port = Port.LEFT
