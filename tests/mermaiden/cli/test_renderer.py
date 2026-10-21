import json
from pathlib import Path

from mermaiden import Application


def test_node_lock_uses_the_separate_supported_mermaid_versions() -> None:
    root = Path(__file__).parents[3]
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    package_lock = json.loads((root / "package-lock.json").read_text(encoding="utf-8"))
    with Application.create() as application:
        mermaid_version = application.mermaid_version
        cli_version = application.mermaid_cli_version

    assert package["devDependencies"] == {
        "@mermaid-js/mermaid-cli": cli_version,
        "mermaid": mermaid_version,
    }
    assert package_lock["packages"][""]["devDependencies"] == package["devDependencies"]
    assert package_lock["packages"]["node_modules/@mermaid-js/mermaid-cli"]["version"] == cli_version
    assert package_lock["packages"]["node_modules/mermaid"]["version"] == mermaid_version
