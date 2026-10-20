from dataclasses import dataclass
from pathlib import Path

from mermaiden import Application

from ._analytical import AnalyticalFixtureBuilder
from ._behavioral import BehavioralFixtureBuilder
from ._specialized import SpecializedFixtureBuilder
from ._structural import StructuralFixtureBuilder
from .models import DiagramFixture, FixtureCoverageError, FixtureIssue, FixtureIssueKind


@dataclass(frozen=True, slots=True)
class FixtureCatalog:
    application: Application

    def fixtures(self) -> tuple[DiagramFixture, ...]:
        return (
            *StructuralFixtureBuilder(self.application).fixtures(),
            *BehavioralFixtureBuilder(self.application).fixtures(),
            *AnalyticalFixtureBuilder(self.application).fixtures(),
            *SpecializedFixtureBuilder(self.application).fixtures(),
        )

    def inspect(self) -> tuple[dict[str, str], tuple[FixtureIssue, ...]]:
        fixtures = self.fixtures()
        registered = {info.id for info in self.application.available_diagrams()}
        builders: dict[str, list[str]] = {}
        for fixture in fixtures:
            builders.setdefault(fixture.id, []).append(fixture.builder)

        missing = tuple(
            FixtureIssue(FixtureIssueKind.MISSING, diagram_id, f"missing fixture '{diagram_id}'")
            for diagram_id in sorted(registered - builders.keys())
        )
        duplicate = tuple(
            FixtureIssue(
                FixtureIssueKind.DUPLICATE,
                diagram_id,
                f"duplicate fixture '{diagram_id}' from builders: {', '.join(names)}",
            )
            for diagram_id, names in sorted(builders.items())
            if len(names) > 1
        )
        extra = tuple(
            FixtureIssue(FixtureIssueKind.EXTRA, diagram_id, f"extra fixture '{diagram_id}'")
            for diagram_id in sorted(builders.keys() - registered)
        )
        rendered = tuple(
            (fixture, self.application.render(self.application.restore(fixture.snapshot))) for fixture in fixtures
        )
        unpopulated = tuple(
            FixtureIssue(
                FixtureIssueKind.UNPOPULATED,
                fixture.id,
                f"unpopulated fixture '{fixture.id}' from builder: {fixture.builder}",
            )
            for fixture, source in rendered
            if not self.has_semantic_statement(source)
        )
        issues = (*missing, *duplicate, *extra, *unpopulated)
        if duplicate:
            return {}, issues
        return {fixture.id: source for fixture, source in sorted(rendered, key=lambda item: item[0].id)}, issues

    def render(self) -> dict[str, str]:
        sources, issues = self.inspect()
        if issues:
            raise FixtureCoverageError(issues)
        return sources

    def fixture(self, diagram_id: str) -> DiagramFixture:
        fixtures = {fixture.id: fixture for fixture in self.fixtures()}
        try:
            return fixtures[diagram_id]
        except KeyError:
            raise FixtureCoverageError(
                (FixtureIssue(FixtureIssueKind.MISSING, diagram_id, f"missing fixture '{diagram_id}'"),)
            ) from None

    def has_semantic_statement(self, source: str) -> bool:
        body = source.split("---\n", 2)[-1]
        return len(tuple(line for line in body.splitlines() if line.strip())) > 1

    def write(self, output: Path) -> tuple[Path, ...]:
        output.mkdir(parents=True, exist_ok=True)
        sources = self.render()
        paths = tuple(output / f"{diagram_id}.mmd" for diagram_id in sources)
        for path, source in zip(paths, sources.values(), strict=True):
            path.write_text(source, encoding="utf-8")
        return paths
