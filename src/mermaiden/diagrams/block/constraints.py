from wireup import injectable

from ..domain import DiagramConstraint


@injectable(qualifier="block_structure")
class BlockDiagramConstraint(DiagramConstraint):
    pass
