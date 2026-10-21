import subprocess
import sys

from packaging.version import InvalidVersion, Version
from pydantic import RootModel, ValidationError

from mermaiden.mermaid.schema import MermaidSchemaStore


class NpmVersionsPayload(RootModel[tuple[str, ...]]):
    pass


class NpmRegistryError(RuntimeError):
    pass


def latest_package_version(package: str, current_version: str) -> str:
    try:
        result = subprocess.run(
            ("npm", "view", package, "versions", "--json"),
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired as error:
        raise NpmRegistryError(f"npm registry timed out while reading versions for {package}.") from error
    except OSError as error:
        raise NpmRegistryError(f"npm could not read versions for {package}: {error}") from error
    if result.returncode:
        details = result.stderr.strip() or result.stdout.strip() or f"npm exited with status {result.returncode}"
        raise NpmRegistryError(f"npm could not read versions for {package}: {details}")
    try:
        versions = NpmVersionsPayload.model_validate_json(result.stdout).root
    except ValidationError as error:
        raise NpmRegistryError(f"npm returned an invalid version list for {package}: {error}") from error
    try:
        current = Version(current_version)
        compatible = tuple(
            parsed
            for value in versions
            if (parsed := Version(value)).major == current.major and not parsed.is_prerelease
        )
    except InvalidVersion as error:
        raise NpmRegistryError(f"npm returned an invalid version for {package}: {error}") from error
    if not compatible:
        raise NpmRegistryError(f"npm has no stable {current.major}.x release for {package}.")
    return str(max(compatible))


def assert_current(package: str, current_version: str) -> None:
    latest_version = latest_package_version(package, current_version)
    print(f"{package}: configured {current_version}, latest {latest_version}")
    if current_version != latest_version:
        raise RuntimeError(f"{package} is stale: configured {current_version}, latest {latest_version}.")


def main() -> None:
    schemas = MermaidSchemaStore()
    try:
        assert_current("mermaid", schemas.mermaid_version)
        assert_current("@mermaid-js/mermaid-cli", schemas.mermaid_cli_version)
    except RuntimeError as error:
        print(f"Mermaid freshness check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
