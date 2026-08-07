from typing import ClassVar

from wireup import injectable

from ...domain import DiagramMembersConstraint
from ..annotations import Note
from ..elements import FlowGroup, FlowNode
from ..relations import Flow
from .constraint import FlowchartConstraint


@injectable(as_type=FlowchartConstraint, qualifier="flowchart_members")
class FlowchartContainsOnlyFlowchartMembers(DiagramMembersConstraint, FlowchartConstraint):
    element_types: ClassVar = (FlowNode, FlowGroup)
    relation_types: ClassVar = (Flow,)
    annotation_types: ClassVar = (Note,)
    element_description: ClassVar[str] = "a flowchart element"
    relation_description: ClassVar[str] = "a flow"
    annotation_description: ClassVar[str] = "a flowchart note"

    @property
    def code(self) -> str:
        return "flowchart.member_type"
