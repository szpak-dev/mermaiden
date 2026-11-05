from pathlib import Path

from scripts.render_mutation_contract import load_contract, render_artifacts

from .documentation import DocumentationCrawler


def test_documentation_links_resolve_and_every_page_is_reachable() -> None:
    root = Path(__file__).resolve().parents[2]
    pages = DocumentationCrawler(root).crawl(root / "README.md")
    assert pages


def test_generated_mutation_contract_matches_public_discovery() -> None:
    root = Path(__file__).resolve().parents[2]
    artifacts = render_artifacts(load_contract())
    for path, expected in artifacts.items():
        assert path.is_file(), f"Missing generated contract: {path.relative_to(root)}"
        assert path.read_text(encoding="utf-8") == expected, f"Stale generated contract: {path.relative_to(root)}"
    contract_root = root / "docs" / "contracts" / "diagram-mutations"
    actual = {
        path
        for directory in (contract_root / "diagrams", contract_root / "characters")
        for path in directory.iterdir()
        if path.suffix in {".json", ".md"}
    }
    assert actual <= set(artifacts), f"Unexpected generated contract files: {actual - set(artifacts)}"
