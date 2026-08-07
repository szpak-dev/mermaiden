from dataclasses import dataclass

from wireup import injectable

from ..diagrams.architecture.diagram import Architecture
from ..diagrams.architecture.relations import Port
from ..diagrams.block.diagram import BlockDiagram
from ..diagrams.c4.diagram import C4ContextDiagram
from ..diagrams.classdiagram.diagram import ClassDiagram
from ..diagrams.classdiagram.elements import ClassAttribute, ClassMethod
from ..diagrams.classdiagram.relations import ClassRelationKind
from ..diagrams.cynefin.diagram import CynefinDiagram
from ..diagrams.cynefin.elements import DomainKind
from ..diagrams.er.diagram import EntityRelationshipDiagram
from ..diagrams.flowchart.diagram import Flowchart
from ..diagrams.gantt.diagram import Gantt
from ..diagrams.gitgraph.diagram import GitGraphDiagram
from ..diagrams.journey.diagram import Journey
from ..diagrams.kanban.diagram import KanbanDiagram
from ..diagrams.mindmap.diagram import Mindmap
from ..diagrams.packet.diagram import Packet
from ..diagrams.pie.diagram import PieDiagram
from ..diagrams.radar.diagram import Radar
from ..diagrams.railroad.diagram import RailroadDiagram
from ..diagrams.registry import DiagramRegistry
from ..diagrams.requirement.diagram import RequirementDiagram
from ..diagrams.requirement.elements import RequirementType, Risk, VerificationMethod
from ..diagrams.requirement.relations import RequirementRelationKind
from ..diagrams.sankey.diagram import Sankey
from ..diagrams.sequence.annotations import NotePosition
from ..diagrams.sequence.diagram import SequenceDiagram
from ..diagrams.sequence.elements import ParticipantKind
from ..diagrams.sequence.relations import ControlKind, MessageKind
from ..diagrams.state.annotations import NotePosition as StateNotePosition
from ..diagrams.state.diagram import StateDiagram
from ..diagrams.swimlane.diagram import SwimlaneDiagram
from ..diagrams.timeline.diagram import Timeline
from ..diagrams.treeview.diagram import TreeView
from ..diagrams.venn.diagram import Venn
from ..diagrams.wardley.diagram import WardleyDiagram
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

        timeline = self.registry.get("timeline").diagram
        assert isinstance(timeline, Timeline)
        timeline.set_title("Modwire history")
        timeline.add_section("foundation", "Foundation")
        timeline.add_period("2024", "2024", "foundation")
        timeline.add_event("prototype", "Prototype", "2024")
        timeline.add_event("release", "First release", "2024")

        sankey = self.registry.get("sankey").diagram
        assert isinstance(sankey, Sankey)
        sankey.add_node("grid", "Electricity grid")
        sankey.add_node("industry", "Industry")
        sankey.add_node("homes", "Homes")
        sankey.add_flow("grid_industry", "grid", "industry", 342.165)
        sankey.add_flow("grid_homes", "grid", "homes", 113.726)

        journey = self.registry.get("journey").diagram
        assert isinstance(journey, Journey)
        journey.set_title("Working day")
        journey.add_section("work", "Go to work")
        journey.add_task("tea", "Make tea", 5, ("Me",), "work")
        journey.add_task("work_task", "Do work", 1, ("Me", "Cat"), "work")

        venn = self.registry.get("venn-beta").diagram
        assert isinstance(venn, Venn)
        venn.add_set("frontend", "Frontend", 20)
        venn.add_text("react", "React", "frontend")
        venn.add_set("backend", "Backend", 12)
        venn.add_text("api", "API", "backend")
        venn.add_union("shared", "Shared", ("frontend", "backend"), 3)
        venn.add_text("openapi", "OpenAPI", "shared")

        radar = self.registry.get("radar-beta").diagram
        assert isinstance(radar, Radar)
        radar.set_title("Restaurant comparison")
        radar.add_axis("food", "Food quality")
        radar.add_axis("service", "Service")
        radar.add_axis("price", "Price")
        radar.add_curve("restaurant_a", "Restaurant A", (4, 3, 2))
        radar.add_curve("restaurant_b", "Restaurant B", (3, 4, 3))
        radar.set_range(0, 5)
        radar.set_graticule("polygon")
        radar.set_ticks(5)

        block = self.registry.get("block").diagram
        assert isinstance(block, BlockDiagram)
        block.set_columns(3)
        block.add_block("frontend", "Frontend")
        block.add_space("gap")
        block.add_group("backend", "Backend", columns=2)
        block.add_block("api", "API", parent_id="backend")
        block.add_block("database", "Database", parent_id="backend")

        packet = self.registry.get("packet").diagram
        assert isinstance(packet, Packet)
        packet.set_title("UDP packet")
        packet.add_bits("source", "Source port", 16)
        packet.add_bits("destination", "Destination port", 16)
        packet.add_field("length", "Length", 32, 47)
        packet.add_field("checksum", "Checksum", 48, 63)

        er = self.registry.get("erDiagram").diagram
        assert isinstance(er, EntityRelationshipDiagram)
        er.add_entity("CUSTOMER", "Customer")
        er.add_attribute("customer_id", "id", "int", "CUSTOMER", ("PK",))
        er.add_entity("ORDER", "Order")
        er.add_attribute("order_id", "id", "int", "ORDER", ("PK",))
        er.add_relationship("places", "CUSTOMER", "ORDER", "places", "||--o{")

        gantt = self.registry.get("gantt").diagram
        assert isinstance(gantt, Gantt)
        gantt.set_title("Release plan")
        gantt.add_section("delivery", "Delivery")
        gantt.add_task("design", "Design", ("done", "design", "2026-08-01", "2d"), "delivery")

        gitgraph = self.registry.get("gitGraph").diagram
        assert isinstance(gitgraph, GitGraphDiagram)
        gitgraph.add_commit("initial", "ZERO", tag="v1.0.0")
        gitgraph.add_branch("develop", "develop", 1)
        gitgraph.checkout("checkout_develop", "develop")
        gitgraph.add_commit("feature", "FEATURE", "HIGHLIGHT")
        gitgraph.checkout("checkout_main", "main")
        gitgraph.add_commit("release", "RELEASE", tag="v1.1.0")

        c4 = self.registry.get("C4Context").diagram
        assert isinstance(c4, C4ContextDiagram)
        c4.add_person("customer", "Customer", "A personal banking customer")
        c4.add_system("banking", "Internet Banking System", "Provides online banking", "Python")
        c4.add_database("accounts", "Accounts Database", "Stores account balances", "PostgreSQL")
        c4.add_relationship("uses", "customer", "banking", "Uses")
        c4.add_relationship("reads", "banking", "accounts", "Reads account data")

        cynefin = self.registry.get("cynefin-beta").diagram
        assert isinstance(cynefin, CynefinDiagram)
        cynefin.add_item("investigate", "Investigate root cause", DomainKind.COMPLEX)
        cynefin.add_item("analyze", "Analyze performance data", DomainKind.COMPLICATED)
        cynefin.add_item("restart", "Restart service", DomainKind.CLEAR)
        cynefin.add_transition("pattern", "investigate", "analyze", "Pattern identified")

        kanban = self.registry.get("kanban").diagram
        assert isinstance(kanban, KanbanDiagram)
        kanban.add_column("todo", "Todo")
        kanban.add_column("doing", "In progress")
        kanban.add_task("docs", "Create documentation", "todo", ticket="MC-2037", priority="High")
        kanban.add_task("render", "Create renderer", "doing", assigned="knsv")

        railroad = self.registry.get("railroad-ebnf-beta").diagram
        assert isinstance(railroad, RailroadDiagram)
        railroad.add_rule("expression", "expression")
        railroad.add_non_terminal("term", "term", "expression")
        railroad.add_terminal("plus", "+", "expression")
        railroad.add_non_terminal("term_repeat", "term", "expression")

        wardley = self.registry.get("wardley-beta").diagram
        assert isinstance(wardley, WardleyDiagram)
        wardley.add_anchor("business", "Business", 0.95, 0.63)
        wardley.add_component("tea", "Cup of Tea", 0.79, 0.61, "build")
        wardley.add_component("water", "Hot Water", 0.52, 0.8)
        wardley.add_dependency("business_tea", "business", "tea")
        wardley.add_dependency("tea_water", "tea", "water")
        wardley.add_evolution("water_evolve", "water", 0.89)

        return {
            "flowchart": self.renderer.render(flowchart),
            "treeview": self.renderer.render(treeview),
            "classdiagram": self.renderer.render(classes),
            "architecture": self.renderer.render(architecture),
            "sequence": self.renderer.render(sequence),
            "requirement": self.renderer.render(requirements),
            "mindmap": self.renderer.render(mindmap),
            "pie": self.renderer.render(pie),
            "timeline": self.renderer.render(timeline),
            "sankey": self.renderer.render(sankey),
            "journey": self.renderer.render(journey),
            "venn": self.renderer.render(venn),
            "radar": self.renderer.render(radar),
            "block": self.renderer.render(block),
            "packet": self.renderer.render(packet),
            "er": self.renderer.render(er),
            "gantt": self.renderer.render(gantt),
            "gitgraph": self.renderer.render(gitgraph),
            "c4": self.renderer.render(c4),
            "cynefin": self.renderer.render(cynefin),
            "kanban": self.renderer.render(kanban),
            "railroad": self.renderer.render(railroad),
            "wardley": self.renderer.render(wardley),
            "state": self.renderer.render(state),
            "swimlane": self.renderer.render(swimlane),
        }
