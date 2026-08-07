from wireup import injectable

from ....core.constraint import ConstraintDiagram, ConstraintLevel, Violation
from ..elements import RadarAxis, RadarCurve
from .constraint import RadarConstraint


@injectable(as_type=RadarConstraint, qualifier="radar_structure")
class RadarStructure(RadarConstraint):
    @property
    def code(self) -> str:
        return "radar.structure"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        axes = tuple(item for item in diagram.root_elements if isinstance(item, RadarAxis))
        return tuple(
            self.violation(
                f"Radar curve '{item.id}' has {len(item.values)} values but the diagram has {len(axes)} axes.",
                path=f"elements.{item.id}",
            )
            for item in diagram.root_elements
            if isinstance(item, RadarCurve) and len(item.values) != len(axes)
        )
