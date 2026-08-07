from wireup import injectable

from ....core.constraint import ConstraintDiagram, ConstraintLevel, Violation
from ..elements import Swimlane
from .constraint import SwimlaneConstraint


@injectable(as_type=SwimlaneConstraint, qualifier="lanes_are_top_level")
class LanesAreTopLevel(SwimlaneConstraint):
    @property
    def code(self) -> str:
        return "swimlane.top_level_lanes"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        root_ids = {item.id for item in diagram.root_elements if isinstance(item, Swimlane)}
        return tuple(
            self.violation(f"Lane '{lane.id}' must be top-level.", path=f"elements.{lane.id}")
            for lane in diagram.walk_elements()
            if isinstance(lane, Swimlane) and lane.id not in root_ids
        )
