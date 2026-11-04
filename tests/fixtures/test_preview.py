import os
from base64 import b64decode
from pathlib import Path
from xml.etree import ElementTree

import pytest

from mermaiden import Application
from tests.fixtures.catalog import FixtureCatalog


@pytest.mark.integration
def test_mermaid_preview_embeds_verified_svgs_in_source_order(tmp_path: Path) -> None:
    output = tmp_path / "preview" / "index.html"
    with Application.create() as application:
        sources = FixtureCatalog(application).render()
        result = application.write_preview(sources, output)

    assert result == output
    document = output.read_text(encoding="utf-8")
    assert tuple(document.index(f"<h2>{diagram_id}</h2>") for diagram_id in sources) == tuple(
        sorted(document.index(f"<h2>{diagram_id}</h2>") for diagram_id in sources)
    )
    assert "<script" not in document
    assert "cdn.jsdelivr.net" not in document
    images = document.split('src="data:image/svg+xml;base64,')[1:]
    assert len(images) == len(sources)
    for image in images:
        svg = ElementTree.fromstring(b64decode(image.split('"', 1)[0]))
        assert svg.tag == "{http://www.w3.org/2000/svg}svg"
    assert document.count("<summary>Mermaid source</summary>") == len(sources)


def test_failed_preview_preserves_the_existing_file_and_diagram(tmp_path: Path) -> None:
    output = tmp_path / "preview.html"
    output.write_text("Existing preview", encoding="utf-8")
    original_path = os.environ.get("PATH")
    with Application.create() as application:
        diagram = application.create_diagram("classDiagram")
        application.execute(diagram, "add_class", {"id": "class_example", "label": "Example"})
        before = application.snapshot(diagram).to_dict()
        source = application.render(diagram)
        try:
            os.environ["PATH"] = os.fspath(tmp_path)
            with pytest.raises(RuntimeError, match="Mermaid CLI could not be started"):
                application.write_preview({"classDiagram": source}, output)
            assert output.read_text(encoding="utf-8") == "Existing preview"
            assert application.snapshot(diagram).to_dict() == before
        finally:
            if original_path is None:
                del os.environ["PATH"]
            else:
                os.environ["PATH"] = original_path
