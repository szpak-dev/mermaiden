from dataclasses import dataclass

from wireup import SyncContainer, create_sync_container

from . import runtime
from .diagrams import flowchart


@dataclass(frozen=True, slots=True)
class Application:
    """Composition root. No domain service constructs its dependencies."""

    @staticmethod
    def create() -> SyncContainer:
        return create_sync_container(injectables=[runtime, flowchart])
