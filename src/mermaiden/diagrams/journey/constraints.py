from wireup import injectable

from ..domain import DiagramConstraint


@injectable(qualifier="journey_structure")
class JourneyConstraint(DiagramConstraint):
    pass
