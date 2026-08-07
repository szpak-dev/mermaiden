import argparse
from dataclasses import dataclass
from pathlib import Path

from wireup import SyncContainer, create_sync_container

import mermaiden

from .mermaid.application import MermaidPreviewApplication
from .mermaid.compatibility import CompatibilityReport, MermaidCompatibilityService
from .mermaid.compatibility.schema import MermaidDiagramConfig, MermaidSchemaStore
from .mermaid.fixtures import DiagramFixtures


@dataclass(frozen=True, slots=True)
class MermaidenCli:
    _container: SyncContainer

    @classmethod
    def create(cls) -> "MermaidenCli":
        return cls(create_sync_container(injectables=[mermaiden], config={}))

    def mermaid_diagram_configs(self) -> tuple[MermaidDiagramConfig, ...]:
        with self._container.enter_scope() as scope:
            return scope.get(MermaidSchemaStore).diagram_configs()

    def rendered_diagrams(self) -> dict[str, str]:
        with self._container.enter_scope() as scope:
            return scope.get(DiagramFixtures).render()

    def write_fixtures(self, output: Path) -> tuple[Path, ...]:
        output.mkdir(parents=True, exist_ok=True)
        return tuple(self._write_source(output, name, source) for name, source in self.rendered_diagrams().items())

    def write_preview(self, output: Path) -> Path:
        with self._container.enter_scope() as scope:
            preview = scope.get(MermaidPreviewApplication)
            return preview.write_sources(self.rendered_diagrams(), output)

    def compatibility_report(self) -> CompatibilityReport:
        with self._container.enter_scope() as scope:
            return scope.get(MermaidCompatibilityService).inspect()

    def verify_compatibility(self) -> CompatibilityReport:
        with self._container.enter_scope() as scope:
            return scope.get(MermaidCompatibilityService).verify()

    @staticmethod
    def _write_source(output: Path, name: str, source: str) -> Path:
        path = output / f"{name}.mmd"
        path.write_text(source, encoding="utf-8")
        return path

    @classmethod
    def run(cls) -> None:
        parser = argparse.ArgumentParser()
        commands = parser.add_subparsers(dest="command", required=True)
        fixtures = commands.add_parser("fixtures")
        fixtures.add_argument("--output", "-o", type=Path,
                              default=Path(".preview"))
        preview = commands.add_parser("preview")
        preview.add_argument("--output", "-o", type=Path,
                             default=Path(".preview/index.html"))
        commands.add_parser("compat")
        arguments = parser.parse_args()
        cli = cls.create()
        if arguments.command == "fixtures":
            for path in cli.write_fixtures(arguments.output):
                print(path)
        if arguments.command == "preview":
            print(cli.write_preview(arguments.output))
        if arguments.command == "compat":
            report = cli.verify_compatibility()
            for diagram in report.diagrams:
                print(
                    f"{diagram.diagram_id}: {'valid' if report.diagram_valid(diagram) else 'invalid'}")
            for diagram in report.missing_diagrams:
                print(
                    f"{diagram.config_key}: not implemented ({diagram.schema_definition})")
            for violation in report.syntax_violations:
                print(f"{violation.diagram_id}: {violation.message}")
            if not report.valid:
                raise SystemExit(1)


if __name__ == "__main__":
    MermaidenCli.run()
