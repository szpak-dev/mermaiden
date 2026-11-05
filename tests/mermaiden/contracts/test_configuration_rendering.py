import pytest

from mermaiden import Application
from tests.fixtures.configuration_proof_renderer import ConfigurationProofRenderer
from tests.fixtures.configuration_proofs import ConfigurationProofCatalog


@pytest.mark.integration
@pytest.mark.configuration_render
@pytest.mark.parametrize("shard", (1, 2, 3, 4))
def test_configuration_probes_produce_valid_svg_in_order(shard: int) -> None:
    with Application.create() as application:
        probes = ConfigurationProofCatalog(application).rendered_probes()
        sources = {
            f"{index:04d}-{probe.id}": probe.source for index, probe in enumerate(probes) if index % 4 == shard - 1
        }
        rendered = ConfigurationProofRenderer(application).render(sources)
        assert tuple(rendered) == tuple(sources)
