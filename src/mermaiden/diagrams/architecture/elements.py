from pydantic import Field

from ...core.element import Container, Entity
from .relations import Alignment, AlignmentAxis


class ArchitectureGroup(Container):
    columns: int = Field(default=1, ge=1)

    @property
    def grid_alignments(self) -> tuple[Alignment, ...]:
        member_ids = tuple(item.id for item in self.elements if isinstance(item, Service | Junction))
        rows = tuple(member_ids[index : index + self.columns] for index in range(0, len(member_ids), self.columns))
        columns = tuple(member_ids[index :: self.columns] for index in range(min(self.columns, len(member_ids))))
        return tuple(
            Alignment(
                id=f"{self.id}_{axis.value}_{index}",
                element_ids=members,
                axis=axis,
            )
            for axis, groups in ((AlignmentAxis.ROW, rows), (AlignmentAxis.COLUMN, columns))
            for index, members in enumerate(groups, start=1)
            if len(members) >= 2
        )


class Service(Entity):
    pass


class Junction(Entity):
    pass
