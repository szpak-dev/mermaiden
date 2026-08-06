import pytest
from wireup import SyncContainer, create_sync_container

from new_proto import runtime
from new_proto.core import ChangeRejected, ConstraintLevel, Container, Diagram


@pytest.fixture(scope="module")
def container() -> SyncContainer:
    return create_sync_container(injectables=[runtime])


def test_empty_scoped_diagram_is_ready_but_advisory_invalid(container: SyncContainer) -> None:
    with container.enter_scope() as scope:
        diagram = scope.get(Diagram)

        report = diagram.validate()

        assert diagram.id == "diagram"
        assert report.can_commit
        assert not report.is_valid
        assert report.violations[0].level is ConstraintLevel.ADVISORY


def test_observer_reports_before_and_after_constraint_delta(container: SyncContainer) -> None:
    with container.enter_scope() as scope:
        diagram = scope.get(Diagram)

        result = diagram.add_entity("customer", "Customer")

        assert result.accepted
        assert result.introduced == ()
        assert result.resolved[0].code == "structure.elements_exist"
        assert diagram.validate().is_valid


def test_composite_containment_and_small_traversal_api(container: SyncContainer) -> None:
    with container.enter_scope() as scope:
        diagram = scope.get(Diagram)
        diagram.add_container("system", "System")
        diagram.add_container("backend", "Backend", "system")
        diagram.add_entity("api", "API", "backend")
        diagram.add_entity("database", "Database")
        diagram.connect("writes", ("api", "database"), "writes")

        system = diagram.find_element("system")

        assert isinstance(system, Container)
        assert [item.id for item in diagram.walk_elements()] == ["system", "backend", "api", "database"]
        assert [item.id for item in diagram.walk_elements("backend")] == ["api"]
        assert [item.id for item in diagram.find_relations("api")] == ["writes"]


def test_blocking_constraint_rolls_candidate_back_atomically(container: SyncContainer) -> None:
    with container.enter_scope() as scope:
        diagram = scope.get(Diagram)
        diagram.add_entity("api", "API")

        with pytest.raises(ChangeRejected, match="requires at least two elements"):
            diagram.connect("broken", ("api",))

        assert diagram.find_relations() == ()


def test_local_operation_error_is_actionable_and_preserves_state(container: SyncContainer) -> None:
    with container.enter_scope() as scope:
        diagram = scope.get(Diagram)
        diagram.add_entity("api", "API")

        with pytest.raises(ChangeRejected, match="already exists"):
            diagram.add_entity("api", "Duplicate")

        assert [item.label for item in diagram.walk_elements()] == ["API"]


def test_cascade_removes_the_complete_typed_dependency_closure(container: SyncContainer) -> None:
    with container.enter_scope() as scope:
        diagram = scope.get(Diagram)
        diagram.add_container("group", "Group")
        diagram.add_entity("child", "Child", "group")
        diagram.add_entity("external", "External")
        diagram.connect("flow", ("child", "external"))
        diagram.annotate("note", {"text": "important"}, relation_ids=("flow",))

        with pytest.raises(ChangeRejected, match="use cascade=True"):
            diagram.remove_element("group")
        diagram.remove_element("group", cascade=True)

        assert [item.id for item in diagram.walk_elements()] == ["external"]
        assert diagram.find_relations() == ()
        assert diagram.find_annotations() == ()


def test_wireup_scopes_isolate_diagram_state(container: SyncContainer) -> None:
    with container.enter_scope() as first_scope:
        first_scope.get(Diagram).add_entity("first", "First")
    with container.enter_scope() as second_scope:
        second = second_scope.get(Diagram)

        assert second.walk_elements() == ()
