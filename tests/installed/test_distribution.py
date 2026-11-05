import importlib.metadata
import json
import os
import subprocess
import sys
import tarfile
import tomllib
from pathlib import Path

import pytest
from pydantic import TypeAdapter
from wireup import create_sync_container, injectable

from mermaiden import Application, ChangeRejected, MermaidRenderFailure, PngExportOptionsError

pytestmark = pytest.mark.installed


@injectable
class ExampleConsumerService:
    pass


def test_sdist_contains_declared_content_and_license() -> None:
    with tarfile.open(os.environ["MERMAIDEN_SDIST"]) as archive:
        names = archive.getnames()
        pyproject_name = next(name for name in names if name.endswith("/pyproject.toml"))
        pyproject_file = archive.extractfile(pyproject_name)
        assert pyproject_file is not None
        project = tomllib.loads(pyproject_file.read().decode())
        includes = TypeAdapter(tuple[str, ...]).validate_python(
            project["tool"]["hatch"]["build"]["targets"]["sdist"]["include"]
        )
        contents = {Path(*Path(name).parts[1:]) for name in names if len(Path(name).parts) > 1}
    assert Path("LICENSE") in contents
    for include in includes:
        assert any(path == Path(include) or path.is_relative_to(include) for path in contents), include


def test_wheel_declares_and_contains_proprietary_license() -> None:
    distribution = importlib.metadata.distribution("mermaiden")
    assert distribution.metadata["License-Expression"] == "LicenseRef-Proprietary"
    files = distribution.files
    assert files is not None
    assert any(path.parts[-2:] == ("licenses", "LICENSE") for path in files)


def test_consumer_wireup_scan_can_import_the_public_facade() -> None:
    container = create_sync_container(injectables=[sys.modules[__name__]], config={})
    try:
        assert type(container.get(ExampleConsumerService)) is ExampleConsumerService
    finally:
        container.close()
    with Application.create() as application:
        assert any(info.id == "classDiagram" for info in application.available_diagrams())


def test_png_failure_then_literal_text_export_works_from_the_installed_wheel() -> None:
    with Application.create() as application:
        diagram = application.create_diagram("classDiagram")
        application.execute(diagram, "add_class", {"id": "png_example", "label": "Example " + "x" * 60000})
        before = application.snapshot(diagram).to_dict()
        with pytest.raises(PngExportOptionsError, match="scale"):
            application.render_png(diagram, scale=0)
        with pytest.raises(MermaidRenderFailure) as failure:
            application.render_png(diagram)
        assert failure.value.code == "render_failed"
        assert "MermaidTextLimitError" in failure.value.message
        assert application.snapshot(diagram).to_dict() == before
        application.execute(
            diagram,
            "update_element",
            {
                "id": "png_example",
                "kind": "class",
                "changes": {"label": 'Example: Syntax error in text; literal &amp; #59; "quotes"'},
            },
        )
        recovered = application.snapshot(diagram).to_dict()
        report = application.validate_render(diagram)
        assert report.success, report.diagnostics
        content = application.render_png(diagram, background="transparent")
        assert content.startswith(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
        assert int.from_bytes(content[16:20]) > 0
        assert int.from_bytes(content[20:24]) > 0
        assert content.endswith(b"\x00\x00\x00\x00IEND\xaeB`\x82")
        assert application.snapshot(diagram).to_dict() == recovered


def test_durable_draft_rejects_invalid_change_then_recovers_across_handles() -> None:
    with Application.create() as application:
        diagram = application.create_diagram("flowchart")
        persisted = application.snapshot(diagram).to_dict()
    with Application.create() as application:
        diagram = application.restore(persisted)
        application.execute(diagram, "add_start", {"id": "start_example", "label": "Example start"})
        persisted = application.snapshot(diagram).to_dict()
    with Application.create() as application:
        diagram = application.restore(persisted)
        with pytest.raises(ChangeRejected):
            application.execute(
                diagram,
                "add_flow",
                {"id": "invalid_example", "source_id": "start_example", "target_id": "missing_example"},
            )
        assert application.snapshot(diagram).to_dict() == persisted
        application.execute(diagram, "add_end", {"id": "end_example", "label": "Example end"})
        persisted = application.snapshot(diagram).to_dict()
    with Application.create() as application:
        diagram = application.restore(persisted)
        application.execute(
            diagram,
            "add_flow",
            {"id": "path_example", "source_id": "start_example", "target_id": "end_example"},
        )
        persisted = application.snapshot(diagram).to_dict()
        assert "mermaiden." not in json.dumps(persisted)
    with Application.create() as application:
        restored = application.restore(persisted)
        assert application.snapshot(restored).to_dict() == persisted
        assert "e_v_start_example r_v_path_example@--> e_v_end_example" in application.render(restored)


@pytest.mark.parametrize("command", ("--help", "compat"))
def test_installed_cli_runs_outside_the_checkout(tmp_path: Path, command: str) -> None:
    result = subprocess.run(
        (sys.executable, "-I", "-m", "mermaiden.cli", command), cwd=tmp_path, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    if command == "--help":
        assert "compat" in result.stdout
