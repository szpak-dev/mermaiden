from dataclasses import dataclass

from mermaiden import Application

from .models import DiagramFixture, FixtureCommand, FixtureDefinition


@dataclass(frozen=True, slots=True)
class BehavioralFixtureBuilder:
    application: Application

    def fixtures(self) -> tuple[DiagramFixture, ...]:
        builder = type(self).__name__
        definitions = (
            FixtureDefinition(
                "sequenceDiagram",
                (
                    FixtureCommand("add_box", {"id": "clients", "label": "Clients", "color": "#E3F2FD"}),
                    FixtureCommand(
                        "add_participant", {"id": "user", "label": "User", "kind": "actor", "box_id": "clients"}
                    ),
                    FixtureCommand(
                        "add_participant", {"id": "web", "label": "Web", "kind": "boundary", "box_id": "clients"}
                    ),
                    FixtureCommand("add_box", {"id": "backend", "label": "Backend", "color": "#F3E5F5"}),
                    FixtureCommand(
                        "add_participant", {"id": "api", "label": "API", "kind": "control", "box_id": "backend"}
                    ),
                    FixtureCommand(
                        "add_participant",
                        {"id": "database", "label": "Database", "kind": "database", "box_id": "backend"},
                    ),
                    FixtureCommand("add_participant", {"id": "events", "label": "Events", "kind": "queue"}),
                    FixtureCommand(
                        "add_participant", {"id": "worker", "label": "Worker", "kind": "entity", "created": True}
                    ),
                    FixtureCommand("autonumber", {"id": "number"}),
                    FixtureCommand(
                        "add_message",
                        {
                            "id": "request",
                            "source_id": "user",
                            "target_id": "web",
                            "label": "Open",
                            "kind": "solid",
                            "activate": True,
                        },
                    ),
                    FixtureCommand(
                        "add_message",
                        {"id": "forward", "source_id": "web", "target_id": "api", "label": "Forward", "kind": "open"},
                    ),
                    FixtureCommand("create", {"id": "create_worker", "participant_id": "worker"}),
                    FixtureCommand(
                        "add_message",
                        {"id": "start_worker", "source_id": "api", "target_id": "worker", "label": "Start job"},
                    ),
                    FixtureCommand("control", {"id": "loop", "kind": "loop", "label": "retry"}),
                    FixtureCommand(
                        "add_message",
                        {
                            "id": "query",
                            "source_id": "api",
                            "target_id": "database",
                            "label": "Query",
                            "kind": "dotted",
                        },
                    ),
                    FixtureCommand("control", {"id": "parallel", "kind": "par", "label": "effects"}),
                    FixtureCommand(
                        "add_message",
                        {
                            "id": "publish",
                            "source_id": "api",
                            "target_id": "events",
                            "label": "Publish",
                            "kind": "dotted_open",
                        },
                    ),
                    FixtureCommand("control", {"id": "end_parallel", "kind": "end"}),
                    FixtureCommand("control", {"id": "end_loop", "kind": "end"}),
                    FixtureCommand("deactivate", {"id": "deactivate_web", "participant_id": "web"}),
                    FixtureCommand("destroy", {"id": "destroy_worker", "participant_id": "worker"}),
                    FixtureCommand(
                        "add_message",
                        {"id": "stop_worker", "source_id": "api", "target_id": "worker", "label": "Stop job"},
                    ),
                    FixtureCommand(
                        "add_note",
                        {"id": "user_note", "text": "Caller", "participant_ids": ["user"], "position": "left of"},
                    ),
                    FixtureCommand(
                        "add_note",
                        {"id": "web_note", "text": "Gateway", "participant_ids": ["web"], "position": "right of"},
                    ),
                    FixtureCommand(
                        "add_note",
                        {
                            "id": "sequence_note",
                            "text": "Asynchronous",
                            "participant_ids": ["api", "events"],
                            "position": "over",
                        },
                    ),
                ),
            ),
            FixtureDefinition(
                "swimlane-beta",
                (
                    FixtureCommand("add_lane", {"id": "customer", "label": "Customer"}),
                    FixtureCommand("add_lane", {"id": "support", "label": "Support"}),
                    FixtureCommand("add_lane", {"id": "engineering", "label": "Engineering"}),
                    FixtureCommand("add_start", {"id": "request", "label": "Request service", "lane_id": "customer"}),
                    FixtureCommand("add_activity", {"id": "triage", "label": "Triage request", "lane_id": "support"}),
                    FixtureCommand("add_decision", {"id": "known", "label": "Known issue?", "lane_id": "support"}),
                    FixtureCommand("add_activity", {"id": "answer", "label": "Send answer", "lane_id": "support"}),
                    FixtureCommand(
                        "add_activity", {"id": "investigate", "label": "Investigate issue", "lane_id": "engineering"}
                    ),
                    FixtureCommand("add_connector", {"id": "handoff", "label": "Handoff", "lane_id": "engineering"}),
                    FixtureCommand("add_end", {"id": "receive", "label": "Receive update", "lane_id": "customer"}),
                    FixtureCommand("add_flow", {"id": "request_triage", "source_id": "request", "target_id": "triage"}),
                    FixtureCommand("add_flow", {"id": "triage_known", "source_id": "triage", "target_id": "known"}),
                    FixtureCommand(
                        "add_conditional_flow",
                        {"id": "known_answer", "source_id": "known", "target_id": "answer", "condition": "Yes"},
                    ),
                    FixtureCommand(
                        "add_conditional_flow",
                        {
                            "id": "known_investigate",
                            "source_id": "known",
                            "target_id": "investigate",
                            "condition": "No",
                        },
                    ),
                    FixtureCommand(
                        "add_flow", {"id": "investigate_handoff", "source_id": "investigate", "target_id": "handoff"}
                    ),
                    FixtureCommand("add_flow", {"id": "handoff_answer", "source_id": "handoff", "target_id": "answer"}),
                    FixtureCommand("add_flow", {"id": "answer_receive", "source_id": "answer", "target_id": "receive"}),
                ),
            ),
            FixtureDefinition(
                "stateDiagram-v2",
                (
                    FixtureCommand("add_state", {"id": "still", "label": "Still"}),
                    FixtureCommand("add_state", {"id": "moving", "label": "Moving"}),
                    FixtureCommand("add_state", {"id": "crash", "label": "Crash"}),
                    FixtureCommand("add_initial", {"id": "initial"}),
                    FixtureCommand("add_final", {"id": "final"}),
                    FixtureCommand("add_choice", {"id": "decision", "label": "Route"}),
                    FixtureCommand("add_fork", {"id": "fork", "label": "Fork"}),
                    FixtureCommand("add_join", {"id": "join", "label": "Join"}),
                    FixtureCommand("add_composite", {"id": "active", "label": "Active"}),
                    FixtureCommand("add_initial", {"id": "active_initial", "composite_id": "active"}),
                    FixtureCommand("add_final", {"id": "active_final", "composite_id": "active"}),
                    FixtureCommand(
                        "add_state", {"id": "num_lock_off", "label": "Num lock off", "composite_id": "active"}
                    ),
                    FixtureCommand(
                        "add_state", {"id": "num_lock_on", "label": "Num lock on", "composite_id": "active"}
                    ),
                    FixtureCommand(
                        "add_state", {"id": "caps_lock_off", "label": "Caps lock off", "composite_id": "active"}
                    ),
                    FixtureCommand(
                        "add_transition", {"id": "start_still", "source_id": "initial", "target_id": "still"}
                    ),
                    FixtureCommand(
                        "add_transition",
                        {"id": "still_moving", "source_id": "still", "target_id": "moving", "label": "accelerate"},
                    ),
                    FixtureCommand(
                        "add_transition", {"id": "moving_decision", "source_id": "moving", "target_id": "decision"}
                    ),
                    FixtureCommand(
                        "add_transition",
                        {"id": "decision_active", "source_id": "decision", "target_id": "active", "label": "continue"},
                    ),
                    FixtureCommand(
                        "add_transition",
                        {"id": "decision_crash", "source_id": "decision", "target_id": "crash", "label": "fail"},
                    ),
                    FixtureCommand("add_transition", {"id": "active_fork", "source_id": "active", "target_id": "fork"}),
                    FixtureCommand("add_transition", {"id": "fork_still", "source_id": "fork", "target_id": "still"}),
                    FixtureCommand("add_transition", {"id": "fork_crash", "source_id": "fork", "target_id": "crash"}),
                    FixtureCommand("add_transition", {"id": "still_join", "source_id": "still", "target_id": "join"}),
                    FixtureCommand("add_transition", {"id": "crash_join", "source_id": "crash", "target_id": "join"}),
                    FixtureCommand("add_transition", {"id": "end_join", "source_id": "join", "target_id": "final"}),
                    FixtureCommand(
                        "add_transition",
                        {
                            "id": "start_num_lock",
                            "source_id": "active_initial",
                            "target_id": "num_lock_off",
                            "composite_id": "active",
                        },
                    ),
                    FixtureCommand(
                        "add_transition",
                        {
                            "id": "num_lock_toggle",
                            "source_id": "num_lock_off",
                            "target_id": "num_lock_on",
                            "label": "toggle",
                            "composite_id": "active",
                        },
                    ),
                    FixtureCommand(
                        "add_transition",
                        {
                            "id": "end_num_lock",
                            "source_id": "num_lock_on",
                            "target_id": "active_final",
                            "composite_id": "active",
                        },
                    ),
                    FixtureCommand(
                        "add_transition",
                        {
                            "id": "start_caps_lock",
                            "source_id": "active_initial",
                            "target_id": "caps_lock_off",
                            "composite_id": "active",
                        },
                    ),
                    FixtureCommand(
                        "add_transition",
                        {
                            "id": "end_caps_lock",
                            "source_id": "caps_lock_off",
                            "target_id": "active_final",
                            "composite_id": "active",
                        },
                    ),
                    FixtureCommand(
                        "add_note",
                        {"id": "moving_note", "state_id": "moving", "text": "A moving system", "position": "right"},
                    ),
                ),
            ),
            FixtureDefinition(
                "timeline",
                (
                    FixtureCommand("set_title", {"title": "Mermaiden history"}),
                    FixtureCommand("add_section", {"id": "foundation", "label": "Foundation"}),
                    FixtureCommand("add_period", {"id": "2024", "label": "2024", "section_id": "foundation"}),
                    FixtureCommand("add_event", {"id": "prototype", "label": "Prototype", "period_id": "2024"}),
                    FixtureCommand("add_event", {"id": "release", "label": "First release", "period_id": "2024"}),
                    FixtureCommand("add_period", {"id": "2025", "label": "2025", "section_id": "foundation"}),
                    FixtureCommand("add_event", {"id": "typed_runtime", "label": "Typed runtime", "period_id": "2025"}),
                    FixtureCommand("add_event", {"id": "snapshots", "label": "Typed snapshots", "period_id": "2025"}),
                    FixtureCommand(
                        "add_event", {"id": "validation", "label": "Render validation", "period_id": "2025"}
                    ),
                    FixtureCommand("add_period", {"id": "2026", "label": "2026", "section_id": "foundation"}),
                    FixtureCommand(
                        "add_event", {"id": "configuration", "label": "Typed configuration", "period_id": "2026"}
                    ),
                    FixtureCommand("add_event", {"id": "proofs", "label": "Physical proofs", "period_id": "2026"}),
                    FixtureCommand("add_event", {"id": "release_12", "label": "Release 12", "period_id": "2026"}),
                ),
            ),
            FixtureDefinition(
                "journey",
                (
                    FixtureCommand("set_title", {"title": "Working day"}),
                    FixtureCommand("add_section", {"id": "work", "label": "Go to work"}),
                    FixtureCommand(
                        "add_task",
                        {"id": "tea", "label": "Make tea", "score": 5, "actors": ["Me"], "section_id": "work"},
                    ),
                    FixtureCommand(
                        "add_task",
                        {
                            "id": "work_task",
                            "label": "Do work",
                            "score": 1,
                            "actors": ["Me", "Cat"],
                            "section_id": "work",
                        },
                    ),
                    FixtureCommand("add_section", {"id": "commute", "label": "Commute"}),
                    FixtureCommand(
                        "add_task",
                        {
                            "id": "walk",
                            "label": "Walk to station",
                            "score": 4,
                            "actors": ["Me"],
                            "section_id": "commute",
                        },
                    ),
                    FixtureCommand(
                        "add_task",
                        {"id": "train", "label": "Take train", "score": 3, "actors": ["Me"], "section_id": "commute"},
                    ),
                    FixtureCommand(
                        "add_task",
                        {
                            "id": "arrive",
                            "label": "Reach office",
                            "score": 5,
                            "actors": ["Me"],
                            "section_id": "commute",
                        },
                    ),
                    FixtureCommand("add_section", {"id": "delivery", "label": "Deliver software"}),
                    FixtureCommand(
                        "add_task",
                        {
                            "id": "design",
                            "label": "Review design",
                            "score": 4,
                            "actors": ["Me", "Team"],
                            "section_id": "delivery",
                        },
                    ),
                    FixtureCommand(
                        "add_task",
                        {
                            "id": "build",
                            "label": "Build feature",
                            "score": 3,
                            "actors": ["Me", "Team"],
                            "section_id": "delivery",
                        },
                    ),
                    FixtureCommand(
                        "add_task",
                        {
                            "id": "verify",
                            "label": "Verify behavior",
                            "score": 5,
                            "actors": ["Me", "QA"],
                            "section_id": "delivery",
                        },
                    ),
                    FixtureCommand(
                        "add_task",
                        {
                            "id": "deploy",
                            "label": "Deploy release",
                            "score": 4,
                            "actors": ["Me", "Ops"],
                            "section_id": "delivery",
                        },
                    ),
                ),
            ),
            FixtureDefinition(
                "eventmodeling",
                (
                    FixtureCommand("add_swimlane", {"id": "checkout", "label": "Checkout"}),
                    FixtureCommand("add_actor", {"id": "cart_ui", "label": "Cart UI", "swimlane_id": "checkout"}),
                    FixtureCommand("add_command", {"id": "add_item", "label": "Add item", "swimlane_id": "checkout"}),
                    FixtureCommand("add_event", {"id": "item_added", "label": "Item added", "swimlane_id": "checkout"}),
                    FixtureCommand("add_view", {"id": "cart_items", "label": "Cart items", "swimlane_id": "checkout"}),
                    FixtureCommand("add_flow", {"id": "submit", "source_id": "cart_ui", "target_id": "add_item"}),
                    FixtureCommand("add_flow", {"id": "record", "source_id": "add_item", "target_id": "item_added"}),
                    FixtureCommand("add_flow", {"id": "project", "source_id": "item_added", "target_id": "cart_items"}),
                    FixtureCommand("add_swimlane", {"id": "fulfillment", "label": "Fulfillment"}),
                    FixtureCommand(
                        "add_actor", {"id": "warehouse_ui", "label": "Warehouse UI", "swimlane_id": "fulfillment"}
                    ),
                    FixtureCommand(
                        "add_command", {"id": "pack_order", "label": "Pack order", "swimlane_id": "fulfillment"}
                    ),
                    FixtureCommand(
                        "add_event", {"id": "order_packed", "label": "Order packed", "swimlane_id": "fulfillment"}
                    ),
                    FixtureCommand(
                        "add_view", {"id": "packing_queue", "label": "Packing queue", "swimlane_id": "fulfillment"}
                    ),
                    FixtureCommand(
                        "add_flow", {"id": "select_order", "source_id": "warehouse_ui", "target_id": "pack_order"}
                    ),
                    FixtureCommand(
                        "add_flow", {"id": "record_pack", "source_id": "pack_order", "target_id": "order_packed"}
                    ),
                    FixtureCommand(
                        "add_flow", {"id": "project_queue", "source_id": "order_packed", "target_id": "packing_queue"}
                    ),
                ),
            ),
        )
        return tuple(definition.build(self.application, builder) for definition in definitions)
