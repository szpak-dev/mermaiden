import argparse
from collections.abc import Mapping
from pathlib import Path
from types import TracebackType

from pydantic import BaseModel, ConfigDict
from wireup import ScopedSyncContainer

from .bootstrap import process_scope
from .core.domain import CliClosed
from .mermaid.compatibility import CompatibilityReport, MermaidCompatibilityService
from .mermaid.schema import MermaidDiagramConfig, MermaidSchemaStore
from .mermaid.validation.domain import RenderValidationRuntime


class CliArguments(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    command: str
    prefix: Path


class MermaidenCli:
    def __init__(self, scope: ScopedSyncContainer) -> None:
        self._scope = scope
        self._closed = False

    @classmethod
    def create(cls) -> "MermaidenCli":
        return cls(process_scope())

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True

    def __enter__(self) -> "MermaidenCli":
        self._ensure_open()
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        self.close()

    def mermaid_diagram_configs(self) -> tuple[MermaidDiagramConfig, ...]:
        self._ensure_open()
        return self._scope.get(MermaidSchemaStore).diagram_configs()

    def compatibility_report(self) -> CompatibilityReport:
        self._ensure_open()
        return self._scope.get(MermaidCompatibilityService).inspect()

    def verify_compatibility(self, sources: Mapping[str, str]) -> CompatibilityReport:
        self._ensure_open()
        return self._scope.get(MermaidCompatibilityService).verify(sources)

    def setup_renderer(self, prefix: Path) -> str:
        self._ensure_open()
        return self._scope.get(RenderValidationRuntime).setup_renderer(prefix)

    def _ensure_open(self) -> None:
        if self._closed:
            raise CliClosed("Mermaiden CLI is closed.")


def run() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("compat").set_defaults(prefix=Path.cwd())
    commands.add_parser("renderer-setup").add_argument("--prefix", type=Path, default=Path.cwd())
    arguments = CliArguments.model_validate(vars(parser.parse_args()))
    with MermaidenCli.create() as cli:
        if arguments.command == "renderer-setup":
            print(cli.setup_renderer(arguments.prefix))
            return
        report = cli.compatibility_report()
        for diagram in report.diagrams:
            print(f"{diagram.diagram_id}: {'valid' if report.diagram_valid(diagram) else 'invalid'}")
        for diagram in report.missing_diagrams:
            print(f"{diagram.config_key}: not implemented ({diagram.schema_definition})")
        if not report.valid:
            raise SystemExit(1)


if __name__ == "__main__":
    run()
