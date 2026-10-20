from dataclasses import dataclass

from mermaiden import Application

from .models import DiagramFixture, FixtureCommand, FixtureDefinition


@dataclass(frozen=True, slots=True)
class AnalyticalFixtureBuilder:
    application: Application

    def fixtures(self) -> tuple[DiagramFixture, ...]:
        builder = type(self).__name__
        definitions = (
            FixtureDefinition(
                "requirementDiagram",
                (
                    FixtureCommand(
                        "add_requirement",
                        {
                            "id": "system",
                            "requirement_id": "REQ-001",
                            "text": "The system provides secure access.",
                            "requirement_type": "requirement",
                            "risk": "high",
                            "verification_method": "test",
                        },
                    ),
                    FixtureCommand(
                        "add_requirement",
                        {
                            "id": "login",
                            "requirement_id": "REQ-002",
                            "text": "Users can sign in.",
                            "requirement_type": "functionalRequirement",
                            "risk": "medium",
                            "verification_method": "demonstration",
                        },
                    ),
                    FixtureCommand(
                        "add_requirement",
                        {
                            "id": "api",
                            "requirement_id": "REQ-003",
                            "text": "The API is documented.",
                            "requirement_type": "interfaceRequirement",
                            "risk": "low",
                            "verification_method": "inspection",
                        },
                    ),
                    FixtureCommand(
                        "add_requirement",
                        {
                            "id": "latency",
                            "requirement_id": "REQ-004",
                            "text": "Responses complete within 100ms.",
                            "requirement_type": "performanceRequirement",
                            "risk": "high",
                            "verification_method": "analysis",
                        },
                    ),
                    FixtureCommand(
                        "add_requirement",
                        {
                            "id": "device",
                            "requirement_id": "REQ-005",
                            "text": "The device withstands heat.",
                            "requirement_type": "physicalRequirement",
                            "risk": "medium",
                            "verification_method": "test",
                        },
                    ),
                    FixtureCommand(
                        "add_requirement",
                        {
                            "id": "policy",
                            "requirement_id": "REQ-006",
                            "text": "Access follows policy.",
                            "requirement_type": "designConstraint",
                            "risk": "low",
                            "verification_method": "inspection",
                        },
                    ),
                    FixtureCommand(
                        "add_element",
                        {
                            "id": "service",
                            "element_type": "software",
                            "document_reference": "docs/service.md",
                        },
                    ),
                    FixtureCommand(
                        "add_element",
                        {
                            "id": "test_suite",
                            "element_type": "test",
                            "document_reference": "tests/requirements.py",
                        },
                    ),
                    FixtureCommand(
                        "add_relation",
                        {
                            "id": "system_contains_login",
                            "source_id": "system",
                            "target_id": "login",
                            "relation_kind": "contains",
                        },
                    ),
                    FixtureCommand(
                        "add_relation",
                        {"id": "login_copies_api", "source_id": "login", "target_id": "api", "relation_kind": "copies"},
                    ),
                    FixtureCommand(
                        "add_relation",
                        {
                            "id": "api_derives_latency",
                            "source_id": "api",
                            "target_id": "latency",
                            "relation_kind": "derives",
                        },
                    ),
                    FixtureCommand(
                        "add_relation",
                        {
                            "id": "service_satisfies_system",
                            "source_id": "service",
                            "target_id": "system",
                            "relation_kind": "satisfies",
                        },
                    ),
                    FixtureCommand(
                        "add_relation",
                        {
                            "id": "test_verifies_login",
                            "source_id": "test_suite",
                            "target_id": "login",
                            "relation_kind": "verifies",
                        },
                    ),
                    FixtureCommand(
                        "add_relation",
                        {
                            "id": "policy_refines_system",
                            "source_id": "policy",
                            "target_id": "system",
                            "relation_kind": "refines",
                        },
                    ),
                    FixtureCommand(
                        "add_relation",
                        {
                            "id": "device_traces_policy",
                            "source_id": "device",
                            "target_id": "policy",
                            "relation_kind": "traces",
                        },
                    ),
                ),
            ),
            FixtureDefinition(
                "mindmap",
                (
                    FixtureCommand("add_root", {"id": "root", "label": "Mermaiden"}),
                    FixtureCommand("add_node", {"id": "domain", "label": "Domain model", "parent_id": "root"}),
                    FixtureCommand("add_square", {"id": "contracts", "label": "Contracts", "parent_id": "domain"}),
                    FixtureCommand(
                        "add_rounded_square", {"id": "services", "label": "Services", "parent_id": "domain"}
                    ),
                    FixtureCommand("add_circle", {"id": "runtime", "label": "Runtime", "parent_id": "root"}),
                    FixtureCommand("add_bang", {"id": "warning", "label": "Important", "parent_id": "runtime"}),
                    FixtureCommand("add_cloud", {"id": "cloud", "label": "Cloud", "parent_id": "runtime"}),
                    FixtureCommand("add_hexagon", {"id": "quality", "label": "Quality", "parent_id": "root"}),
                    FixtureCommand("add_node", {"id": "commands", "label": "Commands", "parent_id": "contracts"}),
                    FixtureCommand("add_node", {"id": "snapshots", "label": "Snapshots", "parent_id": "contracts"}),
                    FixtureCommand("add_node", {"id": "transactions", "label": "Transactions", "parent_id": "runtime"}),
                    FixtureCommand("add_node", {"id": "rendering", "label": "Rendering", "parent_id": "quality"}),
                ),
            ),
            FixtureDefinition(
                "pie",
                (
                    FixtureCommand("set_title", {"title": "Adopted pets"}),
                    FixtureCommand("show_values", {}),
                    FixtureCommand("add_slice", {"id": "dogs", "label": "Dogs", "value": 386}),
                    FixtureCommand("add_slice", {"id": "cats", "label": "Cats", "value": 85}),
                    FixtureCommand("add_slice", {"id": "rats", "label": "Rats", "value": 15}),
                    FixtureCommand("add_slice", {"id": "rabbits", "label": "Rabbits", "value": 42}),
                    FixtureCommand("add_slice", {"id": "birds", "label": "Birds", "value": 31}),
                    FixtureCommand("add_slice", {"id": "fish", "label": "Fish", "value": 27}),
                    FixtureCommand("add_slice", {"id": "hamsters", "label": "Hamsters", "value": 19}),
                    FixtureCommand("add_slice", {"id": "turtles", "label": "Turtles", "value": 12}),
                    FixtureCommand("add_slice", {"id": "snakes", "label": "Snakes", "value": 8}),
                    FixtureCommand("add_slice", {"id": "lizards", "label": "Lizards", "value": 7}),
                    FixtureCommand("add_slice", {"id": "ferrets", "label": "Ferrets", "value": 5}),
                    FixtureCommand("add_slice", {"id": "other", "label": "Other", "value": 11}),
                ),
            ),
            FixtureDefinition(
                "sankey",
                (
                    FixtureCommand("add_node", {"id": "grid", "label": "Electricity grid"}),
                    FixtureCommand("add_node", {"id": "industry", "label": "Industry"}),
                    FixtureCommand("add_node", {"id": "homes", "label": "Homes"}),
                    FixtureCommand("add_node", {"id": "solar", "label": "Solar farms"}),
                    FixtureCommand("add_node", {"id": "wind", "label": "Wind farms"}),
                    FixtureCommand("add_node", {"id": "storage", "label": "Battery storage"}),
                    FixtureCommand("add_node", {"id": "commercial", "label": "Commercial buildings"}),
                    FixtureCommand("add_node", {"id": "losses", "label": "Transmission losses"}),
                    FixtureCommand(
                        "add_flow",
                        {"id": "grid_industry", "source_id": "grid", "target_id": "industry", "value": 342.165},
                    ),
                    FixtureCommand(
                        "add_flow", {"id": "grid_homes", "source_id": "grid", "target_id": "homes", "value": 113.726}
                    ),
                    FixtureCommand(
                        "add_flow", {"id": "solar_grid", "source_id": "solar", "target_id": "grid", "value": 180.5}
                    ),
                    FixtureCommand(
                        "add_flow", {"id": "wind_grid", "source_id": "wind", "target_id": "grid", "value": 240.75}
                    ),
                    FixtureCommand(
                        "add_flow", {"id": "grid_storage", "source_id": "grid", "target_id": "storage", "value": 45.5}
                    ),
                    FixtureCommand(
                        "add_flow",
                        {"id": "grid_commercial", "source_id": "grid", "target_id": "commercial", "value": 96.25},
                    ),
                    FixtureCommand(
                        "add_flow", {"id": "grid_losses", "source_id": "grid", "target_id": "losses", "value": 28.4}
                    ),
                    FixtureCommand(
                        "add_flow", {"id": "storage_homes", "source_id": "storage", "target_id": "homes", "value": 22.0}
                    ),
                ),
            ),
            FixtureDefinition(
                "venn-beta",
                (
                    FixtureCommand("add_set", {"id": "frontend", "label": "Frontend", "size": 20}),
                    FixtureCommand("add_text", {"id": "react", "label": "React", "parent_id": "frontend"}),
                    FixtureCommand("add_set", {"id": "backend", "label": "Backend", "size": 12}),
                    FixtureCommand("add_text", {"id": "api", "label": "API", "parent_id": "backend"}),
                    FixtureCommand("add_set", {"id": "operations", "label": "Operations", "size": 16}),
                    FixtureCommand("add_text", {"id": "platform", "label": "Platform", "parent_id": "operations"}),
                    FixtureCommand("add_set", {"id": "compliance", "label": "Compliance", "size": 10}),
                    FixtureCommand("add_text", {"id": "audit", "label": "Audit", "parent_id": "compliance"}),
                    FixtureCommand(
                        "add_union", {"id": "shared", "label": "Shared", "set_ids": ["frontend", "backend"], "size": 3}
                    ),
                    FixtureCommand("add_text", {"id": "openapi", "label": "OpenAPI", "parent_id": "shared"}),
                    FixtureCommand(
                        "add_union",
                        {"id": "delivery", "label": "Delivery", "set_ids": ["frontend", "operations"], "size": 4},
                    ),
                    FixtureCommand("add_text", {"id": "pipeline", "label": "Pipeline", "parent_id": "delivery"}),
                    FixtureCommand(
                        "add_union",
                        {"id": "governance", "label": "Governance", "set_ids": ["backend", "compliance"], "size": 2},
                    ),
                    FixtureCommand("add_text", {"id": "policy", "label": "Policy", "parent_id": "governance"}),
                ),
            ),
            FixtureDefinition(
                "radar-beta",
                (
                    FixtureCommand("set_title", {"title": "Restaurant comparison"}),
                    FixtureCommand("add_axis", {"id": "food", "label": "Food quality"}),
                    FixtureCommand("add_axis", {"id": "service", "label": "Service"}),
                    FixtureCommand("add_axis", {"id": "price", "label": "Price"}),
                    FixtureCommand("add_axis", {"id": "ambience", "label": "Ambience"}),
                    FixtureCommand("add_axis", {"id": "location", "label": "Location"}),
                    FixtureCommand("add_axis", {"id": "sustainability", "label": "Sustainability"}),
                    FixtureCommand(
                        "add_curve", {"id": "restaurant_a", "label": "Restaurant A", "values": [4, 3, 2, 5, 4, 3]}
                    ),
                    FixtureCommand(
                        "add_curve", {"id": "restaurant_b", "label": "Restaurant B", "values": [3, 4, 3, 2, 5, 4]}
                    ),
                    FixtureCommand(
                        "add_curve", {"id": "restaurant_c", "label": "Restaurant C", "values": [5, 2, 4, 4, 3, 5]}
                    ),
                    FixtureCommand(
                        "add_curve", {"id": "restaurant_d", "label": "Restaurant D", "values": [2, 5, 5, 3, 2, 4]}
                    ),
                    FixtureCommand(
                        "add_curve", {"id": "restaurant_e", "label": "Restaurant E", "values": [4, 4, 3, 4, 4, 2]}
                    ),
                    FixtureCommand(
                        "add_curve", {"id": "restaurant_f", "label": "Restaurant F", "values": [3, 3, 5, 5, 3, 3]}
                    ),
                    FixtureCommand("set_range", {"minimum": 0, "maximum": 5}),
                    FixtureCommand("set_graticule", {"graticule": "polygon"}),
                    FixtureCommand("set_ticks", {"ticks": 5}),
                ),
            ),
            FixtureDefinition(
                "packet",
                (
                    FixtureCommand("set_title", {"title": "UDP packet"}),
                    FixtureCommand("add_bits", {"id": "source", "label": "Source port", "bits": 16}),
                    FixtureCommand("add_bits", {"id": "destination", "label": "Destination port", "bits": 16}),
                    FixtureCommand("add_field", {"id": "length", "label": "Length", "start": 32, "end": 47}),
                    FixtureCommand("add_field", {"id": "checksum", "label": "Checksum", "start": 48, "end": 63}),
                    FixtureCommand("add_field", {"id": "payload_1", "label": "Payload 1", "start": 64, "end": 79}),
                    FixtureCommand("add_field", {"id": "payload_2", "label": "Payload 2", "start": 80, "end": 95}),
                    FixtureCommand("add_field", {"id": "payload_3", "label": "Payload 3", "start": 96, "end": 111}),
                    FixtureCommand("add_field", {"id": "payload_4", "label": "Payload 4", "start": 112, "end": 127}),
                    FixtureCommand("add_field", {"id": "payload_5", "label": "Payload 5", "start": 128, "end": 143}),
                    FixtureCommand("add_field", {"id": "payload_6", "label": "Payload 6", "start": 144, "end": 159}),
                    FixtureCommand("add_field", {"id": "payload_7", "label": "Payload 7", "start": 160, "end": 175}),
                    FixtureCommand("add_field", {"id": "payload_8", "label": "Payload 8", "start": 176, "end": 191}),
                ),
            ),
            FixtureDefinition(
                "erDiagram",
                (
                    FixtureCommand("add_entity", {"id": "CUSTOMER", "label": "Customer"}),
                    FixtureCommand(
                        "add_attribute",
                        {
                            "id": "customer_id",
                            "label": "id",
                            "data_type": "int",
                            "entity_id": "CUSTOMER",
                            "keys": ["PK"],
                        },
                    ),
                    FixtureCommand("add_entity", {"id": "ORDER", "label": "Order"}),
                    FixtureCommand(
                        "add_attribute",
                        {
                            "id": "order_id",
                            "label": "id",
                            "data_type": "int",
                            "entity_id": "ORDER",
                            "keys": ["PK"],
                        },
                    ),
                    FixtureCommand(
                        "add_relationship",
                        {
                            "id": "places",
                            "source_id": "CUSTOMER",
                            "target_id": "ORDER",
                            "label": 'references content; "protected" — while scoped: [v2] #1 & <trusted>',
                            "target_cardinality": "zero_or_more",
                        },
                    ),
                    FixtureCommand("add_entity", {"id": "PRODUCT", "label": "Product"}),
                    FixtureCommand(
                        "add_attribute",
                        {"id": "product_id", "label": "id", "data_type": "int", "entity_id": "PRODUCT", "keys": ["PK"]},
                    ),
                    FixtureCommand("add_entity", {"id": "PAYMENT", "label": "Payment"}),
                    FixtureCommand(
                        "add_attribute",
                        {"id": "payment_id", "label": "id", "data_type": "int", "entity_id": "PAYMENT", "keys": ["PK"]},
                    ),
                    FixtureCommand("add_entity", {"id": "SHIPMENT", "label": "Shipment"}),
                    FixtureCommand(
                        "add_attribute",
                        {
                            "id": "shipment_id",
                            "label": "id",
                            "data_type": "int",
                            "entity_id": "SHIPMENT",
                            "keys": ["PK"],
                        },
                    ),
                    FixtureCommand("add_entity", {"id": "INVOICE", "label": "Invoice"}),
                    FixtureCommand(
                        "add_attribute",
                        {"id": "invoice_id", "label": "id", "data_type": "int", "entity_id": "INVOICE", "keys": ["PK"]},
                    ),
                    FixtureCommand(
                        "add_relationship",
                        {
                            "id": "contains",
                            "source_id": "ORDER",
                            "target_id": "PRODUCT",
                            "label": "contains",
                            "target_cardinality": "one_or_more",
                        },
                    ),
                    FixtureCommand(
                        "add_relationship",
                        {
                            "id": "paid_by",
                            "source_id": "ORDER",
                            "target_id": "PAYMENT",
                            "label": "paid by",
                            "target_cardinality": "zero_or_one",
                        },
                    ),
                    FixtureCommand(
                        "add_relationship",
                        {
                            "id": "ships_as",
                            "source_id": "ORDER",
                            "target_id": "SHIPMENT",
                            "label": "ships as",
                            "target_cardinality": "zero_or_one",
                        },
                    ),
                    FixtureCommand(
                        "add_relationship",
                        {
                            "id": "invoiced_as",
                            "source_id": "ORDER",
                            "target_id": "INVOICE",
                            "label": "invoiced as",
                            "target_cardinality": "exactly_one",
                        },
                    ),
                ),
            ),
        )
        return tuple(definition.build(self.application, builder) for definition in definitions)
