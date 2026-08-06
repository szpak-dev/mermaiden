from ..core.element import Element
from ..core.relation import DirectedRelation, Relation


class ParticipantRelation[Participant: Element](Relation):
    def __init__(self, participants: tuple[Participant, ...]):
        self._participants = participants

    @property
    def participants(self) -> tuple[Participant, ...]:
        return self._participants


class DirectedConnection[Participant: Element](DirectedRelation):
    def __init__(self, source: Participant, target: Participant):
        self._source = source
        self._target = target

    @property
    def participants(self) -> tuple[Participant, ...]:
        return self._source, self._target

    @property
    def source(self) -> Participant:
        return self._source

    @property
    def target(self) -> Participant:
        return self._target
