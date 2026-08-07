from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from wireup import injectable

from .domain import DiagramModel


@dataclass(frozen=True, slots=True)
class DiagramInfo:
    diagram: DiagramModel

    @property
    def id(self) -> str:
        return self.diagram.syntax

    @property
    def name(self) -> str:
        return self.diagram.name

    @property
    def diagram_type(self) -> type[DiagramModel]:
        return type(self.diagram)

    @property
    def config_key(self) -> str:
        return self.diagram.config_key

    @property
    def schema_definition(self) -> str:
        return self.diagram.schema_definition

    @property
    def syntax_id(self) -> str:
        return self.id


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramsApplication:
    diagrams: Sequence[DiagramModel]

    def available(self) -> tuple[DiagramInfo, ...]:
        return tuple(sorted((DiagramInfo(diagram) for diagram in self.diagrams), key=lambda item: item.id))

    def get(self, diagram_id: str) -> DiagramInfo:
        for diagram in self.available():
            if diagram.id == diagram_id:
                return diagram
        available = ", ".join(diagram.id for diagram in self.available())
        raise KeyError(f"Unknown diagram '{diagram_id}'. Available diagrams: {available}.")

    def get_by_config_key(self, config_key: str) -> DiagramInfo:
        for diagram in self.available():
            if diagram.config_key == config_key:
                return diagram
        available = ", ".join(diagram.config_key for diagram in self.available())
        raise KeyError(f"Unknown Mermaid config key '{config_key}'. Available config keys: {available}.")

    def find(self, diagram: DiagramModel) -> DiagramInfo | None:
        return next((item for item in self.available() if item.id == diagram.kind), None)

    def __iter__(self) -> Iterator[DiagramInfo]:
        return iter(self.available())
