from collections.abc import Hashable, Iterator, Mapping
from dataclasses import dataclass

from wireup import SyncContainer, injectable

from ..runtime.snapshot import DiagramSnapshot, DiagramSnapshotCodec
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
    diagrams: Mapping[Hashable, DiagramModel]

    def available(self) -> tuple[DiagramInfo, ...]:
        return tuple(
            sorted((DiagramInfo.from_diagram(diagram) for diagram in self.diagrams.values()), key=lambda item: item.id)
        )

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

    def get_diagram(self, diagram_id: str) -> DiagramModel:
        for diagram in self.diagrams.values():
            if diagram.definition.syntax == diagram_id:
                return diagram
        self.get(diagram_id)
        raise AssertionError("Unreachable.")

    def qualifier(self, diagram_id: str) -> Hashable:
        for qualifier, diagram in self.diagrams.items():
            if diagram.definition.syntax == diagram_id:
                return qualifier
        self.get(diagram_id)
        raise AssertionError("Unreachable.")

    def find(self, diagram: DiagramModel) -> DiagramInfo | None:
        return next((item for item in self.available() if item.id == diagram.kind), None)

    def __iter__(self) -> Iterator[DiagramInfo]:
        return iter(self.available())


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramFactory:
    container: SyncContainer
    registry: DiagramsApplication

    def create(self, diagram_id: str) -> DiagramModel:
        qualifier = self.registry.qualifier(diagram_id)
        with self.container.enter_scope() as scope:
            return scope.get(DiagramModel, qualifier=qualifier)


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramPersistenceApplication:
    diagrams: DiagramFactory
    snapshots: DiagramSnapshotCodec

    def snapshot(self, diagram: DiagramModel) -> DiagramSnapshot:
        return self.snapshots.snapshot(diagram)

    def restore(self, payload: Mapping[str, object]) -> DiagramModel:
        snapshot = self.snapshots.restore(payload)
        diagram = self.diagrams.create(snapshot.kind)
        data = self.snapshots.hydrate(snapshot, diagram)
        diagram.restore_snapshot(data)
        return diagram
