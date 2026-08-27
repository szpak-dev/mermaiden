from pydantic import BaseModel
from wireup import injectable

from ...core.diagram import Diagram
from .domain import SnapshotError


@injectable
class DiagramConfigurationReader:
    def read(self, diagram: Diagram) -> BaseModel:
        configuration = getattr(diagram, "configuration", None)
        if not isinstance(configuration, BaseModel):
            raise SnapshotError(f"Diagram '{diagram.kind}' has no persistable configuration.")
        return configuration
