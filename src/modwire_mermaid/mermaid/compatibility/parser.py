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
        incomplete = tuple(
            MermaidSyntaxViolation(diagram_id, "compatibility fixture has no diagram content")
            for diagram_id, source in sources.items()
            if not self._has_content(source)
        )
        if incomplete:
            return incomplete
        with tempfile.TemporaryDirectory(prefix="modwire-mermaid-") as temporary:
            root = Path(temporary)
            input_path = root / "diagrams.md"
            output_path = root / "diagrams.rendered.md"
            input_path.write_text(self._markdown(sources), encoding="utf-8")
            process = subprocess.run(
                (
                    "npx",
                    "--yes",
                    f"--package=@mermaid-js/mermaid-cli@{self.version}",
                    "mmdc",
                    "-i",
                    str(input_path),
                    "-o",
                    str(output_path),
                ),
                capture_output=True,
                check=False,
                text=True,
            )
            if not process.returncode:
                return self._rendering_violations(root, sources)
            output = process.stderr.strip() or process.stdout.strip()
            return (MermaidSyntaxViolation("all", self._message(output)),)

    @staticmethod
    def _has_content(source: str) -> bool:
        body = source.split("---\n", 2)[-1]
        return len(tuple(line for line in body.splitlines() if line.strip())) > 1

    @staticmethod
    def _markdown(sources: Mapping[str, str]) -> str:
        return "\n".join(
            f"## {diagram_id}\n```mermaid\n{source}```" for diagram_id, source in sources.items()
        )

    @staticmethod
    def _rendering_violations(
        root: Path,
        sources: Mapping[str, str],
    ) -> tuple[MermaidSyntaxViolation, ...]:
        return tuple(
            MermaidSyntaxViolation(diagram_id, "Mermaid rendered a syntax-error diagram.")
            for index, diagram_id in enumerate(sources, start=1)
            if MermaidSyntaxValidator._has_error_svg(root / f"diagrams.rendered-{index}.svg")
        )

    @staticmethod
    def _has_error_svg(path: Path) -> bool:
        return path.exists() and "Syntax error in text" in path.read_text(encoding="utf-8")

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
