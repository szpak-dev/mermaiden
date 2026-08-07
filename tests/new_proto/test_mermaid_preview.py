from pathlib import Path

from new_proto.application import Application
from new_proto.diagrams.registry import DiagramRegistry
from new_proto.mermaid.preview import MermaidPreview


def test_mermaid_preview_writes_rendered_diagrams(tmp_path: Path) -> None:
    container = Application.create()
    output = tmp_path / "preview" / "index.html"
    with container.enter_scope() as scope:
        registry = scope.get(DiagramRegistry)
        result = scope.get(MermaidPreview).write((registry.get("flowchart").diagram,), output)

    assert result == output
    assert output.read_text(encoding="utf-8") == """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>Mermaid previews</title>
<style>body { font-family: sans-serif; margin: 2rem; } section { margin-block: 3rem; }</style>
<body>
<section><h2>flowchart</h2><pre class="mermaid">---
config:
  wrap: true
---
flowchart TD
</pre></section>
<script type="module">
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
mermaid.initialize({ startOnLoad: true });
</script>
</body>
</html>
"""
