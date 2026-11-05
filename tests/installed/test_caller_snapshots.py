import os
from pathlib import Path

import pytest
from pydantic import JsonValue, TypeAdapter

from mermaiden import Application

pytestmark = [pytest.mark.installed, pytest.mark.caller_snapshots]


def test_migrated_caller_snapshots_render_svg_and_png_without_mutation() -> None:
    directory = Path(os.environ["MERMAIDEN_CALLER_SNAPSHOTS"])
    paths = sorted(directory.glob("*.json"))
    assert paths, f"No caller snapshots in {directory}"
    with Application.create() as application:
        for path in paths:
            payload = TypeAdapter(dict[str, JsonValue]).validate_json(path.read_text(encoding="utf-8"))
            assert payload["version"] in (10, 11, 12), path.name
            kind = payload["kind"]
            assert isinstance(kind, str), path.name
            payload["version"] = application.snapshot_contract_identity(kind).snapshot_version
            if kind == "classDiagram":
                configuration = payload["configuration"]
                assert isinstance(configuration, dict), path.name
                fields = configuration["fields"]
                assert isinstance(fields, dict), path.name
                fields.pop("html_labels", None)
            diagram = application.restore(payload)
            before = application.snapshot(diagram).to_dict()
            source = application.render(diagram)
            report = application.validate_render(diagram)
            assert report.success, (path.name, report.diagnostics)
            content = application.render_png(diagram)
            assert content.startswith(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"), path.name
            assert int.from_bytes(content[16:20]) > 0, path.name
            assert int.from_bytes(content[20:24]) > 0, path.name
            assert content.endswith(b"\x00\x00\x00\x00IEND\xaeB`\x82"), path.name
            assert application.snapshot(diagram).to_dict() == before, path.name
            assert application.render(diagram) == source, path.name
