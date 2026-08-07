from pathlib import Path

from new_proto.application import Application


def test_mermaid_preview_writes_rendered_diagrams(tmp_path: Path) -> None:
    output = tmp_path / "preview" / "index.html"
    result = Application.create().write_preview(output)

    assert result == output
    preview = output.read_text(encoding="utf-8")
    assert '<pre class="mermaid">---\nconfig:\n  wrap: true\n---\nflowchart TD\n' in preview
    assert '<pre class="mermaid">---\nconfig:\n  wrap: true\n---\ntreeView-beta\n' in preview
    assert 'import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";' in preview
