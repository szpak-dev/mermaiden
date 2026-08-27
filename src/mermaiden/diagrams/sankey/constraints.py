from wireup import injectable

from ..domain import DiagramConstraint


@injectable(qualifier="sankey_structure")
class SankeyConstraint(DiagramConstraint):
    pass
