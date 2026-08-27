from wireup import injectable

from ..domain import DiagramConstraint


@injectable(qualifier="railroad_structure")
class RailroadDiagramConstraint(DiagramConstraint):
    pass
