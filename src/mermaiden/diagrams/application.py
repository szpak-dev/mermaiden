from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from wireup import injectable

from .domain import DiagramModel


@dataclass(frozen=True, slots=True)
class DiagramInfo:
    id: str
    name: str
    diagram_type: type[DiagramModel]
    config_key: str
    schema_definition: str

    @classmethod
    def from_diagram(cls, diagram: DiagramModel) -> "DiagramInfo":
        return cls(
            id=diagram.definition.syntax,
            name=diagram.definition.name,
            diagram_type=type(diagram),
            config_key=diagram.definition.config_key,
            schema_definition=diagram.definition.schema_definition,
        )

@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramsApplication:
    diagrams: Sequence[DiagramModel]

    def available(self) -> tuple[DiagramInfo, ...]:
        return tuple(sorted((DiagramInfo.from_diagram(diagram) for diagram in self.diagrams), key=lambda item: item.id))

    def get(self, diagram_id: str) -> DiagramInfo:
        for diagram in self.available():
            if diagram.id == diagram_id:
                return diagram
        available = ", ".join(diagram.id for diagram in self.available())
        raise KeyError(f"Unknown diagram '{diagram_id}'. Available diagrams: {available}.")

    def get_by_config_key(self, config_key: str) -> DiagramInfo:
        for diagram in self.available():
            if diagram.definition.config_key == config_key:
                return diagram
        available = ", ".join(diagram.config_key for diagram in self.available())
        raise KeyError(f"Unknown Mermaid config key '{config_key}'. Available config keys: {available}.")

    def get_diagram(self, diagram_id: str) -> DiagramModel:
        for diagram in self.diagrams:
            if diagram.definition.syntax == diagram_id:
                return diagram
        self.get(diagram_id)
        raise AssertionError("Unreachable.")

    def find(self, diagram: DiagramModel) -> DiagramInfo | None:
        return next((item for item in self.available() if item.id == diagram.kind), None)

    def __iter__(self) -> Iterator[DiagramInfo]:
        return iter(self.available())
