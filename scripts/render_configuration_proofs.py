import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from configuration_proof_renderer import ConfigurationProofRenderer

from mermaiden import Application
from tests.fixtures.configuration_proofs import ConfigurationProofCatalog

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "contracts" / "configuration-rendering"


def digest(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def generate(enclosure_audit: Path | None) -> None:
    with Application.create() as application:
        catalog = ConfigurationProofCatalog(application)
        proofs = catalog.proofs()
        probes = catalog.probes()
        version = application.mermaid_version
        cli_version = application.mermaid_cli_version
    sources = {proof.diagram_id: proof.source for proof in proofs}
    svgs = ConfigurationProofRenderer(cli_version).render(sources)
    source_root = OUTPUT / "sources"
    svg_root = OUTPUT / "rendered"
    source_root.mkdir(parents=True, exist_ok=True)
    svg_root.mkdir(parents=True, exist_ok=True)
    probes_by_field: dict[tuple[str, str], list[object]] = defaultdict(list)
    for probe in probes:
        probes_by_field[(probe.diagram_id, probe.field)].append(probe.value)
    diagrams: list[dict[str, object]] = []
    for proof in proofs:
        source = sources[proof.diagram_id]
        svg = svgs[proof.diagram_id]
        source_path = source_root / f"{proof.diagram_id}.mmd"
        svg_path = svg_root / f"{proof.diagram_id}.svg"
        source_path.write_text(source, encoding="utf-8")
        svg_path.write_text(svg, encoding="utf-8")
        fields = [
            {
                "name": field,
                "showcase_value": value,
                "probes": probes_by_field[(proof.diagram_id, field)],
                "witness": "fresh_svg",
            }
            for field, value in proof.configuration.items()
        ]
        diagrams.append(
            {
                "diagram_id": proof.diagram_id,
                "source": str(source_path.relative_to(OUTPUT)),
                "source_sha256": digest(source),
                "svg": str(svg_path.relative_to(OUTPUT)),
                "svg_sha256": digest(svg),
                "semantic_object_count": proof.semantic_object_count,
                "configuration_fields": fields,
            }
        )
    manifest = {
        "mermaid_version": version,
        "mermaid_cli_version": cli_version,
        "diagram_count": len(proofs),
        "configuration_field_count": sum(len(proof.configuration) for proof in proofs),
        "probe_count": len(probes),
        "diagrams": diagrams,
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if enclosure_audit is not None:
        audit = json.loads(enclosure_audit.read_text(encoding="utf-8"))
        (OUTPUT / "enclosure-corpus-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--enclosure-audit", type=Path)
    arguments = parser.parse_args()
    generate(arguments.enclosure_audit)


if __name__ == "__main__":
    main()
