import yaml

from mermaiden import Application
from tests.fixtures.configuration_proofs import ConfigurationProofCatalog


def test_application_serializes_every_configuration_probe_exactly_after_snapshot_restoration() -> None:
    with Application.create() as application:
        catalog = ConfigurationProofCatalog(application)
        probes = catalog.rendered_probes()
        config_keys = {info.id: info.config_key for info in application.available_diagrams()}

    assert len({probe.probe.id for probe in probes}) == 549
    assert len(probes) == 1929
    for rendered in probes:
        document = yaml.safe_load(rendered.source.split("---\n", 2)[1])["config"]
        actual = (
            document[rendered.probe.field]
            if rendered.probe.field == "wrap"
            else document[config_keys[rendered.probe.diagram_id]][rendered.probe.field]
        )
        assert actual == rendered.probe.value
