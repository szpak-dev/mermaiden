from dataclasses import FrozenInstanceError

import pytest

from new_proto import Application
from new_proto.diagrams.flowchart import (
    Action,
    ConditionalFlow,
    Decision,
    Direction,
    End,
    Flow,
    FlowchartDraft,
    FlowchartRuntime,
    FlowGroup,
    Note,
    Start,
)
from new_proto.runtime import DiagramValidationError, DuplicateIdError


@pytest.fixture
def flowcharts() -> FlowchartRuntime:
    return Application.create().get(FlowchartRuntime)


def valid_flowchart(flowcharts: FlowchartRuntime) -> FlowchartDraft:
    draft = flowcharts.start("checkout", Direction.LEFT_RIGHT)
    draft = flowcharts.add_group(draft, FlowGroup("main", "Checkout"))
    draft = flowcharts.add_node(draft, Start("start", "Start", "main"))
    draft = flowcharts.add_node(draft, Decision("paid", "Paid?", "main"))
    draft = flowcharts.add_node(draft, Action("retry", "Retry payment", "main"))
    draft = flowcharts.add_node(draft, End("done", "Done", "main"))
    draft = flowcharts.add_flow(draft, Flow("enter", "start", "paid"))
    draft = flowcharts.add_flow(draft, ConditionalFlow("success", "paid", "done", condition="yes"))
    draft = flowcharts.add_flow(draft, ConditionalFlow("failure", "paid", "retry", condition="no"))
    draft = flowcharts.add_flow(draft, Flow("finish_retry", "retry", "done"))
    return flowcharts.add_note(draft, Note("entry_note", "Public entry", "start"))


def test_wireup_composes_frozen_services_through_properties(flowcharts: FlowchartRuntime) -> None:
    with pytest.raises(FrozenInstanceError):
        flowcharts.renderer = object()  # type: ignore[attr-defined,misc]

    assert len(flowcharts.diagrams.validator.constraints) == 3  # type: ignore[attr-defined]
    assert len(flowcharts.constraints) == 6  # type: ignore[attr-defined]


def test_flowchart_proves_service_build_validate_visit_and_render(flowcharts: FlowchartRuntime) -> None:
    diagram = flowcharts.build(valid_flowchart(flowcharts))

    assert flowcharts.inspect(valid_flowchart(flowcharts)).is_valid
    source = flowcharts.render(diagram)

    assert source.startswith("flowchart LR\n")
    assert 'subgraph main["Checkout"]' in source
    assert "paid -->|yes| done" in source
    assert "start -.-> annotation_entry_note" in source


def test_constraint_services_are_visitors_with_diagnostics(flowcharts: FlowchartRuntime) -> None:
    draft = flowcharts.start("invalid")
    draft = flowcharts.add_node(draft, Start("one", "One"))
    draft = flowcharts.add_node(draft, Start("two", "Two"))

    report = flowcharts.inspect(draft)

    assert not report.is_valid
    assert "flowchart.one_start" in {issue.code for issue in report.violations}
    with pytest.raises(DiagramValidationError) as caught:
        flowcharts.build(draft)
    assert caught.value.report == report


def test_immutable_drafts_make_failed_changes_atomic(flowcharts: FlowchartRuntime) -> None:
    original = flowcharts.start("atomic")
    changed = flowcharts.add_node(original, Start("start", "Start"))

    with pytest.raises(DuplicateIdError):
        flowcharts.add_node(changed, End("start", "Duplicate"))

    assert original.state.elements == ()
    assert tuple(item.id for item in changed.state.elements) == ("start",)


def test_published_diagram_and_members_are_immutable(flowcharts: FlowchartRuntime) -> None:
    diagram = flowcharts.build(valid_flowchart(flowcharts))

    with pytest.raises(FrozenInstanceError):
        diagram.direction = Direction.TOP_DOWN  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        diagram.elements[0].element_id = "changed"  # type: ignore[attr-defined,misc]
