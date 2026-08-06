from . import diagrams, runtime

from wireup import SyncContainer, create_sync_container


def create_application() -> SyncContainer:
    return create_sync_container(injectables=[runtime, diagrams])
