from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from mermaiden import Application


@dataclass(frozen=True, slots=True)
class DiagramFixture:
    id: str
    snapshot: Mapping[str, object]
    builder: str


@dataclass(frozen=True, slots=True)
class FixtureCommand:
    operation: str
    arguments: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class FixtureDefinition:
    diagram_id: str
    commands: tuple[FixtureCommand, ...]

    def build(self, application: Application, builder: str) -> DiagramFixture:
        diagram = application.create_diagram(self.diagram_id)
        for command in self.commands:
            application.execute(diagram, command.operation, command.arguments)
        return DiagramFixture(self.diagram_id, application.snapshot(diagram).to_dict(), builder)


class FixtureIssueKind(StrEnum):
    MISSING = "missing"
    DUPLICATE = "duplicate"
    EXTRA = "extra"
    UNPOPULATED = "unpopulated"


@dataclass(frozen=True, slots=True)
class FixtureIssue:
    kind: FixtureIssueKind
    diagram_id: str
    message: str


class FixtureCoverageError(RuntimeError):
    def __init__(self, issues: tuple[FixtureIssue, ...]) -> None:
        self.issues = issues
        super().__init__("; ".join(issue.message for issue in issues))
