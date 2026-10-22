from mermaiden import Application
from tests.fixtures.c4_human_proofs import C4HumanProofCatalog


def test_application_renders_every_c4_mode_with_complex_content() -> None:
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

        assert element_count >= 12
        assert f'"c4ShapeInRow": {proof.shape_in_row}' in source
        assert f'"c4BoundaryInRow": {proof.boundary_in_row}' in source
        assert (
            f'UpdateLayoutConfig($c4ShapeInRow="{proof.shape_in_row}", $c4BoundaryInRow="{proof.boundary_in_row}")'
        ) in source
