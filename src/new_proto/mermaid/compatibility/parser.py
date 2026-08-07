import subprocess
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from wireup import injectable


@dataclass(frozen=True, slots=True)
class MermaidSyntaxViolation:
    diagram_id: str
    output: str


@injectable
@dataclass(frozen=True, slots=True)
class MermaidSyntaxValidator:
    version: str = field(default="11.16.0", init=False)

    def validate(self, sources: Mapping[str, str]) -> tuple[MermaidSyntaxViolation, ...]:
        with tempfile.TemporaryDirectory(prefix="modwire-mermaid-") as temporary:
            root = Path(temporary)
            violations: list[MermaidSyntaxViolation] = []
            for diagram_id, source in sources.items():
                source_path = root / f"{diagram_id}.mmd"
                output_path = root / f"{diagram_id}.svg"
                source_path.write_text(source, encoding="utf-8")
                process = subprocess.run(
                    (
                        "npx",
                        "--yes",
                        f"--package=@mermaid-js/mermaid-cli@{self.version}",
                        "mmdc",
                        "-i",
                        str(source_path),
                        "-o",
                        str(output_path),
                    ),
                    capture_output=True,
                    check=False,
                    text=True,
                )
                if process.returncode:
                    violations.append(
                        MermaidSyntaxViolation(diagram_id, process.stderr.strip() or process.stdout.strip())
                    )
            return tuple(violations)
