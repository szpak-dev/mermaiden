from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright
from pydantic import BaseModel

from mermaiden import Application
from tests.fixtures.svg_geometry import SvgGeometryProbe


class SvgMeasurement(BaseModel):
    failures: tuple[str, ...]
    label_count: int
    wrapped_rows: int
    wrapped_labels: tuple[str, ...]
    mixed_height_neighbors: int
    foreign_object_count: int


@pytest.mark.integration
class TestExportedSvgLabels:
    def test_attack_long_class_signatures_remain_visible(self, tmp_path: Path) -> None:
        name = "class-attack"
        with Application.create() as application:
            diagram = application.create_diagram("classDiagram")
            application.execute(
                diagram,
                "add_class",
                {
                    "id": "long_class_example",
                    "label": "ExampleLongClassNameWithWideCharactersWWWW",
                    "attributes": [
                        {
                            "name": "long_field_name_example",
                            "type": {"name": "ExampleLongFieldType"},
                            "visibility": "private",
                        },
                        {"name": "count_example", "type": {"name": "int"}, "static": True},
                    ],
                    "methods": [
                        {
                            "name": "find_nested_example",
                            "visibility": "public",
                            "parameters": [
                                {
                                    "name": "values_example",
                                    "type": {
                                        "name": "Map",
                                        "arguments": [
                                            {"name": "ExampleKey"},
                                            {"name": "List", "arguments": [{"name": "ExampleValue"}]},
                                        ],
                                    },
                                },
                                {"name": "limit_example", "type": {"name": "int"}},
                            ],
                            "return_type": {
                                "name": "Map",
                                "arguments": [
                                    {"name": "ExampleKey"},
                                    {
                                        "name": "List",
                                        "arguments": [
                                            {
                                                "name": "Pair",
                                                "arguments": [{"name": "ExampleLeft"}, {"name": "ExampleRight"}],
                                            }
                                        ],
                                    },
                                ],
                            },
                        },
                        {
                            "name": "refresh_example",
                            "modifier": "abstract",
                            "return_type": {"name": "ExampleRefreshResult"},
                        },
                    ],
                },
            )
            application.execute(diagram, "add_class", {"id": "target_example", "label": "ExampleTarget"})
            application.execute(
                diagram,
                "add_relation",
                {
                    "id": "relation_example",
                    "source_id": "long_class_example",
                    "target_id": "target_example",
                    "relation_kind": "inheritance",
                },
            )
            before = application.snapshot(diagram).to_dict()
            source = application.render(diagram)
            report = application.validate_render(application.restore(before))
            if not report.success:
                pytest.fail(str(report.diagnostics))
            if application.snapshot(diagram).to_dict() != before or application.render(diagram) != source:
                pytest.fail("Rendering changed the accepted diagram content.")
            self.check_export(
                tmp_path,
                name,
                source,
                report.svg,
                (
                    "ExampleLongClassNameWithWideCharactersWWWW",
                    "-ExampleLongFieldType long_field_name_example",
                    "int count_example",
                    "+find_nested_example(Map<ExampleKey, List<ExampleValue>> values_example, int limit_example)",
                    "Map<ExampleKey, List<Pair<ExampleLeft, ExampleRight>>>",
                    "refresh_example()",
                    "ExampleRefreshResult",
                    "ExampleTarget",
                ),
            )

    def test_attack_adjacent_wrapped_attributes_and_methods_do_not_overlap(self, tmp_path: Path) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("classDiagram")
            application.execute(
                diagram,
                "add_class",
                {
                    "id": "resolver_example",
                    "label": "ExampleResolver",
                    "attributes": [
                        {"name": "active_example", "type": {"name": "bool"}},
                        {
                            "name": "configured_declaration_collection_example",
                            "type": {
                                "name": "ExampleDeclaration" * 10,
                            },
                        },
                    ],
                    "methods": [
                        {"name": "name", "return_type": {"name": "str"}},
                        {"name": "title", "return_type": {"name": "str"}},
                        {
                            "name": "resolve",
                            "parameters": [
                                {"name": "example_collection", "type": {"name": "ExampleCollectionMap"}},
                                {"name": "config", "type": {"name": "ExampleRules"}},
                            ],
                            "return_type": {"name": "tuple.ExampleResult"},
                        },
                        {
                            "name": "inspect_example_declarations",
                            "parameters": [
                                {"name": "example_id", "type": {"name": "str"}},
                                {"name": "declaration", "type": {"name": "ExampleDeclaration"}},
                                {"name": "config", "type": {"name": "ExampleRules"}},
                            ],
                            "return_type": {"name": "tuple.ExampleResult"},
                        },
                    ],
                },
            )
            before = application.snapshot(diagram).to_dict()
            source = application.render(diagram)
            report = application.validate_render(application.restore(before))
            assert report.success, report.diagnostics
            measurement = self.check_export(
                tmp_path,
                "wrapped-members-attack",
                source,
                report.svg,
                (
                    "ExampleResolver",
                    "active_example",
                    "configured_declaration_collection_example",
                    "ExampleDeclaration" * 10,
                    "name()",
                    "title()",
                    "resolve(",
                    "inspect_example_declarations(",
                    "ExampleCollectionMap",
                    "ExampleRules",
                    "ExampleDeclaration",
                    "tuple.ExampleResult",
                ),
            )
            assert measurement.label_count == 7
            assert measurement.wrapped_rows >= 2
            assert measurement.mixed_height_neighbors >= 2
            assert any("inspect_example_declarations" in label for label in measurement.wrapped_labels)
            assert any("configured_declaration_collection_example" in label for label in measurement.wrapped_labels)
            assert application.snapshot(diagram).to_dict() == before
            assert application.render(diagram) == source

    def test_preserves_treeview_readability(self, tmp_path: Path) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("treeView-beta")
            application.execute(diagram, "add_directory", {"id": "root_example", "label": "example_root"})
            application.execute(
                diagram,
                "add_file",
                {"id": "file_example", "label": "example_long_filename_with_wide_characters_WWWW.py"},
            )
            application.execute(
                diagram,
                "add_branch",
                {"id": "branch_example", "parent_id": "root_example", "child_id": "file_example"},
            )
            before = application.snapshot(diagram).to_dict()
            source = application.render(diagram)
            report = application.validate_render(diagram)
            if not report.success:
                pytest.fail(str(report.diagnostics))
            if application.snapshot(diagram).to_dict() != before or application.render(diagram) != source:
                pytest.fail("Rendering changed the accepted TreeView content.")
            self.check_export(
                tmp_path,
                "tree-invariant",
                source,
                report.svg,
                ("example_root", "example_long_filename_with_wide_characters_WWWW.py"),
            )

    def check_export(
        self, directory: Path, name: str, source: str, svg: str, expected: tuple[str, ...]
    ) -> SvgMeasurement:
        path = directory / f"{name}.svg"
        path.write_text(svg, encoding="utf-8")
        (directory / f"{name}.mmd").write_text(source, encoding="utf-8")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel="chromium")
            try:
                page = browser.new_page(viewport={"width": 1800, "height": 1600}, device_scale_factor=1)
                page.goto(path.as_uri())
                page.evaluate("async () => { await document.fonts.ready; }")
                measurement = SvgMeasurement.model_validate(
                    page.evaluate(
                        SvgGeometryProbe().script(),
                        {
                            "expected": expected,
                            "kind": "tree" if name == "tree-invariant" else "class",
                            "styled": name == "class-attack",
                        },
                    )
                )
                (directory / f"{name}.json").write_text(measurement.model_dump_json(indent=2), encoding="utf-8")
                assert measurement.label_count > 0
                assert measurement.failures == ()
                if name != "tree-invariant":
                    assert measurement.foreign_object_count == 0
                return measurement
            finally:
                browser.close()
