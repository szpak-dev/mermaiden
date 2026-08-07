

from wireup import injectable

from ..domain import DiagramConstraint


@injectable(qualifier="architecture_structure")
class ArchitectureConstraint(DiagramConstraint):
    pass
