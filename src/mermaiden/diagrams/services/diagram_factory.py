from dataclasses import dataclass

from wireup import SyncContainer, injectable

from ..application import DiagramsApplication
from ..domain import DiagramModel


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramFactory:
    container: SyncContainer
    registry: DiagramsApplication

    def create(self, diagram_id: str) -> DiagramModel:
        qualifier = self.registry.qualifier(diagram_id)
        with self.container.enter_scope() as scope:
            return scope.get(DiagramModel, qualifier=qualifier)
