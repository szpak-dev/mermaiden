from collections import defaultdict
from collections.abc import Iterable

from wireup import injectable

from ....core.domain import ConstraintDiagram, Violation
from ..domain import ConstraintGraph, EdgeConstraint, LayoutAlignment
from ..elements import ArchitectureGroup
from ..relations import Alignment, AlignmentAxis, Edge, Port
from .structure import ArchitectureConstraint


@injectable(as_type=ArchitectureConstraint, qualifier="architecture_alignments_are_compatible")
class AlignmentsAreCompatible(ArchitectureConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        alignments = self._alignments(diagram)
        horizontal, vertical = self._edge_constraints(diagram)
        issues = [*self._overlap_issues(alignments), *self._cross_axis_issues(alignments)]
        for alignment in alignments:
            ordered = horizontal if alignment.axis is AlignmentAxis.ROW else vertical
            perpendicular = vertical if alignment.axis is AlignmentAxis.ROW else horizontal
            issues.extend(self._ordering_issues(alignment, ordered))
            issues.extend(self._perpendicular_issues(alignment, perpendicular))
        return tuple(issues)

    def _alignments(self, diagram: ConstraintDiagram) -> tuple[LayoutAlignment, ...]:
        declared = tuple(
            LayoutAlignment(item.id, item.axis, item.member_ids, f"relations.{item.id}")
            for item in diagram.find_relations()
            if isinstance(item, Alignment)
        )
        derived = tuple(
            LayoutAlignment(item.id, item.axis, item.member_ids, f"elements.{group.id}.columns")
            for group in diagram.walk_elements()
            if isinstance(group, ArchitectureGroup)
            for item in group.grid_alignments
        )
        return (*declared, *derived)

    def _overlap_issues(self, alignments: tuple[LayoutAlignment, ...]) -> Iterable[Violation]:
        owners: dict[tuple[AlignmentAxis, str], LayoutAlignment] = {}
        for alignment in alignments:
            for member_id in alignment.member_ids:
                key = (alignment.axis, member_id)
                other = owners.get(key)
                if other is not None and other.id != alignment.id:
                    yield self.violation(
                        f"Alignment '{alignment.id}' overlaps alignment '{other.id}' on {alignment.axis.value} "
                        f"member '{member_id}'.",
                        path=alignment.path,
                    )
                else:
                    owners[key] = alignment

    def _cross_axis_issues(self, alignments: tuple[LayoutAlignment, ...]) -> Iterable[Violation]:
        for index, first in enumerate(alignments):
            for second in alignments[index + 1 :]:
                shared = tuple(member_id for member_id in first.member_ids if member_id in second.member_ids)
                if first.axis is not second.axis and len(shared) >= 2:
                    members = ", ".join(f"'{member_id}'" for member_id in shared)
                    yield self.violation(
                        f"Alignments '{first.id}' and '{second.id}' constrain members {members} to both a row "
                        "and a column.",
                        path=second.path,
                    )

    def _ordering_issues(
        self,
        alignment: LayoutAlignment,
        constraints: ConstraintGraph,
    ) -> Iterable[Violation]:
        for index, earlier in enumerate(alignment.member_ids):
            for later in alignment.member_ids[index + 1 :]:
                edge_ids = constraints.path(later, earlier)
                if edge_ids:
                    yield self.violation(
                        f"Alignment '{alignment.id}' orders '{earlier}' before '{later}', but edge direction "
                        f"constraint(s) {self._edge_list(edge_ids)} require the reverse order.",
                        path=alignment.path,
                    )

    def _perpendicular_issues(
        self,
        alignment: LayoutAlignment,
        constraints: ConstraintGraph,
    ) -> Iterable[Violation]:
        for index, first in enumerate(alignment.member_ids):
            for second in alignment.member_ids[index + 1 :]:
                edge_ids = constraints.path(first, second) or constraints.path(second, first)
                if edge_ids:
                    yield self.violation(
                        f"Alignment '{alignment.id}' requires '{first}' and '{second}' to share a "
                        f"{alignment.axis.value}, but edge direction constraint(s) {self._edge_list(edge_ids)} "
                        "require separation on that axis.",
                        path=alignment.path,
                    )

    def _edge_constraints(self, diagram: ConstraintDiagram) -> tuple[ConstraintGraph, ConstraintGraph]:
        horizontal: defaultdict[str, list[EdgeConstraint]] = defaultdict(list)
        vertical: defaultdict[str, list[EdgeConstraint]] = defaultdict(list)
        for relation in diagram.find_relations():
            if not isinstance(relation, Edge) or len(relation.element_ids) != 2:
                continue
            source, target = relation.element_ids
            if (relation.source_port, relation.target_port) == (Port.RIGHT, Port.LEFT):
                horizontal[source].append(EdgeConstraint(target, relation.id))
            elif (relation.source_port, relation.target_port) == (Port.LEFT, Port.RIGHT):
                horizontal[target].append(EdgeConstraint(source, relation.id))
            elif (relation.source_port, relation.target_port) == (Port.BOTTOM, Port.TOP):
                vertical[source].append(EdgeConstraint(target, relation.id))
            elif (relation.source_port, relation.target_port) == (Port.TOP, Port.BOTTOM):
                vertical[target].append(EdgeConstraint(source, relation.id))
        return (
            ConstraintGraph({node: tuple(edges) for node, edges in horizontal.items()}),
            ConstraintGraph({node: tuple(edges) for node, edges in vertical.items()}),
        )

    def _edge_list(self, edge_ids: tuple[str, ...]) -> str:
        return ", ".join(f"'{edge_id}'" for edge_id in edge_ids)
