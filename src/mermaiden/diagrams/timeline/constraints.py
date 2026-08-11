
from wireup import injectable

from ..domain import DiagramConstraint


@injectable(qualifier="timeline_structure")
class TimelineConstraint(DiagramConstraint):
    pass
