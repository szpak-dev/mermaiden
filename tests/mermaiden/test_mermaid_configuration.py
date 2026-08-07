import pytest
from pydantic import ValidationError

from mermaiden.diagrams.block.configuration import BlockDiagramConfiguration


def test_diagram_configuration_provides_a_source_keyed_mermaid_document() -> None:
    configuration = BlockDiagramConfiguration(padding=12)

    assert configuration.document("block").to_mermaid() == {
        "wrap": True,
        "block": {"padding": 12},
    }


def test_diagram_configuration_validates_its_values() -> None:
    with pytest.raises(ValidationError):
        BlockDiagramConfiguration(padding="invalid")
