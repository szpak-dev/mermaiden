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
                    FixtureCommand(
                        "configure",
                        {
                            "showIcons": True,
                            "filenameIcons": {"README.md": "file"},
                            "extensionIcons": {"py": "file"},
                        },
                    ),
                    FixtureCommand("add_directory", {"id": "root", "label": "root"}),
                    FixtureCommand("add_directory", {"id": "source", "label": "src"}),
                    FixtureCommand("add_directory", {"id": "package", "label": "mermaiden"}),
                    FixtureCommand("add_directory", {"id": "diagrams", "label": "diagrams"}),
                    FixtureCommand("add_directory", {"id": "runtime", "label": "runtime"}),
                    FixtureCommand("add_directory", {"id": "tests", "label": "tests"}),
                    FixtureCommand("add_directory", {"id": "unit", "label": "unit"}),
                    FixtureCommand("add_directory", {"id": "integration", "label": "integration"}),
                    FixtureCommand("add_file", {"id": "readme", "label": "README.md"}),
                    FixtureCommand("add_file", {"id": "pyproject", "label": "pyproject.toml"}),
                    FixtureCommand("add_file", {"id": "application", "label": "application.py"}),
                    FixtureCommand("add_file", {"id": "configuration", "label": "configuration.py"}),
                    FixtureCommand("add_file", {"id": "snapshot", "label": "snapshot.py"}),
                    FixtureCommand("add_file", {"id": "behavior", "label": "test_behavior.py"}),
                    FixtureCommand("add_file", {"id": "render", "label": "test_rendering.py"}),
                    FixtureCommand("add_item", {"id": "evidence", "label": "Release evidence"}),
                    FixtureCommand(
                        "add_annotation",
                        {
                            "id": "root_note",
                            "element_id": "root",
                            "highlight": True,
                            "icon": "folder",
                            "description": "Typed diagram toolkit",
                        },
                    ),
                    FixtureCommand("add_annotation", {"id": "source_note", "element_id": "source", "icon": "folder"}),
                    FixtureCommand("add_branch", {"id": "root_source", "parent_id": "root", "child_id": "source"}),
                    FixtureCommand("add_annotation", {"id": "tests_note", "element_id": "tests", "icon": "folder"}),
                    FixtureCommand("add_branch", {"id": "root_tests", "parent_id": "root", "child_id": "tests"}),
                    FixtureCommand(
                        "add_branch", {"id": "source_package", "parent_id": "source", "child_id": "package"}
                    ),
                    FixtureCommand(
                        "add_branch", {"id": "package_diagrams", "parent_id": "package", "child_id": "diagrams"}
                    ),
                    FixtureCommand(
                        "add_branch", {"id": "package_runtime", "parent_id": "package", "child_id": "runtime"}
                    ),
                    FixtureCommand(
                        "add_branch", {"id": "package_application", "parent_id": "package", "child_id": "application"}
                    ),
                    FixtureCommand(
                        "add_branch",
                        {"id": "diagrams_configuration", "parent_id": "diagrams", "child_id": "configuration"},
                    ),
                    FixtureCommand(
                        "add_branch", {"id": "runtime_snapshot", "parent_id": "runtime", "child_id": "snapshot"}
                    ),
                    FixtureCommand("add_branch", {"id": "tests_unit", "parent_id": "tests", "child_id": "unit"}),
                    FixtureCommand(
                        "add_branch", {"id": "tests_integration", "parent_id": "tests", "child_id": "integration"}
                    ),
                    FixtureCommand("add_branch", {"id": "unit_behavior", "parent_id": "unit", "child_id": "behavior"}),
                    FixtureCommand(
                        "add_branch", {"id": "integration_render", "parent_id": "integration", "child_id": "render"}
                    ),
                    FixtureCommand("add_branch", {"id": "root_readme", "parent_id": "root", "child_id": "readme"}),
                    FixtureCommand(
                        "add_branch", {"id": "root_pyproject", "parent_id": "root", "child_id": "pyproject"}
                    ),
                    FixtureCommand("add_branch", {"id": "root_evidence", "parent_id": "root", "child_id": "evidence"}),
                    FixtureCommand(
                        "add_annotation",
                        {
                            "id": "readme_note",
                            "element_id": "readme",
                            "highlight": True,
                            "description": "Documentation",
                        },
                    ),
                    FixtureCommand(
                        "add_annotation",
                        {
                            "id": "configuration_note",
                            "element_id": "configuration",
                            "highlight": True,
                            "icon": "file",
                            "description": "Typed configuration",
                        },
                    ),
                    FixtureCommand(
                        "add_annotation",
                        {
                            "id": "render_note",
                            "element_id": "render",
                            "highlight": True,
                            "icon": "file",
                            "description": "Browser rendering",
                        },
                    ),
                    FixtureCommand(
                        "add_annotation",
                        {
                            "id": "evidence_note",
                            "element_id": "evidence",
                            "highlight": True,
                            "description": "Release evidence",
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
                    FixtureCommand("add_group", {"id": "platform", "label": "Platform", "columns": 3}),
                    FixtureCommand("add_group", {"id": "data", "label": "Data", "columns": 3}),
                    FixtureCommand("add_service", {"id": "web", "label": "Web", "group_id": "clients"}),
                    FixtureCommand("add_service", {"id": "mobile", "label": "Mobile", "group_id": "clients"}),
                    FixtureCommand("add_service", {"id": "partner", "label": "Partner", "group_id": "clients"}),
                    FixtureCommand("add_service", {"id": "api", "label": "API", "group_id": "platform"}),
                    FixtureCommand("add_service", {"id": "auth", "label": "Auth", "group_id": "platform"}),
                    FixtureCommand("add_service", {"id": "catalog", "label": "Catalog", "group_id": "platform"}),
                    FixtureCommand("add_service", {"id": "orders", "label": "Orders", "group_id": "platform"}),
                    FixtureCommand("add_service", {"id": "worker", "label": "Worker", "group_id": "platform"}),
                    FixtureCommand("add_service", {"id": "events", "label": "Events", "group_id": "platform"}),
                    FixtureCommand("add_service", {"id": "data_bus", "label": "Data API", "group_id": "data"}),
                    FixtureCommand("add_service", {"id": "database", "label": "Database", "group_id": "data"}),
                    FixtureCommand("add_service", {"id": "cache", "label": "Cache", "group_id": "data"}),
                    FixtureCommand("add_service", {"id": "search", "label": "Search", "group_id": "data"}),
                    FixtureCommand("add_service", {"id": "warehouse", "label": "Warehouse", "group_id": "data"}),
                    FixtureCommand("add_service", {"id": "gateway", "label": "Gateway"}),
                    FixtureCommand(
                        "add_alignment",
                        {"id": "client_gateway_column", "axis": "column", "member_ids": ["gateway", "web"]},
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "web_gateway",
                            "source_id": "web",
                            "target_id": "gateway",
                            "source_port": "top",
                            "target_port": "bottom",
                            "label": "mTLS",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "api_orders",
                            "source_id": "api",
                            "target_id": "orders",
                            "source_port": "bottom",
                            "target_port": "top",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "auth_worker",
                            "source_id": "auth",
                            "target_id": "worker",
                            "source_port": "bottom",
                            "target_port": "top",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "catalog_events",
                            "source_id": "catalog",
                            "target_id": "events",
                            "source_port": "bottom",
                            "target_port": "top",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "data_search",
                            "source_id": "data_bus",
                            "target_id": "search",
                            "source_port": "bottom",
                            "target_port": "top",
                        },
                    ),
                    FixtureCommand(
                        "add_edge",
                        {
                            "id": "database_warehouse",
                            "source_id": "database",
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
