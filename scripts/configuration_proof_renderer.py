from collections.abc import Mapping
from dataclasses import dataclass

from mermaiden import Application


@dataclass(frozen=True, slots=True)
class ConfigurationProofRenderer:
    application: Application
    batch_size: int = 20

    def render(self, sources: Mapping[str, str]) -> Mapping[str, str]:
        items = tuple(sources.items())
        rendered: dict[str, str] = {}
        for start in range(0, len(items), self.batch_size):
            reports = self.application.validate_sources(dict(items[start : start + self.batch_size]))
            for report in reports:
                if not report.success:
                    details = "; ".join(f"{item.message} {item.details}" for item in report.diagnostics)
                    raise RuntimeError(f"Mermaid proof '{report.diagram_id}' failed: {details}")
                rendered[report.diagram_id] = report.svg
        return rendered
