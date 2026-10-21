import pytest

from mermaiden.mermaid.schema import MermaidSchemaStore
from scripts.check_mermaid_freshness import latest_package_version


@pytest.mark.freshness
def test_configured_mermaid_versions_match_the_latest_supported_releases() -> None:
    schemas = MermaidSchemaStore()

    assert schemas.mermaid_version == latest_package_version("mermaid", schemas.mermaid_version)
    assert schemas.mermaid_cli_version == latest_package_version("@mermaid-js/mermaid-cli", schemas.mermaid_cli_version)
