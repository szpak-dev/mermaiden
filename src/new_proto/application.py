from dataclasses import dataclass

from wireup import SyncContainer, create_sync_container

import new_proto


@dataclass(frozen=True, slots=True)
class Application:
    @staticmethod
    def create() -> SyncContainer:
        return create_sync_container(injectables=[new_proto], config={})
