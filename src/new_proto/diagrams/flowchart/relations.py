from dataclasses import dataclass

from ...core.relation import DirectedRelation


@dataclass(frozen=True, slots=True)
class Flow(DirectedRelation):
    relation_id: str
    source: str
    target: str
    label: str = ""

    @property
    def id(self) -> str:
        return self.relation_id

    @property
    def source_id(self) -> str:
        return self.source

    @property
    def target_id(self) -> str:
        return self.target


@dataclass(frozen=True, slots=True)
class ConditionalFlow(Flow):
    condition: str = ""
