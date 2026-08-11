

from wireup import injectable

from ..domain import DiagramConstraint


@injectable(qualifier="sequence_structure")
class SequenceConstraint(DiagramConstraint):
    pass
