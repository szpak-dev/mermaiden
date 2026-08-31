from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass

from .relations import AlignmentAxis


@dataclass(frozen=True, slots=True)
class LayoutAlignment:
    id: str
    axis: AlignmentAxis
    member_ids: tuple[str, ...]
    path: str


@dataclass(frozen=True, slots=True)
class EdgeConstraint:
    successor_id: str
    edge_id: str


@dataclass(frozen=True, slots=True)
class ConstraintGraph:
    outgoing: Mapping[str, tuple[EdgeConstraint, ...]]

    def path(self, start: str, target: str) -> tuple[str, ...]:
        queue: deque[tuple[str, tuple[str, ...]]] = deque(((start, ()),))
        visited = {start}
        while queue:
            current, edge_ids = queue.popleft()
            for constraint in self.outgoing.get(current, ()):
                path = (*edge_ids, constraint.edge_id)
                if constraint.successor_id == target:
                    return path
                if constraint.successor_id not in visited:
                    visited.add(constraint.successor_id)
                    queue.append((constraint.successor_id, path))
        return ()
