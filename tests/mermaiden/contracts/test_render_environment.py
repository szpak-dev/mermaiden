import json
import os
from pathlib import Path

import pytest

from mermaiden import Application


class TestRenderEnvironmentSiege:
    def test_missing_mermaid_cli_is_reported_without_mutating_the_diagram(self, tmp_path: Path) -> None:
        original_path = os.environ.get("PATH")
        try:
            os.environ["PATH"] = os.fspath(tmp_path)
            with Application.create() as application:
                diagram = application.create_diagram("classDiagram")
                application.execute(diagram, "add_class", {"id": "class_example", "label": "Class Example"})
                before = application.snapshot(diagram).to_dict()

                report = application.validate_render(diagram)

                assert not report.success
                assert report.mermaid_version == application.mermaid_version
                assert report.mermaid_cli_version == application.mermaid_cli_version
                assert report.diagnostics[0].code == "renderer_unavailable"
                assert "does not provide 'mmdc' on PATH" in report.diagnostics[0].details
                assert application.snapshot(diagram).to_dict() == before
        finally:
            if original_path is None:
                del os.environ["PATH"]
            else:
                os.environ["PATH"] = original_path
        assert os.environ.get("PATH") == original_path

    def test_unowned_mermaid_cli_executable_is_rejected_without_execution(self, tmp_path: Path) -> None:
        executable = tmp_path / "mmdc"
        executable.write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
        executable.chmod(0o755)
        original_path = os.environ.get("PATH")
        try:
            os.environ["PATH"] = os.fspath(tmp_path)
            with Application.create() as application:
                diagram = application.create_diagram("classDiagram")
                application.execute(diagram, "add_class", {"id": "class_example", "label": "Class Example"})
                before = application.snapshot(diagram).to_dict()

                report = application.validate_render(diagram)

                assert not report.success
                assert report.diagnostics[0].code == "renderer_unavailable"
                assert "does not belong to an installed '@mermaid-js/mermaid-cli' package" in (
                    report.diagnostics[0].details
                )
                assert application.snapshot(diagram).to_dict() == before
        finally:
            if original_path is None:
                del os.environ["PATH"]
            else:
                os.environ["PATH"] = original_path
        assert os.environ.get("PATH") == original_path

    def test_missing_mermaid_engine_metadata_is_reported_without_execution(self, tmp_path: Path) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("classDiagram")
            application.execute(diagram, "add_class", {"id": "class_example", "label": "Class Example"})
            before = application.snapshot(diagram).to_dict()

            cli_root = tmp_path / "node_modules" / "@mermaid-js" / "mermaid-cli"
            entrypoint = cli_root / "src" / "cli.js"
            entrypoint.parent.mkdir(parents=True)
            entrypoint.write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
            entrypoint.chmod(0o755)
            (cli_root / "package.json").write_text(
                json.dumps({"name": "@mermaid-js/mermaid-cli", "version": application.mermaid_cli_version}),
                encoding="utf-8",
            )
            binary_root = tmp_path / "node_modules" / ".bin"
            binary_root.mkdir()
            (binary_root / "mmdc").symlink_to("../@mermaid-js/mermaid-cli/src/cli.js")

            original_path = os.environ.get("PATH")
            try:
                os.environ["PATH"] = os.fspath(binary_root)

                report = application.validate_render(diagram)

                assert not report.success
                assert report.diagnostics[0].code == "renderer_unavailable"
                assert "does not provide the 'mermaid' package required by 'mmdc'" in report.diagnostics[0].details
                assert application.snapshot(diagram).to_dict() == before
            finally:
                if original_path is None:
                    del os.environ["PATH"]
                else:
                    os.environ["PATH"] = original_path
            assert os.environ.get("PATH") == original_path

    @pytest.mark.parametrize("mismatched_package", ("mermaid", "mermaid_cli"))
    def test_each_mismatched_supported_semver_is_rejected(
        self,
        tmp_path: Path,
        mismatched_package: str,
    ) -> None:
        with Application.create() as application:
            mermaid_version = application.mermaid_version
            mermaid_cli_version = application.mermaid_cli_version
            diagram = application.create_diagram("classDiagram")
            application.execute(diagram, "add_class", {"id": "class_example", "label": "Class Example"})
            before = application.snapshot(diagram).to_dict()

            node_modules = tmp_path / "node_modules"
            cli_root = node_modules / "@mermaid-js" / "mermaid-cli"
            entrypoint = cli_root / "src" / "cli.js"
            entrypoint.parent.mkdir(parents=True)
            entrypoint.write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
            entrypoint.chmod(0o755)
            cli_version = "0.0.0" if mismatched_package == "mermaid_cli" else mermaid_cli_version
            (cli_root / "package.json").write_text(
                json.dumps({"name": "@mermaid-js/mermaid-cli", "version": cli_version}),
                encoding="utf-8",
            )
            mermaid_root = node_modules / "mermaid"
            mermaid_root.mkdir()
            engine_version = "0.0.0" if mismatched_package == "mermaid" else mermaid_version
            (mermaid_root / "package.json").write_text(
                json.dumps({"name": "mermaid", "version": engine_version}),
                encoding="utf-8",
            )
            binary_root = node_modules / ".bin"
            binary_root.mkdir()
            (binary_root / "mmdc").symlink_to("../@mermaid-js/mermaid-cli/src/cli.js")

            original_path = os.environ.get("PATH")
            try:
                os.environ["PATH"] = os.fspath(binary_root)

                report = application.validate_render(diagram)

                assert not report.success
                assert report.diagnostics[0].code == "version_mismatch"
                assert f"supports Mermaid '{mermaid_version}' and Mermaid CLI '{mermaid_cli_version}'" in (
                    report.diagnostics[0].details
                )
                assert f"provides Mermaid '{engine_version}' and Mermaid CLI '{cli_version}'" in (
                    report.diagnostics[0].details
                )
                assert application.snapshot(diagram).to_dict() == before
            finally:
                if original_path is None:
                    del os.environ["PATH"]
                else:
                    os.environ["PATH"] = original_path
            assert os.environ.get("PATH") == original_path
