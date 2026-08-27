from wireup import injectable

from ..domain import DiagramConstraint


@injectable(qualifier="gantt_structure")
class GanttConstraint(DiagramConstraint):
    pass
