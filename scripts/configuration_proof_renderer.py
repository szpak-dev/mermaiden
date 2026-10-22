import re
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

INVALID_GEOMETRY = re.compile(r"(?<![A-Za-z0-9+/])(?:NaN|Infinity)(?![A-Za-z0-9+/])")


@dataclass(frozen=True, slots=True)
class ConfigurationProofRenderer:
    mermaid_cli_version: str
    timeout_seconds: int = 600
    batch_size: int = 80

    def render(self, sources: Mapping[str, str]) -> Mapping[str, str]:
        version = subprocess.run(("mmdc", "--version"), capture_output=True, check=False, text=True, timeout=60)
        observed = version.stdout.strip()
        if version.returncode or observed != self.mermaid_cli_version:
            raise RuntimeError(
                f"Expected mmdc {self.mermaid_cli_version}, observed {observed or version.stderr.strip()}."
            )
        items = tuple(sources.items())
        rendered: dict[str, str] = {}
        for start in range(0, len(items), self.batch_size):
            batch = items[start : start + self.batch_size]
            rendered.update(self.render_batch(batch))
        return rendered

    def render_batch(self, sources: Sequence[tuple[str, str]]) -> Mapping[str, str]:
        with tempfile.TemporaryDirectory(prefix="mermaiden-configuration-proofs-") as temporary:
            directory = Path(temporary)
            input_path = directory / "proofs.md"
            output_path = directory / "proofs.rendered.md"
            input_path.write_text(
                "\n".join(f"## {diagram_id}\n```mermaid\n{source}```" for diagram_id, source in sources),
                encoding="utf-8",
            )
            try:
                process = subprocess.run(
                    ("mmdc", "-i", str(input_path), "-o", str(output_path)),
                    capture_output=True,
                    check=False,
                    text=True,
                    timeout=self.timeout_seconds,
                )
            except subprocess.TimeoutExpired as error:
                if len(sources) > 1:
                    return self.render_split(sources)
                diagram_id = sources[0][0]
                raise RuntimeError(
                    f"Mermaid timed out after {self.timeout_seconds} seconds rendering '{diagram_id}'."
                ) from error
            if process.returncode:
                if len(sources) > 1:
                    return self.render_split(sources)
                diagram_id = sources[0][0]
                details = process.stderr.strip() or process.stdout.strip()
                raise RuntimeError(f"Mermaid failed to render '{diagram_id}': {details}")
            rendered: dict[str, str] = {}
            for index, (diagram_id, _source) in enumerate(sources, start=1):
                path = directory / f"proofs.rendered-{index}.svg"
                if not path.exists():
                    raise RuntimeError(f"Mermaid did not create SVG proof '{diagram_id}'.")
                svg = path.read_text(encoding="utf-8")
                document = ElementTree.fromstring(svg)
                if any(
                    {"error-icon", "error-text"}.intersection(element.attrib.get("class", "").split())
                    for element in document.iter()
                ) or any(
                    message in svg for message in ("Syntax error in text", "Maximum text size in diagram exceeded")
                ):
                    raise RuntimeError(f"Mermaid created an error SVG for '{diagram_id}'.")
                if INVALID_GEOMETRY.search(svg) is not None:
                    raise RuntimeError(f"Mermaid created invalid geometry for '{diagram_id}'.")
                rendered[diagram_id] = svg
            return rendered

    def render_split(self, sources: Sequence[tuple[str, str]]) -> Mapping[str, str]:
        midpoint = len(sources) // 2
        return {
            **self.render_batch(sources[:midpoint]),
            **self.render_batch(sources[midpoint:]),
        }
