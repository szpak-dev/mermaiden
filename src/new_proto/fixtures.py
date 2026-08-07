from pathlib import Path

from .application import Application
from .diagrams.architecture.diagram import Architecture
from .diagrams.architecture.relations import Port
from .diagrams.classdiagram.diagram import ClassDiagram
from .diagrams.classdiagram.elements import ClassAttribute, ClassMethod
from .diagrams.classdiagram.relations import ClassRelationKind
from .diagrams.flowchart.diagram import Flowchart
from .diagrams.rendering import MermaidRenderer
from .diagrams.sequence.annotations import NotePosition
from .diagrams.sequence.diagram import SequenceDiagram
from .diagrams.sequence.elements import ParticipantKind
from .diagrams.sequence.relations import ControlKind, MessageKind
from .diagrams.treeview.diagram import TreeView


def rendered_diagrams() -> dict[str, str]:
    container = Application.create()
    with container.enter_scope() as scope:
        renderer = scope.get(MermaidRenderer)
        flowchart = scope.get(Flowchart)
        flowchart.add_group("entry", "Entry")
        flowchart.add_group("process", "Process")
        flowchart.add_start("start", "Start", "entry")
        flowchart.add_decision("ready", "Ready?", "entry")
        flowchart.add_action("work", "Work", "process")
        flowchart.add_end("end", "End", "process")
        flowchart.add_flow("start_ready", "start", "ready")
        flowchart.add_conditional_flow("ready_work", "ready", "work", "yes")
        flowchart.add_flow("work_end", "work", "end")
        flowchart.add_note("start_note", "Start process", ("start",))
        flowchart.add_note("work_note", "Process work", ("work",))
        flowchart.add_note("end_note", "Finish process", ("end",))

        treeview = scope.get(TreeView)
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

        classes = scope.get(ClassDiagram)
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

        architecture = scope.get(Architecture)
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

        sequence = scope.get(SequenceDiagram)
        sequence.add_box("clients", "Clients", "#E3F2FD")
        sequence.add_participant("user", "User", ParticipantKind.ACTOR, "clients")
        sequence.add_participant("web", "Web", ParticipantKind.BOUNDARY, "clients")
        sequence.add_box("backend", "Backend", "#F3E5F5")
        sequence.add_participant("api", "API", ParticipantKind.CONTROL, "backend")
        sequence.add_participant("database", "Database", ParticipantKind.DATABASE, "backend")
        sequence.add_participant("events", "Events", ParticipantKind.QUEUE)
        sequence.autonumber("number")
        sequence.create("create_api", "api")
        sequence.add_message("request", "user", "web", "Open", MessageKind.SOLID, activate=True)
        sequence.add_message("forward", "web", "api", "Forward", MessageKind.OPEN)
        sequence.control("loop", ControlKind.LOOP, "retry")
        sequence.add_message("query", "api", "database", "Query", MessageKind.DOTTED)
        sequence.control("parallel", ControlKind.PAR, "effects")
        sequence.add_message("publish", "api", "events", "Publish", MessageKind.DOTTED_OPEN)
        sequence.control("end_parallel", ControlKind.END)
        sequence.control("end_loop", ControlKind.END)
        sequence.deactivate("deactivate_api", "api")
        sequence.destroy("destroy_api", "api")
        sequence.add_note("user_note", "Caller", "user", position=NotePosition.LEFT)
        sequence.add_note("web_note", "Gateway", "web", position=NotePosition.RIGHT)
        sequence.add_note("sequence_note", "Asynchronous", "api", "events", position=NotePosition.OVER)

        return {
            "flowchart": renderer.render(flowchart),
            "treeview": renderer.render(treeview),
            "classdiagram": renderer.render(classes),
            "architecture": renderer.render(architecture),
            "sequence": renderer.render(sequence),
        }


def main() -> None:
    output = Path(".preview")
    output.mkdir(exist_ok=True)
    for name, source in rendered_diagrams().items():
        (output / f"{name}.mmd").write_text(source, encoding="utf-8")


if __name__ == "__main__":
    main()
