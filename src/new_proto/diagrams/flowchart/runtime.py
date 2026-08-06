from dataclasses import dataclass, field
from collections.abc import Sequence
from wireup import injectable

from ...runtime.diagram import InMemoryDiagram
from ...core.constraint import Constraint

from .diagram import Flowchart
from .elements import Action, FlowNode, Start, Termination
from .relations import Flow


@injectable(lifetime="transient")
@dataclass(frozen=True)
class InMemoryFlowchart(InMemoryDiagram, Flowchart):
    _constraints: Sequence[Constraint] = field()

    def open_diagram(self) -> None:
        self.add_element(Start("start"))
        self.add_element(Termination("termination"))

    def constraints(self) -> tuple[Constraint, ...]:
        return tuple(self._constraints)

    def violations(self) -> tuple[Constraint, ...]:
        contents = self.contents()
        return tuple(
            constraint
            for constraint in self.constraints()
            if not constraint.is_satisfied_by(contents)
        )

    def add_action(self) -> str:
        id = f"action_{len(self.contents().elements) + 1}"
        self.add_element(Action(id))
        return id

    def add_flow(self, source_id: str, target_id: str) -> None:
        source = self._resolve_element(source_id)
        target = self._resolve_element(target_id)
        if not isinstance(source, FlowNode) or not isinstance(target, FlowNode):
            raise TypeError("Flow endpoints must be flow nodes.")
        self.add_relation(Flow(source, target))
