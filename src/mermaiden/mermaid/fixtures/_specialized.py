from ...diagrams.application import DiagramsApplication
from ...diagrams.c4.diagram import C4ContextDiagram
from ...diagrams.cynefin.diagram import CynefinDiagram
from ...diagrams.cynefin.elements import DomainKind
from ...diagrams.domain import DiagramModel
from ...diagrams.gantt.diagram import Gantt
from ...diagrams.gitgraph.diagram import GitGraphDiagram
from ...diagrams.ishikawa.diagram import IshikawaDiagram
from ...diagrams.kanban.diagram import KanbanDiagram
from ...diagrams.railroad.diagram import RailroadDiagram
from ...diagrams.wardley.diagram import WardleyDiagram


def build_specialized_fixtures(registry: DiagramsApplication) -> dict[str, DiagramModel]:
    gantt = registry.get_diagram("gantt")
    assert isinstance(gantt, Gantt)
    gantt.set_title("Release plan")
    gantt.add_section("delivery", "Delivery")
    gantt.add_task("design", "Design", ("done", "design", "2026-08-01", "2d"), "delivery")

    gitgraph = registry.get_diagram("gitGraph")
    assert isinstance(gitgraph, GitGraphDiagram)
    gitgraph.add_commit("initial", "ZERO", tag="v1.0.0")
    gitgraph.add_branch("develop", "develop", 1)
    gitgraph.checkout("checkout_develop", "develop")
    gitgraph.add_commit("feature", "FEATURE", "HIGHLIGHT")
    gitgraph.checkout("checkout_main", "main")
    gitgraph.add_commit("release", "RELEASE", tag="v1.1.0")

    c4 = registry.get_diagram("C4Context")
    assert isinstance(c4, C4ContextDiagram)
    c4.add_person("customer", "Customer", "A personal banking customer")
    c4.add_system("banking", "Internet Banking System", "Provides online banking", "Python")
    c4.add_database("accounts", "Accounts Database", "Stores account balances", "PostgreSQL")
    c4.add_relationship("uses", "customer", "banking", "Uses")
    c4.add_relationship("reads", "banking", "accounts", "Reads account data")

    ishikawa = registry.get_diagram("ishikawa-beta")
    assert isinstance(ishikawa, IshikawaDiagram)
    ishikawa.add_effect("blurry_photo", "Blurry photo")
    ishikawa.add_category("process", "Process")
    ishikawa.add_cause("focus", "Out of focus", "process")
    ishikawa.add_cause("shutter", "Shutter speed too slow", "process")
    ishikawa.add_category("equipment", "Equipment")
    ishikawa.add_category("lens", "Lens", "equipment")
    ishikawa.add_cause("damaged_lens", "Damaged lens", "lens")

    cynefin = registry.get_diagram("cynefin-beta")
    assert isinstance(cynefin, CynefinDiagram)
    cynefin.add_item("investigate", "Investigate root cause", DomainKind.COMPLEX)
    cynefin.add_item("analyze", "Analyze performance data", DomainKind.COMPLICATED)
    cynefin.add_item("restart", "Restart service", DomainKind.CLEAR)
    cynefin.add_transition("pattern", "investigate", "analyze", "Pattern identified")

    kanban = registry.get_diagram("kanban")
    assert isinstance(kanban, KanbanDiagram)
    kanban.add_column("todo", "Todo")
    kanban.add_column("doing", "In progress")
    kanban.add_task("docs", "Create documentation", "todo", ticket="MC-2037", priority="High")
    kanban.add_task("render", "Create renderer", "doing", assigned="knsv")

    railroad = registry.get_diagram("railroad-ebnf-beta")
    assert isinstance(railroad, RailroadDiagram)
    railroad.add_rule("alternative", "alternative")
    railroad.add_alternative("choices", "alternative")
    railroad.add_special("first_choice", "first", "choices")
    railroad.add_special("second_choice", "second", "choices")
    railroad.add_rule("optional", "optional")
    railroad.add_optional("optional_value", "optional")
    railroad.add_terminal("literal", "value", "optional_value")
    railroad.add_rule("repetition", "repetition")
    railroad.add_repetition("repeated_values", "repetition")
    railroad.add_non_terminal("reference", "value", "repeated_values")
    railroad.add_rule("group", "group")
    railroad.add_group("grouped_value", "group")
    railroad.add_special("group_member", "grouped", "grouped_value")

    wardley = registry.get_diagram("wardley-beta")
    assert isinstance(wardley, WardleyDiagram)
    wardley.add_anchor("business", "Business", 0.95, 0.63)
    wardley.add_component("tea", "Cup of Tea", 0.79, 0.61, "build")
    wardley.add_component("water", "Hot Water", 0.52, 0.8)
    wardley.add_dependency("business_tea", "business", "tea")
    wardley.add_dependency("tea_water", "tea", "water")
    wardley.add_evolution("water_evolve", "water", 0.89)

    return {
        "gantt": gantt,
        "gitgraph": gitgraph,
        "c4": c4,
        "ishikawa": ishikawa,
        "cynefin": cynefin,
        "kanban": kanban,
        "railroad": railroad,
        "wardley": wardley,
    }
