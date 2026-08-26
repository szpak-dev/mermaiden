from dataclasses import dataclass

from wireup import injectable

from ...diagrams.application import DiagramsApplication
from ..application import MermaidApplication
from ._analytical import build_analytical_fixtures
from ._behavioral import build_behavioral_fixtures
from ._specialized import build_specialized_fixtures
from ._structural import build_structural_fixtures


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramFixtures:
    renderer: MermaidApplication
    registry: DiagramsApplication

    def render_compatibility_sources(self) -> dict[str, str]:
        fixtures = self.render()
        aliases = {
            "classdiagram": "class",
            "gitgraph": "gitGraph",
            "treeview": "treeView",
            "wardley": "wardley-beta",
        }
        return {
            self.registry.get_by_config_key(aliases.get(name, name)).id: source for name, source in fixtures.items()
        }

    def render(self) -> dict[str, str]:
        diagrams = {
            **build_structural_fixtures(self.registry),
            **build_behavioral_fixtures(self.registry),
            **build_analytical_fixtures(self.registry),
            **build_specialized_fixtures(self.registry),
        }
        order = (
            "flowchart",
            "treeview",
            "classdiagram",
            "architecture",
            "sequence",
            "requirement",
            "mindmap",
            "pie",
            "timeline",
            "sankey",
            "journey",
            "ishikawa",
            "venn",
            "radar",
            "block",
            "packet",
            "er",
            "eventmodeling",
            "gantt",
            "gitgraph",
            "c4",
            "cynefin",
            "kanban",
            "railroad",
            "wardley",
            "state",
            "swimlane",
        )
        return {name: self.renderer.render(diagrams[name]) for name in order}
