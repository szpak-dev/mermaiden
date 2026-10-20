import hashlib
from pathlib import Path
from xml.etree import ElementTree

from pydantic import BaseModel, ConfigDict

from mermaiden import Application
from tests.fixtures.c4_human_proofs import C4HumanProofCatalog

ROOT = Path(__file__).resolve().parents[2]
PROOF_ROOT = ROOT / "docs" / "contracts" / "configuration-rendering" / "c4-human-layout"


class C4HumanProofManifestDiagram(BaseModel):
    model_config = ConfigDict(frozen=True)

    diagram_id: str
    source: str
    source_sha256: str
    svg: str
    svg_sha256: str


class C4HumanProofManifest(BaseModel):
    model_config = ConfigDict(frozen=True)

    mermaid_version: str
    diagram_count: int
    diagrams: tuple[C4HumanProofManifestDiagram, ...]


class TestC4HumanProofs:
    def test_checked_in_sources_cover_every_c4_renderer_mode_with_complex_content(self) -> None:
        proofs = C4HumanProofCatalog().proofs()
        with Application.create() as application:
            sources = C4HumanProofCatalog().sources(application)

        assert tuple(sources) == tuple(proof.id for proof in proofs)
        assert tuple(sources) == (
            "C4Context-human",
            "C4Container-human",
            "C4Component-human",
            "C4Dynamic-human",
            "C4Deployment-human",
        )
        for proof in proofs:
            source = sources[proof.id]
            path = PROOF_ROOT / "sources" / f"{proof.id}.mmd"
            element_count = sum(
                line.startswith(
                    (
                        "Person(",
                        "System(",
                        "System_Ext(",
                        "SystemDb(",
                        "SystemQueue(",
                        "Container(",
                        "ContainerDb(",
                        "ContainerQueue(",
                        "Component(",
                        "ComponentDb(",
                        "ComponentQueue(",
                        "Deployment_Node(",
                    )
                )
                for line in proof.body
            )

            assert path.read_text(encoding="utf-8") == source
            assert element_count >= 12
            assert f'"c4ShapeInRow": {proof.shape_in_row}' in source
            assert f'"c4BoundaryInRow": {proof.boundary_in_row}' in source
            assert (
                f'UpdateLayoutConfig($c4ShapeInRow="{proof.shape_in_row}", $c4BoundaryInRow="{proof.boundary_in_row}")'
            ) in source

    def test_rendered_proofs_are_semantic_svgs_with_every_complex_element(self) -> None:
        proofs = C4HumanProofCatalog().proofs()

        for proof in proofs:
            svg = (PROOF_ROOT / "rendered" / f"{proof.id}.svg").read_text(encoding="utf-8")
            document = ElementTree.fromstring(svg)
            shapes = tuple(
                element for element in document.iter() if "c4-shape" in element.attrib.get("class", "").split()
            )

            assert document.tag == "{http://www.w3.org/2000/svg}svg"
            assert document.attrib.get("viewBox")
            assert len(shapes) >= 12
            assert not any(token in svg for token in ("NaN", "Infinity"))
            assert not any(
                {"error-icon", "error-text"}.intersection(element.attrib.get("class", "").split())
                for element in document.iter()
            )

    def test_manifest_binds_every_c4_human_proof(self) -> None:
        manifest = C4HumanProofManifest.model_validate_json((PROOF_ROOT / "manifest.json").read_text(encoding="utf-8"))

        assert manifest.mermaid_version == "11.16.0"
        assert manifest.diagram_count == 5
        for diagram in manifest.diagrams:
            source = (PROOF_ROOT / diagram.source).read_text(encoding="utf-8")
            svg = (PROOF_ROOT / diagram.svg).read_text(encoding="utf-8")

            assert hashlib.sha256(source.encode()).hexdigest() == diagram.source_sha256
            assert hashlib.sha256(svg.encode()).hexdigest() == diagram.svg_sha256
