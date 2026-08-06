from new_proto.interface import Interface

from ...core.constraint import Constraint
from ...core.diagram import Diagram


class Flowchart(Diagram):
    @Interface.method
    def constraints(self) -> tuple[Constraint, ...]: ...

    @Interface.method
    def violations(self) -> tuple[Constraint, ...]: ...

    @Interface.method
    def add_action(self) -> str: ...

    @Interface.method
    def add_flow(self, source_id: str, target_id: str) -> None: ...
