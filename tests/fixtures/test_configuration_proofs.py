import hashlib
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

import pytest
import yaml

from mermaiden import Application
from tests.fixtures.configuration_proofs import ConfigurationProofCatalog, ConfigurationProofRenderer

ROOT = Path(__file__).resolve().parents[2]
PROOF_ROOT = ROOT / "docs" / "contracts" / "configuration-rendering"
CONFIGURATION_RENDER_SHARDS = (
    pytest.param(0, 4, id="shard-1-of-4"),
    pytest.param(1, 4, id="shard-2-of-4"),
    pytest.param(2, 4, id="shard-3-of-4"),
    pytest.param(3, 4, id="shard-4-of-4"),
)


@dataclass(frozen=True, slots=True)
class ConfigurationRenderProofs:
    mermaid_version: str
    sources: tuple[tuple[str, str], ...]

    def shard(self, shard_index: int, shard_count: int) -> dict[str, str]:
        return dict(self.sources[shard_index::shard_count])


@pytest.fixture(scope="session")
def configuration_render_proofs() -> ConfigurationRenderProofs:
    with Application.create() as application:
        rendered = ConfigurationProofCatalog(application).rendered_probes()
        version = application.mermaid_version
    return ConfigurationRenderProofs(
        mermaid_version=version,
        sources=tuple((f"{index:04d}-{probe.id}", probe.source) for index, probe in enumerate(rendered)),
    )


def test_checked_in_mermaid_proofs_cover_every_configuration_field() -> None:
    with Application.create() as application:
        catalog = ConfigurationProofCatalog(application)
        proofs = catalog.proofs()
        expected_diagrams = tuple(info.id for info in application.available_diagrams())

    assert tuple(proof.diagram_id for proof in proofs) == expected_diagrams
    assert len(proofs) == 27
    assert sum(len(proof.configuration) for proof in proofs) == 466
    for proof in proofs:
        assert proof.semantic_object_count >= 12
        path = PROOF_ROOT / "sources" / f"{proof.diagram_id}.mmd"
        assert path.read_text(encoding="utf-8") == proof.source
        assert set(proof.configuration) == {
            *yaml.safe_load(proof.source.split("---\n", 2)[1])["config"].get(
                next(
                    info.config_key for info in Application.create().available_diagrams() if info.id == proof.diagram_id
                ),
                {},
            ),
            "wrap",
        }


def test_checked_in_svg_proofs_are_nonempty_semantic_documents() -> None:
    paths = tuple(sorted((PROOF_ROOT / "rendered").glob("*.svg")))

    assert len(paths) == 27
    for path in paths:
        svg = path.read_text(encoding="utf-8")
        document = ElementTree.fromstring(svg)
        assert document.tag == "{http://www.w3.org/2000/svg}svg"
        view_box = tuple(float(value) for value in document.attrib["viewBox"].split())
        assert view_box[2] > 0
        assert view_box[3] > 0
        assert not any(token in svg for token in ("NaN", "Infinity"))
        assert not any("undefined" in text for element in document.iter() for text in element.itertext())
        assert not any(
            {"error-icon", "error-text"}.intersection(element.attrib.get("class", "").split())
            for element in document.iter()
        )


def test_manifest_hashes_bind_every_physical_proof() -> None:
    manifest = yaml.safe_load((PROOF_ROOT / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["mermaid_version"] == "11.16.0"
    assert manifest["diagram_count"] == 27
    assert manifest["configuration_field_count"] == 466
    assert manifest["probe_count"] == 1464
    for diagram in manifest["diagrams"]:
        source = (PROOF_ROOT / diagram["source"]).read_text(encoding="utf-8")
        svg = (PROOF_ROOT / diagram["svg"]).read_text(encoding="utf-8")
        assert diagram["semantic_object_count"] >= 12
        assert hashlib.sha256(source.encode()).hexdigest() == diagram["source_sha256"]
        assert hashlib.sha256(svg.encode()).hexdigest() == diagram["svg_sha256"]


def test_every_configuration_probe_serializes_exactly_and_survives_snapshot_restoration() -> None:
    with Application.create() as application:
        catalog = ConfigurationProofCatalog(application)
        probes = catalog.rendered_probes()
        config_keys = {info.id: info.config_key for info in application.available_diagrams()}

    assert len({probe.probe.id for probe in probes}) == 466
    assert len(probes) == 1464
    render_proofs = ConfigurationRenderProofs(
        mermaid_version="11.16.0",
        sources=tuple((f"{index:04d}-{probe.id}", probe.source) for index, probe in enumerate(probes)),
    )
    expected_keys = tuple(key for key, _source in render_proofs.sources)
    partitioned_keys = tuple(key for shard_index in range(4) for key in render_proofs.shard(shard_index, 4))
    assert len(set(partitioned_keys)) == len(expected_keys)
    assert tuple(sorted(partitioned_keys)) == expected_keys
    for rendered in probes:
        document = yaml.safe_load(rendered.source.split("---\n", 2)[1])["config"]
        actual = (
            document[rendered.probe.field]
            if rendered.probe.field == "wrap"
            else document[config_keys[rendered.probe.diagram_id]][rendered.probe.field]
        )
        assert actual == rendered.probe.value


@pytest.mark.integration
@pytest.mark.parametrize(("shard_index", "shard_count"), CONFIGURATION_RENDER_SHARDS)
def test_every_configuration_probe_produces_a_real_svg(
    configuration_render_proofs: ConfigurationRenderProofs,
    shard_index: int,
    shard_count: int,
) -> None:
    sources = configuration_render_proofs.shard(shard_index, shard_count)

    svgs = ConfigurationProofRenderer(configuration_render_proofs.mermaid_version).render(sources)

    assert tuple(svgs) == tuple(sources)
