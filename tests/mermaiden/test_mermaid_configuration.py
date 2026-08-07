import pytest
from pydantic import ValidationError

from mermaiden.diagrams.block.configuration import BlockDiagramConfiguration
from mermaiden.diagrams.gitgraph.configuration import GitGraphDiagramConfiguration
from mermaiden.diagrams.requirement.configuration import RequirementDiagramConfiguration


def test_diagram_configuration_provides_a_source_keyed_mermaid_document() -> None:
    configuration = BlockDiagramConfiguration(padding=12)

    assert configuration.document("block").to_mermaid() == {
        "wrap": True,
        "block": {"padding": 12},
    }


def test_diagram_configuration_validates_its_values() -> None:
    with pytest.raises(ValidationError):
        BlockDiagramConfiguration(padding="invalid")


def test_configuration_serialization_converts_nested_keys_to_camel_case() -> None:
    assert GitGraphDiagramConfiguration().document("gitGraph").to_mermaid()["gitGraph"]["nodeLabel"] == {
        "width": 75,
        "height": 100,
        "x": -25,
        "y": 0,
    }
    requirement = RequirementDiagramConfiguration().document("requirement").to_mermaid()

    assert requirement["requirement"]["rectFill"] == "#f9f9f9"
