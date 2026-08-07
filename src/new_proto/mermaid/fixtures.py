from dataclasses import dataclass

from wireup import injectable

from ..diagrams.architecture.diagram import Architecture
from ..diagrams.architecture.relations import Port
from ..diagrams.classdiagram.diagram import ClassDiagram
from ..diagrams.classdiagram.elements import ClassAttribute, ClassMethod
from ..diagrams.classdiagram.relations import ClassRelationKind
from ..diagrams.flowchart.diagram import Flowchart
from ..diagrams.mindmap.diagram import Mindmap
from ..diagrams.pie.diagram import PieDiagram
from ..diagrams.registry import DiagramRegistry
from ..diagrams.requirement.diagram import RequirementDiagram
from ..diagrams.requirement.elements import RequirementType, Risk, VerificationMethod
from ..diagrams.requirement.relations import RequirementRelationKind
from ..diagrams.sequence.annotations import NotePosition
from ..diagrams.sequence.diagram import SequenceDiagram
from ..diagrams.sequence.elements import ParticipantKind
from ..diagrams.sequence.relations import ControlKind, MessageKind
from ..diagrams.state.annotations import NotePosition as StateNotePosition
from ..diagrams.state.diagram import StateDiagram
from ..diagrams.swimlane.diagram import SwimlaneDiagram
from ..diagrams.treeview.diagram import TreeView
from .service import MermaidRenderer


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramFixtures:
    renderer: MermaidRenderer
    registry: DiagramRegistry

    def render(self) -> dict[str, str]:
        flowchart = self.registry.get("flowchart").diagram
        assert isinstance(flowchart, Flowchart)
        flowchart.add_group("entry", "Entry")
        flowchart.add_group("process", "Process")
        flowchart.add_start("start", "Start", "entry")
        flowchart.add_decision("ready", "Ready?", "entry")
        flowchart.add_action("work", "Work", "process")
        flowchart.add_node("node", "Node", "process")
        flowchart.add_input_output("input", "Input", "process")
        flowchart.add_data_store("data", "Data", "process")
        flowchart.add_document("document", "Document", "process")
        flowchart.add_subprocess("subprocess", "Subprocess", "process")
        flowchart.add_junction("junction", "Junction", "process")
        flowchart.add_end("end", "End", "process")
        flowchart.add_flow("start_ready", "start", "ready")
        flowchart.add_conditional_flow("ready_work", "ready", "work", "yes")
        flowchart.add_flow("work_node", "work", "node")
        flowchart.add_flow("node_input", "node", "input")
        flowchart.add_flow("input_data", "input", "data")
        flowchart.add_flow("data_document", "data", "document")
        flowchart.add_flow("document_subprocess", "document", "subprocess")
        flowchart.add_flow("subprocess_junction", "subprocess", "junction")
        flowchart.add_flow("junction_end", "junction", "end")
        flowchart.add_note("start_note", "Start process", ("start",))
        flowchart.add_note("work_note", "Process work", ("work",))
        flowchart.add_note("end_note", "Finish process", ("end",))

        treeview = self.registry.get("treeView-beta").diagram
        assert isinstance(treeview, TreeView)
        for id, label in (("root", "root/"), ("source", "src/"), ("tests", "tests/"), ("readme", "README.md")):
            treeview.add_item(id, label)
        for id, parent, child in (
            ("root_source", "root", "source"),
            ("root_tests", "root", "tests"),
            ("root_readme", "root", "readme"),
        ):
            treeview.add_branch(id, parent, child)
        treeview.add_annotation("source_note", "source", icon="folder")
        treeview.add_annotation("tests_note", "tests", icon="test")
        treeview.add_annotation("readme_note", "readme", highlight=True, description="Documentation")

        classes = self.registry.get("classDiagram").diagram
        assert isinstance(classes, ClassDiagram)
        classes.add_namespace("domain", "Domain", comment="Domain types")
        classes.add_class(
            "Animal",
            attributes=(ClassAttribute("name", "String"),),
            methods=(ClassMethod("sound", return_type="void"),),
            annotations=("abstract",),
            parent_id="domain",
        )
        classes.add_class("Duck", parent_id="domain")
        classes.add_class("Pond", parent_id="domain")
        classes.add_relation("inherits", "Animal", "Duck", ClassRelationKind.INHERITANCE, "extends")
        classes.add_relation("hosts", "Pond", "Duck", ClassRelationKind.AGGREGATION, "hosts", "1", "*")
        classes.add_relation("depends", "Duck", "Pond", ClassRelationKind.DEPENDENCY, "visits")
        classes.add_note("animal_note", "Animal", "Base type")
        classes.add_note("duck_note", "Duck", "Concrete type")
        classes.add_note("pond_note", "Pond", "Aggregate")

        architecture = self.registry.get("architecture-beta").diagram
        assert isinstance(architecture, Architecture)
        for id, label in (("clients", "Clients"), ("platform", "Platform"), ("data", "Data")):
            architecture.add_group(id, label, columns=2)
        architecture.add_service("web", "Web", "clients")
        architecture.add_service("api", "API", "platform")
        architecture.add_junction("events", "Events", "platform")
        architecture.add_service("database", "Database", "data")
        architecture.add_edge("web_api", "web", "api", Port.RIGHT, Port.LEFT)
        architecture.add_edge("api_events", "api", "events", Port.BOTTOM, Port.TOP)
        architecture.add_edge("api_database", "api", "database", Port.RIGHT, Port.LEFT)
        architecture.add_note("web_note", "web", "Client gateway")
        architecture.add_note("api_note", "api", "Public API")
        architecture.add_note("database_note", "database", "Persistent storage")

        sequence = self.registry.get("sequenceDiagram").diagram
        assert isinstance(sequence, SequenceDiagram)
        sequence.add_box("clients", "Clients", "#E3F2FD")
        sequence.add_participant("user", "User", ParticipantKind.ACTOR, "clients")
        sequence.add_participant("web", "Web", ParticipantKind.BOUNDARY, "clients")
        sequence.add_box("backend", "Backend", "#F3E5F5")
        sequence.add_participant("api", "API", ParticipantKind.CONTROL, "backend")
        sequence.add_participant("database", "Database", ParticipantKind.DATABASE, "backend")
        sequence.add_participant("events", "Events", ParticipantKind.QUEUE)
        sequence.add_participant("worker", "Worker", ParticipantKind.ENTITY, created=True)
        sequence.autonumber("number")
        sequence.add_message("request", "user", "web", "Open", MessageKind.SOLID, activate=True)
        sequence.add_message("forward", "web", "api", "Forward", MessageKind.OPEN)
        sequence.create("create_worker", "worker")
        sequence.add_message("start_worker", "api", "worker", "Start job")
        sequence.control("loop", ControlKind.LOOP, "retry")
        sequence.add_message("query", "api", "database", "Query", MessageKind.DOTTED)
        sequence.control("parallel", ControlKind.PAR, "effects")
        sequence.add_message("publish", "api", "events", "Publish", MessageKind.DOTTED_OPEN)
        sequence.control("end_parallel", ControlKind.END)
        sequence.control("end_loop", ControlKind.END)
        sequence.deactivate("deactivate_web", "web")
        sequence.destroy("destroy_worker", "worker")
        sequence.add_message("stop_worker", "api", "worker", "Stop job")
        sequence.add_note("user_note", "Caller", "user", position=NotePosition.LEFT)
        sequence.add_note("web_note", "Gateway", "web", position=NotePosition.RIGHT)
        sequence.add_note("sequence_note", "Asynchronous", "api", "events", position=NotePosition.OVER)

        swimlane = self.registry.get("swimlane-beta").diagram
        assert isinstance(swimlane, SwimlaneDiagram)
        swimlane.add_lane("customer", "Customer")
        swimlane.add_lane("support", "Support")
        swimlane.add_lane("engineering", "Engineering")
        swimlane.add_start("request", "Request service", "customer")
        swimlane.add_activity("triage", "Triage request", "support")
        swimlane.add_decision("known", "Known issue?", "support")
        swimlane.add_activity("answer", "Send answer", "support")
        swimlane.add_activity("investigate", "Investigate issue", "engineering")
        swimlane.add_connector("handoff", "Handoff", "engineering")
        swimlane.add_end("receive", "Receive update", "customer")
        swimlane.add_flow("request_triage", "request", "triage")
        swimlane.add_flow("triage_known", "triage", "known")
        swimlane.add_conditional_flow("known_answer", "known", "answer", "Yes")
        swimlane.add_conditional_flow("known_investigate", "known", "investigate", "No")
        swimlane.add_flow("investigate_handoff", "investigate", "handoff")
        swimlane.add_flow("handoff_answer", "handoff", "answer")
        swimlane.add_flow("answer_receive", "answer", "receive")

        state = self.registry.get("stateDiagram-v2").diagram
        assert isinstance(state, StateDiagram)
        state.add_state("still", "Still")
        state.add_state("moving", "Moving")
        state.add_state("crash", "Crash")
        state.add_initial("initial")
        state.add_final("final")
        state.add_choice("decision", "Route")
        state.add_fork("fork", "Fork")
        state.add_join("join", "Join")
        state.add_composite("active", "Active")
        state.add_initial("active_initial", "active")
        state.add_final("active_final", "active")
        state.add_state("num_lock_off", "Num lock off", "active")
        state.add_state("num_lock_on", "Num lock on", "active")
        state.add_state("caps_lock_off", "Caps lock off", "active")
        state.add_transition("start_still", "initial", "still")
        state.add_transition("still_moving", "still", "moving", "accelerate")
        state.add_transition("moving_decision", "moving", "decision")
        state.add_transition("decision_active", "decision", "active", "continue")
        state.add_transition("decision_crash", "decision", "crash", "fail")
        state.add_transition("active_fork", "active", "fork")
        state.add_transition("fork_still", "fork", "still")
        state.add_transition("fork_crash", "fork", "crash")
        state.add_transition("still_join", "still", "join")
        state.add_transition("crash_join", "crash", "join")
        state.add_transition("end_join", "join", "final")
        state.add_transition("start_num_lock", "active_initial", "num_lock_off", composite_id="active")
        state.add_transition("num_lock_toggle", "num_lock_off", "num_lock_on", "toggle", "active")
        state.add_transition("end_num_lock", "num_lock_on", "active_final", composite_id="active")
        state.add_transition("start_caps_lock", "active_initial", "caps_lock_off", composite_id="active")
        state.add_transition("end_caps_lock", "caps_lock_off", "active_final", composite_id="active")
        state.add_note("moving_note", "moving", "A moving system", StateNotePosition.RIGHT)

        requirements = self.registry.get("requirementDiagram").diagram
        assert isinstance(requirements, RequirementDiagram)
        requirements.add_requirement(
            "system",
            "REQ-001",
            "The system provides secure access.",
            RequirementType.REQUIREMENT,
            Risk.HIGH,
            VerificationMethod.TEST,
        )
        requirements.add_requirement(
            "login",
            "REQ-002",
            "Users can sign in.",
            RequirementType.FUNCTIONAL,
            Risk.MEDIUM,
            VerificationMethod.DEMONSTRATION,
        )
        requirements.add_requirement(
            "api",
            "REQ-003",
            "The API is documented.",
            RequirementType.INTERFACE,
            Risk.LOW,
            VerificationMethod.INSPECTION,
        )
        requirements.add_requirement(
            "latency",
            "REQ-004",
            "Responses complete within 100ms.",
            RequirementType.PERFORMANCE,
            Risk.HIGH,
            VerificationMethod.ANALYSIS,
        )
        requirements.add_requirement(
            "device",
            "REQ-005",
            "The device withstands heat.",
            RequirementType.PHYSICAL,
            Risk.MEDIUM,
            VerificationMethod.TEST,
        )
        requirements.add_requirement(
            "policy",
            "REQ-006",
            "Access follows policy.",
            RequirementType.DESIGN_CONSTRAINT,
            Risk.LOW,
            VerificationMethod.INSPECTION,
        )
        requirements.add_element("service", "software", "docs/service.md")
        requirements.add_element("test_suite", "test", "tests/requirements.py")
        requirements.add_relation("system_contains_login", "system", "login", RequirementRelationKind.CONTAINS)
        requirements.add_relation("login_copies_api", "login", "api", RequirementRelationKind.COPIES)
        requirements.add_relation("api_derives_latency", "api", "latency", RequirementRelationKind.DERIVES)
        requirements.add_relation("service_satisfies_system", "service", "system", RequirementRelationKind.SATISFIES)
        requirements.add_relation("test_verifies_login", "test_suite", "login", RequirementRelationKind.VERIFIES)
        requirements.add_relation("policy_refines_system", "policy", "system", RequirementRelationKind.REFINES)
        requirements.add_relation("device_traces_policy", "device", "policy", RequirementRelationKind.TRACES)

        mindmap = self.registry.get("mindmap").diagram
        assert isinstance(mindmap, Mindmap)
        mindmap.add_root("root", "Modwire")
        mindmap.add_node("domain", "Domain model", "root")
        mindmap.add_square("contracts", "Contracts", "domain")
        mindmap.add_rounded_square("services", "Services", "domain")
        mindmap.add_circle("runtime", "Runtime", "root")
        mindmap.add_bang("warning", "Important", "runtime")
        mindmap.add_cloud("cloud", "Cloud", "runtime")
        mindmap.add_hexagon("quality", "Quality", "root")

        pie = self.registry.get("pie").diagram
        assert isinstance(pie, PieDiagram)
        pie.set_title("Adopted pets")
        pie.show_values()
        pie.add_slice("dogs", "Dogs", 386)
        pie.add_slice("cats", "Cats", 85)
        pie.add_slice("rats", "Rats", 15)

        return {
            "flowchart": self.renderer.render(flowchart),
            "treeview": self.renderer.render(treeview),
            "classdiagram": self.renderer.render(classes),
            "architecture": self.renderer.render(architecture),
            "sequence": self.renderer.render(sequence),
            "requirement": self.renderer.render(requirements),
            "mindmap": self.renderer.render(mindmap),
            "pie": self.renderer.render(pie),
            "state": self.renderer.render(state),
            "swimlane": self.renderer.render(swimlane),
        }
