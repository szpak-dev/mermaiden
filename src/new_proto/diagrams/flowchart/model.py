from abc import ABC, abstractmethod

from ...core.base import Diagram
from ...core.element import Container, Entity
from ...core.relation import DirectedRelation


class FlowNode(Entity, ABC):
    pass


class FlowNodeGroup(Entity, Container, ABC):
    @property
    @abstractmethod
    def children(self) -> tuple[FlowNode, ...]:
        pass


class Flow(DirectedRelation, ABC):
    @property
    @abstractmethod
    def source(self) -> FlowNode:
        pass

    @property
    @abstractmethod
    def target(self) -> FlowNode:
        pass


class Flowchart(Diagram, ABC):
    @property
    @abstractmethod
    def elements(self) -> tuple[FlowNode | FlowNodeGroup, ...]:
        pass

    @property
    @abstractmethod
    def relations(self) -> tuple[Flow, ...]:
        pass
