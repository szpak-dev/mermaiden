from pathlib import Path

from pydantic import BaseModel, ConfigDict

from mermaiden import Application


class PackageManifest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    devDependencies: dict[str, str]


class MermaidLockCheck:
    def __init__(self, root: Path) -> None:
        self.root = root

    def run(self) -> None:
        package = PackageManifest.model_validate_json((self.root / "package.json").read_text(encoding="utf-8"))
        with Application.create() as application:
            expected = {
                "@mermaid-js/mermaid-cli": application.mermaid_cli_version,
                "mermaid": application.mermaid_version,
            }
        if package.devDependencies != expected:
            raise RuntimeError("package.json does not match the public Application Mermaid versions.")


if __name__ == "__main__":
    MermaidLockCheck(Path(__file__).resolve().parents[1]).run()
