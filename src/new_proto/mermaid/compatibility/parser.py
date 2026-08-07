import subprocess
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from wireup import injectable


@dataclass(frozen=True, slots=True)
class MermaidSyntaxViolation:
    diagram_id: str
    message: str


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
                    output = process.stderr.strip() or process.stdout.strip()
                    violations.append(MermaidSyntaxViolation(diagram_id, self._message(output)))
            return tuple(violations)

    @staticmethod
    def _message(output: str) -> str:
        lines = tuple(line.strip() for line in output.splitlines() if line.strip())
        parse_error = next((line for line in lines if line.startswith("Error: Parse error on line ")), "")
        if parse_error:
            line = parse_error.removeprefix("Error: Parse error on line ").rstrip(":")
            expected = next((item for item in lines if " got " in item), "")
            token = expected.rsplit(" got ", 1)[-1].strip("'.") if expected else "unknown token"
            return f"syntax error on line {line} (got {token})"
        return lines[0].removeprefix("Error: ") if lines else "Mermaid parser failed without diagnostic output."
