from dataclasses import dataclass

from wireup import SyncContainer, create_sync_container

import mermaiden

from .diagrams.application import DiagramInfo, DiagramsApplication


@dataclass(frozen=True, slots=True)
class Application:
    container: SyncContainer

    @classmethod
    def create(cls) -> "Application":
        return cls(create_sync_container(injectables=[mermaiden], config={}))

    def available_diagrams(self) -> tuple[DiagramInfo, ...]:
        with self.container.enter_scope() as scope:
            return scope.get(DiagramsApplication).available()

    def diagram_info(self, diagram_id: str) -> DiagramInfo:
        with self.container.enter_scope() as scope:
            return scope.get(DiagramsApplication).get(diagram_id)
