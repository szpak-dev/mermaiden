from dataclasses import dataclass

from mermaiden import Application

from .models import DiagramFixture, FixtureCommand, FixtureDefinition


@dataclass(frozen=True, slots=True)
class StructuralFixtureBuilder:
    application: Application

    def fixtures(self) -> tuple[DiagramFixture, ...]:
        builder = type(self).__name__
        definitions = (
            FixtureDefinition(
                "flowchart",
                (
                    FixtureCommand("add_group", {"id": "entry", "label": "Entry"}),
                    FixtureCommand("add_group", {"id": "process", "label": "Process"}),
                    FixtureCommand("add_start", {"id": "start", "label": "Start", "parent_id": "entry"}),
                    FixtureCommand("add_decision", {"id": "ready", "label": "Ready?", "parent_id": "entry"}),
                    FixtureCommand("add_action", {"id": "work", "label": "Work", "parent_id": "process"}),
                    FixtureCommand("add_node", {"id": "node", "label": "Node", "parent_id": "process"}),
                    FixtureCommand("add_input_output", {"id": "input", "label": "Input", "parent_id": "process"}),
                    FixtureCommand("add_data_store", {"id": "data", "label": "Data", "parent_id": "process"}),
                    FixtureCommand("add_document", {"id": "document", "label": "Document", "parent_id": "process"}),
                    FixtureCommand(
                        "add_subprocess", {"id": "subprocess", "label": "Subprocess", "parent_id": "process"}
                    ),
                    FixtureCommand("add_junction", {"id": "junction", "label": "Junction", "parent_id": "process"}),
                    FixtureCommand("add_end", {"id": "end", "label": "End", "parent_id": "process"}),
                    FixtureCommand(
                        "add_end", {"id": "alternate_end", "label": "Alternate end", "parent_id": "process"}
                    ),
                    FixtureCommand("add_flow", {"id": "start_ready", "source_id": "start", "target_id": "ready"}),
                    FixtureCommand(
                        "add_conditional_flow",
                        {"id": "ready_work", "source_id": "ready", "target_id": "work", "condition": "yes"},
                    ),
                    FixtureCommand(
                        "add_conditional_flow",
                        {"id": "ready_node", "source_id": "ready", "target_id": "node", "condition": "no"},
                    ),
                    FixtureCommand("add_flow", {"id": "work_node", "source_id": "work", "target_id": "node"}),
                    FixtureCommand("add_flow", {"id": "node_input", "source_id": "node", "target_id": "input"}),
                    FixtureCommand("add_flow", {"id": "input_data", "source_id": "input", "target_id": "data"}),
                    FixtureCommand("add_flow", {"id": "data_document", "source_id": "data", "target_id": "document"}),
                    FixtureCommand(
                        "add_flow", {"id": "document_subprocess", "source_id": "document", "target_id": "subprocess"}
                    ),
                    FixtureCommand(
                        "add_flow", {"id": "subprocess_junction", "source_id": "subprocess", "target_id": "junction"}
                    ),
                    FixtureCommand("add_flow", {"id": "junction_end", "source_id": "junction", "target_id": "end"}),
                    FixtureCommand(
                        "add_flow", {"id": "junction_alternate", "source_id": "junction", "target_id": "alternate_end"}
                    ),
                    FixtureCommand("add_note", {"id": "start_note", "text": "Start process", "element_ids": ["start"]}),
                    FixtureCommand("add_note", {"id": "work_note", "text": "Process work", "element_ids": ["work"]}),
                    FixtureCommand("add_note", {"id": "end_note", "text": "Finish process", "element_ids": ["end"]}),
                ),
            ),
            FixtureDefinition(
                "treeView-beta",
                (
                    FixtureCommand("add_directory", {"id": "root", "label": "root"}),
                    FixtureCommand("add_directory", {"id": "source", "label": "src"}),
                    FixtureCommand("add_directory", {"id": "package", "label": "mermaiden"}),
                    FixtureCommand("add_directory", {"id": "tests", "label": "tests"}),
                    FixtureCommand("add_file", {"id": "readme", "label": "README.md"}),
                    FixtureCommand("add_item", {"id": "overview", "label": "Overview"}),
                    FixtureCommand("add_annotation", {"id": "source_note", "element_id": "source", "icon": "folder"}),
                    FixtureCommand("add_branch", {"id": "root_source", "parent_id": "root", "child_id": "source"}),
                    FixtureCommand("add_annotation", {"id": "tests_note", "element_id": "tests", "icon": "test"}),
                    FixtureCommand("add_branch", {"id": "root_tests", "parent_id": "root", "child_id": "tests"}),
                    FixtureCommand(
                        "add_branch", {"id": "source_package", "parent_id": "source", "child_id": "package"}
                    ),
                    FixtureCommand("add_branch", {"id": "root_readme", "parent_id": "root", "child_id": "readme"}),
                    FixtureCommand("add_branch", {"id": "root_overview", "parent_id": "root", "child_id": "overview"}),
                    FixtureCommand(
                        "add_annotation",
                        {
                            "id": "readme_note",
                            "element_id": "readme",
                            "highlight": True,
                            "description": "Documentation",
                        },
                    ),
                ),
            ),
            FixtureDefinition(
                "classDiagram",
                (
                    FixtureCommand("add_namespace", {"id": "domain", "label": "Domain", "comment": "Domain types"}),
                    FixtureCommand(
                        "add_class",
                        {
                            "id": "Animal",
                            "label": "Animal species",
                            "attributes": [{"name": "name", "type": {"name": "String"}}],
                            "methods": [{"name": "sound", "return_type": {"name": "void"}}],
                            "annotations": ["abstract"],
                            "parent_id": "domain",
                        },
                    ),
                    FixtureCommand("add_class", {"id": "Duck", "label": "Duck", "parent_id": "domain"}),
                    FixtureCommand("add_class", {"id": "Pond", "label": "Pond", "parent_id": "domain"}),
                    FixtureCommand("add_class", {"id": "Fish", "label": "Fish", "parent_id": "domain"}),
                    FixtureCommand("add_class", {"id": "Bird", "label": "Bird", "parent_id": "domain"}),
                    FixtureCommand("add_class", {"id": "Habitat", "label": "Habitat", "parent_id": "domain"}),
                    FixtureCommand("add_class", {"id": "Food", "label": "Food", "parent_id": "domain"}),
                    FixtureCommand("add_class", {"id": "Keeper", "label": "Keeper", "parent_id": "domain"}),
                    FixtureCommand("add_class", {"id": "Zoo", "label": "Zoo", "parent_id": "domain"}),
                    FixtureCommand(
                        "add_relation",
                        {
                            "id": "inherits",
                            "source_id": "Duck",
                            "target_id": "Animal",
                            "relation_kind": "inheritance",
                            "label": "extends",
                        },
                    ),
                    FixtureCommand(
                        "add_relation",
                        {
                            "id": "fish_inherits",
                            "source_id": "Fish",
                            "target_id": "Animal",
                            "relation_kind": "inheritance",
                        },
                    ),
                    FixtureCommand(
                        "add_relation",
                        {
                            "id": "bird_inherits",
                            "source_id": "Bird",
                            "target_id": "Animal",
                            "relation_kind": "inheritance",
                        },
                    ),
                    FixtureCommand(
                        "add_relation",
                        {
                            "id": "zoo_contains_habitat",
                            "source_id": "Zoo",
                            "target_id": "Habitat",
                            "relation_kind": "composition",
                            "label": "contains",
                        },
                    ),
                    FixtureCommand(
                        "add_relation",
                        {
                            "id": "keeper_feeds",
                            "source_id": "Keeper",
                            "target_id": "Food",
                            "relation_kind": "association",
                            "label": "feeds",
                        },
                    ),
                    FixtureCommand(
                        "add_relation",
                        {
                            "id": "hosts",
                            "source_id": "Pond",
                            "target_id": "Duck",
                            "relation_kind": "aggregation",
                            "label": "hosts",
                            "source_label": "1",
                            "target_label": "*",
                        },
                    ),
                    FixtureCommand(
                        "add_relation",
                        {
                            "id": "depends",
                            "source_id": "Duck",
                            "target_id": "Pond",
                            "relation_kind": "dependency",
                            "label": "visits",
                        },
                    ),
                    FixtureCommand("add_note", {"id": "animal_note", "class_id": "Animal", "text": "Base type"}),
                    FixtureCommand("add_note", {"id": "duck_note", "class_id": "Duck", "text": "Concrete type"}),
                    FixtureCommand("add_note", {"id": "pond_note", "class_id": "Pond", "text": "Aggregate"}),
                ),
            ),
            FixtureDefinition(
                "architecture-beta",
                (
                    FixtureCommand("configure", {"nodeSeparation": 96, "seed": 7}),
                    FixtureCommand("add_group", {"id": "clients", "label": "Clients", "columns": 3}),
                    FixtureCommand("add_group", {"id": "platform", "label": "Platform", "columns": 2}),
                    FixtureCommand("add_group", {"id": "data", "label": "Data", "columns": 2}),
                    FixtureCommand("add_service", {"id": "web", "label": "Web", "group_id": "clients"}),
                    FixtureCommand("add_service", {"id": "mobile", "label": "Mobile", "group_id": "clients"}),
                    FixtureCommand("add_service", {"id": "partner", "label": "Partner", "group_id": "clients"}),
                    FixtureCommand("add_service", {"id": "api", "label": "API", "group_id": "platform"}),
                    FixtureCommand("add_service", {"id": "auth", "label": "Auth", "group_id": "platform"}),
                    FixtureCommand("add_service", {"id": "catalog", "label": "Catalog", "group_id": "platform"}),
                    FixtureCommand("add_service", {"id": "orders", "label": "Orders", "group_id": "platform"}),
                    FixtureCommand("add_service", {"id": "worker", "label": "Worker", "group_id": "platform"}),
                    FixtureCommand("add_junction", {"id": "events", "label": "Events", "group_id": "platform"}),
                    FixtureCommand("add_junction", {"id": "data_bus", "label": "Data access", "group_id": "data"}),
                    FixtureCommand("add_service", {"id": "database", "label": "Database", "group_id": "data"}),
                    FixtureCommand("add_service", {"id": "cache", "label": "Cache", "group_id": "data"}),
                    FixtureCommand("add_service", {"id": "search", "label": "Search", "group_id": "data"}),
                    FixtureCommand("add_service", {"id": "warehouse", "label": "Warehouse", "group_id": "data"}),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "web_api",
                            "source_id": "web",
                            "target_id": "api",
                            "source_port": "right",
                            "target_port": "left",
                            "label": "mTLS",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "mobile_api",
                            "source_id": "mobile",
                            "target_id": "api",
                            "source_port": "right",
                            "target_port": "left",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "partner_api",
                            "source_id": "partner",
                            "target_id": "api",
                            "source_port": "right",
                            "target_port": "left",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "api_auth",
                            "source_id": "api",
                            "target_id": "auth",
                            "source_port": "right",
                            "target_port": "left",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "api_catalog",
                            "source_id": "api",
                            "target_id": "catalog",
                            "source_port": "bottom",
                            "target_port": "top",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "catalog_orders",
                            "source_id": "catalog",
                            "target_id": "orders",
                            "source_port": "right",
                            "target_port": "left",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "orders_events",
                            "source_id": "orders",
                            "target_id": "events",
                            "source_port": "bottom",
                            "target_port": "top",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "events_worker",
                            "source_id": "events",
                            "target_id": "worker",
                            "source_port": "left",
                            "target_port": "right",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "events_data",
                            "source_id": "events",
                            "target_id": "data_bus",
                            "source_port": "right",
                            "target_port": "left",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "data_database",
                            "source_id": "data_bus",
                            "target_id": "database",
                            "source_port": "right",
                            "target_port": "left",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "data_cache",
                            "source_id": "data_bus",
                            "target_id": "cache",
                            "source_port": "bottom",
                            "target_port": "top",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "cache_search",
                            "source_id": "cache",
                            "target_id": "search",
                            "source_port": "right",
                            "target_port": "left",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "search_warehouse",
                            "source_id": "search",
                            "target_id": "warehouse",
                            "source_port": "bottom",
                            "target_port": "top",
                        },
                    ),
                    FixtureCommand("add_note", {"id": "web_note", "element_id": "web", "text": "Client gateway"}),
                    FixtureCommand("add_note", {"id": "api_note", "element_id": "api", "text": "Public API"}),
                    FixtureCommand(
                        "add_note", {"id": "database_note", "element_id": "database", "text": "Persistent storage"}
                    ),
                ),
            ),
            FixtureDefinition(
                "block",
                (
                    FixtureCommand("set_columns", {"columns": 3}),
                    FixtureCommand("add_block", {"id": "frontend", "label": "Frontend"}),
                    FixtureCommand("add_space", {"id": "gap"}),
                    FixtureCommand("add_group", {"id": "backend", "label": "Backend", "columns": 2}),
                    FixtureCommand("add_block", {"id": "api", "label": "API", "parent_id": "backend"}),
                    FixtureCommand("add_block", {"id": "database", "label": "Database", "parent_id": "backend"}),
                    FixtureCommand("add_block", {"id": "worker", "label": "Worker", "parent_id": "backend"}),
                    FixtureCommand("add_block", {"id": "cache", "label": "Cache", "parent_id": "backend"}),
                    FixtureCommand("add_block", {"id": "queue", "label": "Queue", "parent_id": "backend"}),
                    FixtureCommand("add_block", {"id": "search", "label": "Search", "parent_id": "backend"}),
                    FixtureCommand("add_block", {"id": "metrics", "label": "Metrics"}),
                    FixtureCommand("add_block", {"id": "audit", "label": "Audit"}),
                    FixtureCommand("add_block", {"id": "notifications", "label": "Notifications"}),
                ),
            ),
        )
        return tuple(definition.build(self.application, builder) for definition in definitions)
