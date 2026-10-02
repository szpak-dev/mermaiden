import json
from collections.abc import Mapping

import pytest

from mermaiden import Application


@pytest.fixture(scope="module")
def application() -> Application:
    return Application.create()


class TestClassMembers:
    @pytest.mark.parametrize(
        "name", ("", " ", "total()", "+total", "total$", "total*", "total\n", "total}\nclass Extra {")
    )
    @pytest.mark.parametrize("update", (False, True))
    @pytest.mark.parametrize("member_kind", ("attribute", "method", "parameter"))
    def test_member_names_cannot_contain_signatures_or_diagram_syntax(
        self, application: Application, name: str, update: bool, member_kind: str
    ) -> None:
        diagram = application.create_diagram("classDiagram")
        application.execute(diagram, "add_class", {"id": "order", "label": "Order"})
        before = application.snapshot(diagram).to_dict()
        source = application.render(diagram)
        changes: dict[str, object] = {"attributes": [{"name": name, "type": {"name": "Decimal"}}]}
        if member_kind == "method":
            changes = {"methods": [{"name": name, "return_type": {"name": "void"}}]}
        elif member_kind == "parameter":
            changes = {
                "methods": [
                    {
                        "name": "submit",
                        "return_type": {"name": "void"},
                        "parameters": [{"name": name, "type": {"name": "Decimal"}}],
                    }
                ]
            }

        with pytest.raises((RuntimeError, ValueError), match="name"):
            if update:
                application.execute(diagram, "update_element", {"id": "order", "kind": "class", "changes": changes})
            else:
                application.execute(diagram, "add_class", {"id": "invoice", "label": "Invoice", **changes})

        assert application.snapshot(diagram).to_dict() == before
        assert application.render(diagram) == source

    @pytest.mark.parametrize(
        "field,value",
        (
            ("attributes", ["+Decimal total"]),
            ("methods", ["submit() void"]),
            ("methods", [{"name": "submit", "return_type": {"name": "void"}, "parameters": ["id: str"]}]),
        ),
    )
    @pytest.mark.parametrize("update", (False, True))
    def test_members_and_parameters_require_structured_values(
        self, application: Application, field: str, value: object, update: bool
    ) -> None:
        diagram = application.create_diagram("classDiagram")
        application.execute(diagram, "add_class", {"id": "order", "label": "Order"})
        before = application.snapshot(diagram).to_dict()

        with pytest.raises((RuntimeError, ValueError), match=field):
            if update:
                application.execute(
                    diagram, "update_element", {"id": "order", "kind": "class", "changes": {field: value}}
                )
            else:
                application.execute(diagram, "add_class", {"id": "invoice", "label": "Invoice", field: value})

        assert application.snapshot(diagram).to_dict() == before

    @pytest.mark.parametrize("values", ({}, {"type": None}, {"type": "str"}))
    @pytest.mark.parametrize("member_kind", ("attribute", "parameter"))
    def test_properties_and_parameters_require_an_explicit_type(
        self, application: Application, values: Mapping[str, object], member_kind: str
    ) -> None:
        diagram = application.create_diagram("classDiagram")
        before = application.snapshot(diagram).to_dict()
        member = {"name": "id", **values}
        members = (
            {"attributes": [member]}
            if member_kind == "attribute"
            else {"methods": [{"name": "find", "return_type": {"name": "Order"}, "parameters": [member]}]}
        )

        with pytest.raises(RuntimeError, match="type"):
            application.execute(diagram, "add_class", {"id": "order", "label": "Order", **members})

        assert application.snapshot(diagram).to_dict() == before

    @pytest.mark.parametrize("values", ({}, {"return_type": None}, {"return_type": "void"}))
    def test_methods_require_an_explicit_return_type(
        self, application: Application, values: Mapping[str, object]
    ) -> None:
        diagram = application.create_diagram("classDiagram")
        before = application.snapshot(diagram).to_dict()

        with pytest.raises(RuntimeError, match="return_type"):
            application.execute(
                diagram,
                "add_class",
                {
                    "id": "order",
                    "label": "Order",
                    "methods": [{"name": "submit", **values}],
                },
            )

        assert application.snapshot(diagram).to_dict() == before

    @pytest.mark.parametrize(
        "value",
        (
            {"name": ""},
            {"name": "List[str]"},
            {"name": "str | None"},
            {"name": "str\nclass Extra"},
            {"name": "List", "arguments": [None]},
            {"name": "List", "arguments": "str"},
            {"name": "str", "nullable": True},
        ),
    )
    def test_type_values_reject_unsupported_forms(self, application: Application, value: Mapping[str, object]) -> None:
        diagram = application.create_diagram("classDiagram")
        before = application.snapshot(diagram).to_dict()

        with pytest.raises(RuntimeError, match="type"):
            application.execute(
                diagram,
                "add_class",
                {
                    "id": "order",
                    "label": "Order",
                    "attributes": [{"name": "items", "type": value}],
                },
            )

        assert application.snapshot(diagram).to_dict() == before

    @pytest.mark.parametrize("visibility", ("public", "private", "protected", "package"))
    def test_visibility_and_multi_argument_types_survive_restore_and_edit(
        self, application: Application, visibility: str
    ) -> None:
        diagram = application.create_diagram("classDiagram")
        attribute_type: dict[str, object] = {
            "name": "Map",
            "arguments": [{"name": "Key", "arguments": []}, {"name": "Value", "arguments": []}],
        }
        parameter_type: dict[str, object] = {
            "name": "Map",
            "arguments": [
                {"name": "Key", "arguments": []},
                {"name": "List", "arguments": [{"name": "Value", "arguments": []}]},
            ],
        }
        return_type: dict[str, object] = {
            "name": "Map",
            "arguments": [
                {"name": "Key", "arguments": []},
                {
                    "name": "List",
                    "arguments": [
                        {
                            "name": "Pair",
                            "arguments": [
                                {"name": "Left", "arguments": []},
                                {"name": "Right", "arguments": []},
                            ],
                        }
                    ],
                },
            ],
        }
        attribute: dict[str, object] = {
            "name": "items",
            "type": attribute_type,
            "visibility": visibility,
            "static": False,
        }
        method: dict[str, object] = {
            "name": "find",
            "parameters": [{"name": "key", "type": parameter_type}],
            "return_type": return_type,
            "visibility": visibility,
            "modifier": "instance",
        }
        application.execute(
            diagram, "add_class", {"id": "order", "label": "Order", "attributes": [attribute], "methods": [method]}
        )
        before = application.snapshot(diagram).to_dict()

        restored = application.restore(json.loads(json.dumps(before)))
        order = restored.find_element("order")
        assert order is not None
        assert order.model_dump(mode="json")["attributes"] == [attribute]
        assert order.model_dump(mode="json")["methods"] == [method]
        assert application.snapshot(restored).to_dict() == before
        assert application.render(restored) == application.render(diagram)

        changed_attribute: dict[str, object] = {
            **attribute,
            "type": {
                "name": "Result",
                "arguments": [
                    {"name": "Code", "arguments": []},
                    {"name": "List", "arguments": [{"name": "Error", "arguments": []}]},
                ],
            },
        }
        changed_method: dict[str, object] = {
            **method,
            "name": "lookup",
            "parameters": [
                {
                    "name": "key",
                    "type": {
                        "name": "Mapping",
                        "arguments": [
                            {"name": "Key", "arguments": []},
                            {"name": "Set", "arguments": [{"name": "Value", "arguments": []}]},
                        ],
                    },
                }
            ],
            "return_type": {
                "name": "Either",
                "arguments": [
                    {"name": "Failure", "arguments": []},
                    {
                        "name": "List",
                        "arguments": [
                            {
                                "name": "Pair",
                                "arguments": [
                                    {"name": "Left", "arguments": []},
                                    {"name": "Right", "arguments": []},
                                ],
                            }
                        ],
                    },
                ],
            },
        }
        application.execute(
            restored,
            "update_element",
            {
                "id": "order",
                "kind": "class",
                "changes": {"attributes": [changed_attribute], "methods": [changed_method]},
            },
        )
        edited_snapshot = application.snapshot(restored).to_dict()
        edited_diagram = application.restore(json.loads(json.dumps(edited_snapshot)))
        edited = edited_diagram.find_element("order")
        assert edited is not None
        assert edited.model_dump(mode="json")["attributes"] == [changed_attribute]
        assert edited.model_dump(mode="json")["methods"] == [changed_method]
        source = application.render(edited_diagram)
        assert "Result~Code, List&lt;Error&gt;~ items" in source
        assert (
            "lookup(Mapping~Key, Set&lt;Value&gt;~ key) Either~Failure, List&lt;Pair&lt;Left&comma; Right&gt;&gt;~"
            in source
        )
        assert "find(" not in source

    @pytest.mark.parametrize("visibility", ("+", "-", "#", "~", "Public", "", None))
    @pytest.mark.parametrize("collection,type_field", (("attributes", "type"), ("methods", "return_type")))
    def test_visibility_rejects_symbols_and_unknown_values(
        self, application: Application, visibility: object, collection: str, type_field: str
    ) -> None:
        diagram = application.create_diagram("classDiagram")
        before = application.snapshot(diagram).to_dict()

        with pytest.raises(RuntimeError, match="visibility"):
            application.execute(
                diagram,
                "add_class",
                {
                    "id": "order",
                    "label": "Order",
                    collection: [{"name": "total", type_field: {"name": "Decimal"}, "visibility": visibility}],
                },
            )

        assert application.snapshot(diagram).to_dict() == before

    @pytest.mark.parametrize("modifier,suffix", (("instance", ""), ("static", "$"), ("abstract", "*")))
    def test_method_modifiers_have_explicit_rendered_meaning(
        self, application: Application, modifier: str, suffix: str
    ) -> None:
        diagram = application.create_diagram("classDiagram")
        application.execute(diagram, "configure", {"wrap": False})
        application.execute(
            diagram,
            "add_class",
            {
                "id": "order",
                "label": "Order",
                "methods": [{"name": "submit", "return_type": {"name": "void"}, "modifier": modifier}],
            },
        )

        assert (
            application.render(diagram) == "---\nconfig:\n  wrap: false\n---\nclassDiagram\n"
            f'class c_v_order["Order"] {{\n  +submit() void{suffix}\n}}\n'
        )

    @pytest.mark.parametrize(
        "field,value",
        (
            ("attributes", [{"name": "total", "type": {"name": "Decimal"}}] * 2),
            ("methods", [{"name": "submit", "return_type": {"name": "void"}}] * 2),
            (
                "methods",
                [
                    {
                        "name": "submit",
                        "return_type": {"name": "void"},
                        "parameters": [{"name": "id", "type": {"name": "str"}}] * 2,
                    }
                ],
            ),
        ),
    )
    def test_duplicate_member_identities_do_not_replace_existing_members(
        self, application: Application, field: str, value: object
    ) -> None:
        diagram = application.create_diagram("classDiagram")
        application.execute(diagram, "add_class", {"id": "order", "label": "Order"})
        before = application.snapshot(diagram).to_dict()

        with pytest.raises((RuntimeError, ValueError), match=r"unique|distinct"):
            application.execute(diagram, "update_element", {"id": "order", "kind": "class", "changes": {field: value}})

        assert application.snapshot(diagram).to_dict() == before
        application.execute(
            diagram,
            "update_element",
            {
                "id": "order",
                "kind": "class",
                "changes": {
                    "attributes": [{"name": "total", "type": {"name": "Decimal"}}],
                },
            },
        )
        assert "+Decimal total" in application.render(diagram)

    def test_overloads_preserve_parameter_and_method_order(self, application: Application) -> None:
        diagram = application.create_diagram("classDiagram")
        methods = [
            {"name": "find", "return_type": {"name": "Item"}, "parameters": [{"name": "id", "type": {"name": "UUID"}}]},
            {
                "name": "find",
                "return_type": {"name": "Item"},
                "parameters": [
                    {"name": "name", "type": {"name": "str"}},
                    {"name": "limit", "type": {"name": "int"}},
                ],
            },
        ]
        application.execute(diagram, "add_class", {"id": "catalog", "label": "Catalog", "methods": methods})
        restored = application.restore(application.snapshot(diagram).to_dict())

        source = application.render(restored)
        assert source.index("find(UUID id)") < source.index("find(str name, int limit)")
