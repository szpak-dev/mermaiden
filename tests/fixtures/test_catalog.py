from pathlib import Path

from mermaiden import Application
from tests.fixtures.catalog import FixtureCatalog


def test_exposes_one_populated_fixture_for_every_registered_diagram() -> None:
    with Application.create() as application:
        expected = tuple(info.id for info in application.available_diagrams())
        diagrams = FixtureCatalog(application).render()

    assert tuple(diagrams) == expected
    assert all(source.startswith("---\nconfig:\n") for source in diagrams.values())
    assert all(source.endswith("\n") for source in diagrams.values())


def test_writes_syntax_named_fixtures_without_changing_source(tmp_path: Path) -> None:
    with Application.create() as application:
        fixtures = FixtureCatalog(application)
        expected = fixtures.render()
        paths = fixtures.write(tmp_path)

    assert tuple(path.name for path in paths) == tuple(f"{diagram_id}.mmd" for diagram_id in expected)
    assert {path.stem: path.read_text(encoding="utf-8") for path in paths} == expected
