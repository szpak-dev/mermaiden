from typing import ClassVar

from wireup import injectable

from ...domain import DiagramMembersConstraint
from ..elements import Category, Cause, Effect
from ..relations import CauseRelation
from .constraint import IshikawaDiagramConstraint


@injectable(as_type=IshikawaDiagramConstraint, qualifier="ishikawa_members")
class IshikawaDiagramMembers(DiagramMembersConstraint, IshikawaDiagramConstraint):
    element_types: ClassVar = (Effect, Cause, Category,)
    relation_types: ClassVar = (CauseRelation,)
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in Ishikawa diagram"
    relation_description: ClassVar[str] = "valid in Ishikawa diagram"
    annotation_description: ClassVar[str] = "valid in Ishikawa diagram"

    @property
    def code(self) -> str:
        return "ishikawa.member_type"
