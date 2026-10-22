import argparse

from configuration_proof_renderer import ConfigurationProofRenderer

from mermaiden import Application
from tests.fixtures.configuration_proofs import ConfigurationProofCatalog


class ConfigurationRenderingCheck:
    def run(self, shard_index: int, shard_count: int) -> None:
        with Application.create() as application:
            probes = ConfigurationProofCatalog(application).rendered_probes()
            cli_version = application.mermaid_cli_version
        sources = {
            f"{index:04d}-{probe.id}": probe.source
            for index, probe in enumerate(probes)
            if index % shard_count == shard_index
        }
        rendered = ConfigurationProofRenderer(cli_version).render(sources)
        if tuple(rendered) != tuple(sources):
            raise RuntimeError("Configuration rendering returned an incomplete or reordered result.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--shard-count", type=int, default=4)
    arguments = parser.parse_args()
    if arguments.shard < 1 or arguments.shard > arguments.shard_count:
        raise RuntimeError("Shard must be between 1 and shard-count.")
    ConfigurationRenderingCheck().run(arguments.shard - 1, arguments.shard_count)


if __name__ == "__main__":
    main()
