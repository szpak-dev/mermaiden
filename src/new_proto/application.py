import argparse
from dataclasses import dataclass
from pathlib import Path

from wireup import SyncContainer, create_sync_container

import new_proto

from .diagrams.registry import DiagramInfo, DiagramRegistry
from .fixtures import DiagramFixtures
from .mermaid.preview import MermaidPreview


@dataclass(frozen=True, slots=True)
class Application:
    container: SyncContainer

    @classmethod
    def create(cls) -> "Application":
        return cls(create_sync_container(injectables=[new_proto], config={}))

    def available_diagrams(self) -> tuple[DiagramInfo, ...]:
        with self.container.enter_scope() as scope:
            return scope.get(DiagramRegistry).available()

    def diagram_info(self, diagram_id: str) -> DiagramInfo:
        with self.container.enter_scope() as scope:
            return scope.get(DiagramRegistry).get(diagram_id)

    def rendered_diagrams(self) -> dict[str, str]:
        with self.container.enter_scope() as scope:
            return scope.get(DiagramFixtures).render()

    def write_fixtures(self, output: Path) -> tuple[Path, ...]:
        output.mkdir(parents=True, exist_ok=True)
        return tuple(
            self._write_source(output, name, source) for name, source in self.rendered_diagrams().items()
        )

    def write_preview(self, output: Path) -> Path:
        with self.container.enter_scope() as scope:
            preview = scope.get(MermaidPreview)
            return preview.write_sources(self.rendered_diagrams(), output)

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
        fixtures.add_argument("--output", "-o", type=Path, default=Path(".preview"))
        preview = commands.add_parser("preview")
        preview.add_argument("--output", "-o", type=Path, default=Path(".preview/index.html"))
        arguments = parser.parse_args()
        application = cls.create()
        if arguments.command == "fixtures":
            for path in application.write_fixtures(arguments.output):
                print(path)
        if arguments.command == "preview":
            print(application.write_preview(arguments.output))


if __name__ == "__main__":
    Application.run()
