import os
import shutil
import subprocess
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import ValidationError
from wireup import injectable

from ...schema import MermaidSchemaStore
from ..domain import (
    MermaidRenderDiagnosticCode,
    MermaidRenderFailure,
    RendererRuntimeResult,
    RenderValidationRuntime,
)
from .npm_package_metadata import NpmPackageMetadata


@injectable(as_type=RenderValidationRuntime)
@dataclass(frozen=True, slots=True)
class EnvironmentRenderValidationRuntime(RenderValidationRuntime):
    schema: MermaidSchemaStore
    timeout_seconds: int = field(default=60, init=False)

    @property
    def mermaid_version(self) -> str:
        return self.schema.mermaid_version

    @property
    def mermaid_cli_version(self) -> str:
        return self.schema.mermaid_cli_version

    def render(self, sources: Mapping[str, str]) -> RendererRuntimeResult:
        try:
            executable = self._executable()
            observed_versions = self._versions(executable)
            supported_versions = (self.mermaid_version, self.mermaid_cli_version)
            if observed_versions != supported_versions:
                raise MermaidRenderFailure(
                    MermaidRenderDiagnosticCode.VERSION_MISMATCH,
                    "Mermaid runtime version mismatch.",
                    "Authority 'schema.lock.json' "
                    f"supports Mermaid '{supported_versions[0]}' and Mermaid CLI '{supported_versions[1]}'; "
                    f"the environment provides Mermaid '{observed_versions[0]}' "
                    f"and Mermaid CLI '{observed_versions[1]}'.",
                )
            with tempfile.TemporaryDirectory(prefix="mermaiden-") as temporary:
                root = Path(temporary)
                input_path = root / "diagrams.md"
                output_path = root / "diagrams.rendered.md"
                input_path.write_text(self._markdown(sources), encoding="utf-8")
                process = self._execute(executable, input_path, output_path)
                return RendererRuntimeResult(
                    process.returncode,
                    self._read_svgs(sources, root),
                    process.stderr.strip() or process.stdout.strip(),
                )
        except subprocess.TimeoutExpired as error:
            raise MermaidRenderFailure(
                MermaidRenderDiagnosticCode.RENDER_TIMEOUT,
                f"Mermaid CLI exceeded the {self.timeout_seconds}-second timeout.",
                str(error),
            ) from error
        except OSError as error:
            raise MermaidRenderFailure(
                MermaidRenderDiagnosticCode.RENDERER_UNAVAILABLE,
                "Mermaid CLI could not be started.",
                str(error),
            ) from error

    def _executable(self) -> Path:
        executable = shutil.which("mmdc")
        if executable is None:
            raise MermaidRenderFailure(
                MermaidRenderDiagnosticCode.RENDERER_UNAVAILABLE,
                "Mermaid CLI could not be started.",
                "The execution environment does not provide 'mmdc' on PATH.",
            )
        return Path(executable)

    def _versions(self, executable: Path) -> tuple[str, str]:
        cli_root, cli = self._package(executable.resolve(), "@mermaid-js/mermaid-cli")
        _, mermaid = self._dependency(cli_root, "mermaid")
        return mermaid.version, cli.version

    def _package(self, entrypoint: Path, name: str) -> tuple[Path, NpmPackageMetadata]:
        for root in entrypoint.parents:
            metadata = self._metadata(root / "package.json")
            if metadata is not None and metadata.name == name:
                return root, metadata
        raise MermaidRenderFailure(
            MermaidRenderDiagnosticCode.RENDERER_UNAVAILABLE,
            "Mermaid runtime package metadata is unavailable.",
            f"The environment's 'mmdc' entrypoint does not belong to an installed '{name}' package.",
        )

    def _dependency(self, package_root: Path, name: str) -> tuple[Path, NpmPackageMetadata]:
        package_parts = tuple(name.split("/"))
        for root in (package_root, *package_root.parents):
            dependency_root = root.joinpath("node_modules", *package_parts)
            metadata = self._metadata(dependency_root / "package.json")
            if metadata is not None and metadata.name == name:
                return dependency_root, metadata
        raise MermaidRenderFailure(
            MermaidRenderDiagnosticCode.RENDERER_UNAVAILABLE,
            "Mermaid runtime package metadata is unavailable.",
            f"The environment does not provide the '{name}' package required by 'mmdc'.",
        )

    def _metadata(self, path: Path) -> NpmPackageMetadata | None:
        if not path.is_file():
            return None
        try:
            return NpmPackageMetadata.model_validate_json(path.read_bytes())
        except ValidationError:
            return None

    def _markdown(self, sources: Mapping[str, str]) -> str:
        return "\n".join(f"## {diagram_id}\n```mermaid\n{source}```" for diagram_id, source in sources.items())

    def _environment(self) -> Mapping[str, str]:
        return os.environ | {"NO_COLOR": "1"}

    def _execute(
        self,
        executable: Path,
        input_path: Path,
        output_path: Path,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            (
                os.fspath(executable),
                "-i",
                os.fspath(input_path),
                "-o",
                os.fspath(output_path),
            ),
            capture_output=True,
            check=False,
            env=self._environment(),
            text=True,
            timeout=self.timeout_seconds,
        )

    def _read_svgs(self, sources: Mapping[str, str], root: Path) -> Mapping[str, str]:
        return {
            diagram_id: path.read_text(encoding="utf-8")
            for index, diagram_id in enumerate(sources, start=1)
            if (path := root / f"diagrams.rendered-{index}.svg").exists()
        }
