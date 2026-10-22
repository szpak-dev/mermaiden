import hashlib
import json
from pathlib import Path

from configuration_proof_renderer import ConfigurationProofRenderer

from mermaiden import Application
from tests.fixtures.c4_human_proofs import C4HumanProofCatalog

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "contracts" / "configuration-rendering" / "c4-human-layout"


def digest(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def main() -> None:
    with Application.create() as application:
        sources = C4HumanProofCatalog().sources(application)
        rendered = ConfigurationProofRenderer(application.mermaid_cli_version).render(sources)
        version = application.mermaid_version
        cli_version = application.mermaid_cli_version
    source_root = OUTPUT / "sources"
    svg_root = OUTPUT / "rendered"
    source_root.mkdir(parents=True, exist_ok=True)
    svg_root.mkdir(parents=True, exist_ok=True)
    diagrams: list[dict[str, str]] = []
    for diagram_id, source in sources.items():
        svg = rendered[diagram_id]
        source_path = source_root / f"{diagram_id}.mmd"
        svg_path = svg_root / f"{diagram_id}.svg"
        source_path.write_text(source, encoding="utf-8")
        svg_path.write_text(svg, encoding="utf-8")
        diagrams.append(
            {
                "diagram_id": diagram_id,
                "source": str(source_path.relative_to(OUTPUT)),
                "source_sha256": digest(source),
                "svg": str(svg_path.relative_to(OUTPUT)),
                "svg_sha256": digest(svg),
            }
        )
    manifest = {
        "mermaid_version": version,
        "mermaid_cli_version": cli_version,
        "diagram_count": len(diagrams),
        "diagrams": diagrams,
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
