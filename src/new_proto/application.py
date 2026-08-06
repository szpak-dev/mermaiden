from dataclasses import dataclass

from wireup import SyncContainer, create_sync_container

from . import runtime
from .diagrams import flowchart


@dataclass(frozen=True, slots=True)
class Application:
    @staticmethod
    def create() -> SyncContainer:
        return create_sync_container(injectables=[runtime, flowchart])
