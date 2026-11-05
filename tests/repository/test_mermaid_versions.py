import subprocess
from pathlib import Path

import pytest
from packaging.version import Version
from pydantic import BaseModel, ConfigDict, RootModel

from mermaiden import Application


class PackageManifest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    devDependencies: dict[str, str]


class NpmVersions(BaseModel):
    package: str
    current: str


class VersionList(RootModel[tuple[str, ...]]):
    pass


def test_node_dependencies_match_public_supported_versions() -> None:
    package = Path(__file__).resolve().parents[2] / "package.json"
    dependencies = PackageManifest.model_validate_json(package.read_text(encoding="utf-8")).devDependencies
    with Application.create() as application:
        assert dependencies == {
            "mermaid": application.mermaid_version,
            "@mermaid-js/mermaid-cli": application.mermaid_cli_version,
        }


@pytest.mark.freshness
def test_supported_mermaid_line_matches_latest_stable_registry_versions() -> None:
    with Application.create() as application:
        versions = (
            NpmVersions(package="mermaid", current=application.mermaid_version),
            NpmVersions(package="@mermaid-js/mermaid-cli", current=application.mermaid_cli_version),
        )
    for expected in versions:
        result = subprocess.run(
            ("npm", "view", expected.package, "versions", "--json"), capture_output=True, text=True, timeout=30
        )
        assert result.returncode == 0, f"{expected.package}: {result.stderr or result.stdout}"
        current = Version(expected.current)
        candidates = tuple(
            version
            for text in VersionList.model_validate_json(result.stdout).root
            if (version := Version(text)).major == current.major and not version.is_prerelease
        )
        assert candidates, f"No stable {current.major}.x releases for {expected.package}"
        assert current == max(candidates), f"{expected.package}: configured {current}, latest {max(candidates)}"
