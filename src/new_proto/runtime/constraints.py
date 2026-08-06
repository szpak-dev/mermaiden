from abc import abstractmethod

from ..core.constraint import (
    Constraint,
    ElementPresence,
    IncomingRelationDegree,
    OutgoingRelationDegree,
    RelationDegree,
)
from ..core.diagram import DiagramContents
from ..core.element import Element
from ..core.relation import DirectedRelation, Relation


class BoundedRule(Constraint):
    minimum_count = 0
    maximum_count: int | None = None

    def __init__(self):
        self._validate_bounds(self.minimum_count, self.maximum_count)

    @property
    def minimum(self) -> int:
        return self.minimum_count

    @property
    def maximum(self) -> int | None:
        return self.maximum_count

    def _within_bounds(self, value: int) -> bool:
        return value >= self.minimum_count and (
            self.maximum_count is None or value <= self.maximum_count
        )

    @staticmethod
    def _validate_bounds(minimum: int, maximum: int | None) -> None:
        if minimum < 0 or maximum is not None and maximum < minimum:
            raise ValueError("Constraint bounds must be non-negative and ordered.")


class ElementPresenceRule(BoundedRule, ElementPresence):
    element_type: type[Element]

    @property
    def element(self) -> type[Element]:
        return self.element_type

    def is_satisfied_by(self, diagram_contents: DiagramContents) -> bool:
        count = sum(isinstance(item, self.element_type) for item in diagram_contents.elements)
        return self._within_bounds(count)


class ExactlyOne(ElementPresenceRule):
    minimum_count = 1
    maximum_count = 1


class RelationDegreeRule(BoundedRule, RelationDegree):
    element_type: type[Element]
    relation_type: type[Relation]

    @property
    def element(self) -> type[Element]:
        return self.element_type

    @property
    def relation(self) -> type[Relation]:
        return self.relation_type

    def is_satisfied_by(self, diagram_contents: DiagramContents) -> bool:
        return all(
            self._within_bounds(self._degree_of(element, diagram_contents))
            for element in diagram_contents.elements
            if isinstance(element, self.element_type)
        )

    def _degree_of(self, element: Element, diagram_contents: DiagramContents) -> int:
        return sum(
            isinstance(relation, self.relation_type)
            and any(participant is element for participant in relation.participants)
            for relation in diagram_contents.relations
        )


class DirectedRelationDegreeRule(RelationDegreeRule):
    def _degree_of(self, element: Element, diagram_contents: DiagramContents) -> int:
        return sum(
            isinstance(relation, self.relation_type)
            and isinstance(relation, DirectedRelation)
            and self._matches_endpoint(relation, element)
            for relation in diagram_contents.relations
        )

    @abstractmethod
    def _matches_endpoint(self, relation: DirectedRelation, element: Element) -> bool: ...


class IncomingRelationDegreeRule(DirectedRelationDegreeRule, IncomingRelationDegree):
    def _matches_endpoint(self, relation: DirectedRelation, element: Element) -> bool:
        return relation.target is element


class OutgoingRelationDegreeRule(DirectedRelationDegreeRule, OutgoingRelationDegree):
    def _matches_endpoint(self, relation: DirectedRelation, element: Element) -> bool:
        return relation.source is element


class NoIncoming(IncomingRelationDegreeRule):
    maximum_count = 0


class NoOutgoing(OutgoingRelationDegreeRule):
    maximum_count = 0


class AtLeastOneIncoming(IncomingRelationDegreeRule):
    minimum_count = 1


class AtLeastOneOutgoing(OutgoingRelationDegreeRule):
    minimum_count = 1


class SingleIncoming(IncomingRelationDegreeRule):
    minimum_count = 1
    maximum_count = 1


class SingleOutgoing(OutgoingRelationDegreeRule):
    minimum_count = 1
    maximum_count = 1


class MultipleIncoming(IncomingRelationDegreeRule):
    minimum_count = 2


class MultipleOutgoing(OutgoingRelationDegreeRule):
    minimum_count = 2
