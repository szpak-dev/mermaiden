import re
import subprocess
import sys
import tomllib
from dataclasses import fields
from pathlib import Path

import pytest

from mermaiden import Application

ROOT = Path(__file__).resolve().parents[3]


class TestDocumentation:
    def test_documentation_link_graph_script_succeeds(self) -> None:
        result = subprocess.run(
            (sys.executable, "scripts/check_docs_links.py"),
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        assert result.stdout == "Documentation graph: 52 Markdown pages reachable from README.md.\n"

    def test_local_links_and_repository_paths_exist(self) -> None:
        documents = (ROOT / "README.md", ROOT / "CONTRIBUTING.md", *sorted((ROOT / "docs").rglob("*.md")))

        for document in documents:
            content = document.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^]]+]\((?!https?://|mailto:|#)([^)#]+)(?:#[^)]+)?\)", content):
                path = (document.parent / target).resolve()
                assert path.is_relative_to(ROOT), f"{document}: local link escapes the repository: {target}"
                assert path.exists(), f"{document}: local link does not exist: {target}"
            for target in re.findall(
                r"`((?:(?:src|tests|scripts|docs|\.github)/[^`\s]+)|(?:Makefile|pyproject\.toml|uv\.lock|package-lock\.json|README\.md|CONTRIBUTING\.md))`",
                content,
            ):
                assert (ROOT / target).exists(), f"{document}: repository path does not exist: {target}"

    def test_every_documented_make_command_exists(self) -> None:
        documents = (ROOT / "README.md", ROOT / "CONTRIBUTING.md", *sorted((ROOT / "docs").rglob("*.md")))
        documented = {
            target
            for document in documents
            for target in re.findall(r"\bmake ([a-z][a-z0-9-]*)", document.read_text(encoding="utf-8"))
        }
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        available = set(re.findall(r"^([a-z][a-z0-9-]*):", makefile, flags=re.MULTILINE))

        assert documented <= available, f"documented Make targets do not exist: {sorted(documented - available)}"

    @pytest.mark.integration
    def test_python_examples_execute_without_drift(self, tmp_path: Path) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        named_readme_examples = re.findall(
            r"<!-- executable-example:([a-z-]+):start -->\s*```python\n(.*?)```\s*"
            r"<!-- executable-example:\1:end -->",
            readme,
            flags=re.DOTALL,
        )

        assert len(named_readme_examples) == readme.count("```python")
        assert {name for name, _source in named_readme_examples} == {"application", "discovery", "mutations"}

        documents = (ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md")))
        examples = tuple(
            (document, index, source)
            for document in documents
            for index, source in enumerate(
                re.findall(r"```python\n(.*?)```", document.read_text(encoding="utf-8"), flags=re.DOTALL),
                start=1,
            )
        )

        assert len(examples) >= 10
        for document, index, source in examples:
            name = f"{document.relative_to(ROOT)}:python-example-{index}"
            result = subprocess.run(
                (sys.executable, "-c", source),
                cwd=tmp_path,
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, f"{name}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    def test_returned_data_contract_reference_matches_public_observations(self) -> None:
        reference = (ROOT / "docs/reference/api.md").read_text(encoding="utf-8")
        lines = reference.splitlines()
        names = (
            "DiagramInfo",
            "DiagramDescription",
            "CommandArguments",
            "Violation",
            "ValidationReport",
            "ChangeReport",
            "DiagramObjectReference",
            "DiagramSnapshot",
            "DiagramSnapshotContractIdentity",
            "MermaidRenderReport",
            "MermaidRenderDiagnostic",
        )
        documented: dict[str, set[str]] = {}
        for name in names:
            index = lines.index(f"`{name}`")
            definition: list[str] = []
            for line in lines[index + 1 :]:
                if line.startswith(": "):
                    definition.append(line.removeprefix(": "))
                elif line.startswith("  "):
                    definition.append(line.strip())
                else:
                    break
            documented[name] = set(re.findall(r"`([a-z_]+)(?:\(\))?`", " ".join(definition)))

        with Application.create() as application:
            info = application.diagram_info("sequenceDiagram")
            description = application.diagram_description(info.id)
            arguments = application.command_payload(info.id, "add_participant").validate(
                {"id": "client", "label": "Client"}
            )

            draft = application.create_diagram(info.id)
            validation = application.apply_batch(draft, ())
            violation = validation.violations[0]
            render_report = application.validate_render(draft)
            render_diagnostic = render_report.diagnostics[0]

            diagram = application.create_diagram(info.id)
            change = application.execute(diagram, "add_participant", {"id": "client", "label": "Client"})
            assert change is not None
            application.execute(diagram, "add_participant", {"id": "api", "label": "API"})
            removal = application.execute(diagram, "remove_element", {"id": "client"})
            assert removal is not None
            removed = removal.removed[0]
            snapshot = application.snapshot(diagram)
            identity = application.snapshot_contract_identity(info.id)

        observed = {
            "DiagramInfo": {item.name for item in fields(info)},
            "DiagramDescription": set(description.model_dump()),
            "CommandArguments": {item.name for item in fields(arguments)},
            "Violation": {item.name for item in fields(violation)},
            "ValidationReport": {item.name for item in fields(validation)}
            | {"blocking", "advisory", "can_commit", "is_valid"},
            "ChangeReport": {item.name for item in fields(change)} | {"introduced", "resolved", "current"},
            "DiagramObjectReference": {item.name for item in fields(removed)},
            "DiagramSnapshot": {item.name for item in fields(snapshot)} | {"to_dict"},
            "DiagramSnapshotContractIdentity": {item.name for item in fields(identity)},
            "MermaidRenderReport": {item.name for item in fields(render_report)} | {"success"},
            "MermaidRenderDiagnostic": {item.name for item in fields(render_diagnostic)},
        }

        assert documented == observed

    def test_rendering_guide_has_an_installed_package_setup_path(self) -> None:
        guide = (ROOT / "docs/how-to/render-and-validate.md").read_text(encoding="utf-8")

        assert "application.mermaid_version" in guide
        assert "npm install --global" in guide
        assert "mmdc --version" in guide
        assert "PATH" in guide
        assert "PUPPETEER_EXECUTABLE_PATH" in guide

    def test_sdist_include_paths_are_intentional_tracked_content(self) -> None:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        includes = project["tool"]["hatch"]["build"]["targets"]["sdist"]["include"]

        for include in includes:
            path = ROOT / include
            assert path.exists(), f"sdist include does not exist: {include}"
            tracked = subprocess.run(
                ("git", "ls-files", include),
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            assert tracked.strip(), f"sdist include is not tracked: {include}"

    def test_distribution_is_explicitly_proprietary(self) -> None:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")

        assert project["license"] == "LicenseRef-Proprietary"
        assert project["license-files"] == ["LICENSE"]
        assert not any(classifier.startswith("License ::") for classifier in project["classifiers"])
        assert "All rights reserved" in license_text
        assert "No license or other rights are granted" in license_text
        assert "Any unauthorized use is strictly prohibited" in license_text

    def test_obsolete_documentation_claims_are_absent(self) -> None:
        documents = (ROOT / "README.md", ROOT / "CONTRIBUTING.md", *sorted((ROOT / "docs").rglob("*.md")))
        content = "\n".join(document.read_text(encoding="utf-8") for document in documents)

        for obsolete in ("make docs", "make verify", "MermaidRenderer", "VOCABULARY.md"):
            assert obsolete not in content
        assert "make diagrams-test" in content
        assert "make diagrams-preview" in (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        assert "make diagrams-test" not in (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
