import json
from collections.abc import Mapping
from dataclasses import dataclass

from wireup import injectable


@injectable
@dataclass(frozen=True, slots=True)
class MermaidSourceFormatter:
    def canonicalize(self, value: str) -> str:
        normalized = value.replace("\r\n", "\n").replace("\r", "\n")
        lines = (line.rstrip() for line in normalized.split("\n"))
        return "\n".join(line for line in lines if line).rstrip("\n") + "\n"

    def wrap(self, body: str, configuration: Mapping[str, object]) -> str:
        entries = "".join(
            f"  {key}: {json.dumps(value, ensure_ascii=False)}\n"
            for key, value in configuration.items()
        )
        return f"---\nconfig:\n{entries}---\n{body}"
