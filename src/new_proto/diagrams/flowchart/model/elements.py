from ..elements import FlowNode, FlowNodeGroup, Start


class FlowNodeElement(FlowNode):
    def __init__(self, id: str):
        self._id = id

    @property
    def id(self) -> str:
        return self._id


class FlowNodeGroupElement(FlowNodeGroup):
    def __init__(self, id: str, children: tuple[FlowNode, ...] = ()):
        self._id = id
        self._children = children

    @property
    def id(self) -> str:
        return self._id

    @property
    def children(self) -> tuple[FlowNode, ...]:
        return self._children


class StartElement(Start, FlowNodeElement):
    pass
