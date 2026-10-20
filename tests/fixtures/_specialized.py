from dataclasses import dataclass

from mermaiden import Application

from .models import DiagramFixture, FixtureCommand, FixtureDefinition


@dataclass(frozen=True, slots=True)
class GitGraphFixture:
    main_branch_name: str = "main"

    def build(self, application: Application, builder: str) -> DiagramFixture:
        return FixtureDefinition(
            "gitGraph",
            (
                FixtureCommand("configure", {"mainBranchName": self.main_branch_name}),
                FixtureCommand("add_commit", {"id": "example_initial", "label": "ZERO", "tag": "v1.0.0"}),
                FixtureCommand("add_branch", {"id": "example_develop", "label": "develop", "order": 1}),
                FixtureCommand("checkout", {"id": "example_checkout", "branch": "develop"}),
                FixtureCommand(
                    "add_commit",
                    {"id": "example_feature", "label": "FEATURE", "commit_type": "HIGHLIGHT"},
                ),
                FixtureCommand("add_commit", {"id": "example_tests", "label": "TESTS"}),
                FixtureCommand("add_commit", {"id": "example_docs", "label": "DOCS"}),
                FixtureCommand("add_commit", {"id": "example_review", "label": "REVIEW"}),
                FixtureCommand("add_commit", {"id": "example_fix", "label": "FIX"}),
                FixtureCommand("add_commit", {"id": "example_refine", "label": "REFINE"}),
                FixtureCommand("add_commit", {"id": "example_verify", "label": "VERIFY"}),
                FixtureCommand("add_commit", {"id": "example_release", "label": "RELEASE", "tag": "v1.1.0"}),
                FixtureCommand("add_commit", {"id": "example_followup", "label": "FOLLOWUP"}),
            ),
        ).build(application, builder)


@dataclass(frozen=True, slots=True)
class SpecializedFixtureBuilder:
    application: Application

    def fixtures(self) -> tuple[DiagramFixture, ...]:
        builder = type(self).__name__
        definitions = (
            FixtureDefinition(
                "gantt",
                (
                    FixtureCommand("set_title", {"title": "Example release plan"}),
                    FixtureCommand("add_section", {"id": "example_delivery", "label": "Example delivery"}),
                    FixtureCommand(
                        "add_task",
                        {
                            "id": "example_design",
                            "label": "Example design",
                            "section_id": "example_delivery",
                            "status": "done",
                            "start": {"kind": "date", "date": "2026-08-01"},
                            "finish": {"kind": "duration", "amount": 2},
                        },
                    ),
                    FixtureCommand("add_section", {"id": "example_build", "label": "Build"}),
                    FixtureCommand(
                        "add_task",
                        {
                            "id": "example_implementation",
                            "label": "Implementation",
                            "section_id": "example_build",
                            "status": "active",
                            "start": {"kind": "date", "date": "2026-08-03"},
                            "finish": {"kind": "duration", "amount": 4},
                        },
                    ),
                    FixtureCommand(
                        "add_task",
                        {
                            "id": "example_review",
                            "label": "Review",
                            "section_id": "example_build",
                            "start": {"kind": "date", "date": "2026-08-07"},
                            "finish": {"kind": "duration", "amount": 2},
                        },
                    ),
                    FixtureCommand("add_section", {"id": "example_quality", "label": "Quality"}),
                    FixtureCommand(
                        "add_task",
                        {
                            "id": "example_unit_tests",
                            "label": "Unit tests",
                            "section_id": "example_quality",
                            "start": {"kind": "date", "date": "2026-08-05"},
                            "finish": {"kind": "duration", "amount": 3},
                        },
                    ),
                    FixtureCommand(
                        "add_task",
                        {
                            "id": "example_integration_tests",
                            "label": "Integration tests",
                            "section_id": "example_quality",
                            "start": {"kind": "date", "date": "2026-08-08"},
                            "finish": {"kind": "duration", "amount": 2},
                        },
                    ),
                    FixtureCommand(
                        "add_task",
                        {
                            "id": "example_visual_review",
                            "label": "Visual review",
                            "section_id": "example_quality",
                            "start": {"kind": "date", "date": "2026-08-09"},
                            "finish": {"kind": "duration", "amount": 1},
                        },
                    ),
                    FixtureCommand("add_section", {"id": "example_release", "label": "Release"}),
                    FixtureCommand(
                        "add_task",
                        {
                            "id": "example_package",
                            "label": "Package",
                            "section_id": "example_release",
                            "start": {"kind": "date", "date": "2026-08-10"},
                            "finish": {"kind": "duration", "amount": 1},
                        },
                    ),
                    FixtureCommand(
                        "add_milestone",
                        {
                            "id": "example_published",
                            "label": "Published",
                            "section_id": "example_release",
                            "start": {"kind": "date", "date": "2026-08-11"},
                            "finish": {"kind": "duration", "amount": 0},
                        },
                    ),
                ),
            ),
            FixtureDefinition(
                "C4Context",
                (
                    FixtureCommand(
                        "configure",
                        {"c4ShapeInRow": 3, "nextLinePaddingX": 12, "messageFontSize": 16},
                    ),
                    FixtureCommand(
                        "add_person",
                        {
                            "id": "example_customer",
                            "label": "Example Customer",
                            "description": "Uses example banking",
                        },
                    ),
                    FixtureCommand("add_person", {"id": "example_support", "label": "Support Agent"}),
                    FixtureCommand("add_person", {"id": "example_auditor", "label": "Auditor"}),
                    FixtureCommand(
                        "add_system",
                        {
                            "id": "example_banking",
                            "label": "Example Banking System",
                            "description": "Provides example banking",
                            "technology": "Python",
                        },
                    ),
                    FixtureCommand(
                        "add_system",
                        {"id": "example_auth", "label": "Identity System", "description": "Authenticates users"},
                    ),
                    FixtureCommand(
                        "add_system",
                        {"id": "example_reporting", "label": "Reporting System", "description": "Builds reports"},
                    ),
                    FixtureCommand(
                        "add_database",
                        {
                            "id": "example_accounts",
                            "label": "Example Accounts Database",
                            "description": "Stores example balances",
                            "technology": "PostgreSQL",
                        },
                    ),
                    FixtureCommand(
                        "add_system",
                        {"id": "example_payments", "label": "Payments System", "description": "Processes payments"},
                    ),
                    FixtureCommand(
                        "add_database",
                        {"id": "example_audit", "label": "Audit Database", "description": "Stores audit records"},
                    ),
                    FixtureCommand(
                        "add_queue",
                        {
                            "id": "example_notifications",
                            "label": "Example Notifications",
                            "description": "Publishes example events",
                            "technology": "Kafka",
                        },
                    ),
                    FixtureCommand(
                        "add_system",
                        {"id": "example_fraud", "label": "Fraud System", "description": "Scores transactions"},
                    ),
                    FixtureCommand(
                        "add_queue",
                        {"id": "example_billing", "label": "Billing Queue", "description": "Buffers billing work"},
                    ),
                    FixtureCommand(
                        "add_relationship",
                        {
                            "id": "example_uses",
                            "source_id": "example_customer",
                            "target_id": "example_banking",
                            "label": "Uses",
                            "direction": "Rel_Down",
                        },
                    ),
                    FixtureCommand(
                        "add_relationship",
                        {
                            "id": "support_uses",
                            "source_id": "example_support",
                            "target_id": "example_auth",
                            "label": "Authenticates",
                            "direction": "Rel_Down",
                        },
                    ),
                    FixtureCommand(
                        "add_relationship",
                        {
                            "id": "auditor_reads",
                            "source_id": "example_auditor",
                            "target_id": "example_reporting",
                            "label": "Reviews",
                            "direction": "Rel_Down",
                        },
                    ),
                    FixtureCommand(
                        "add_relationship",
                        {
                            "id": "banking_auth",
                            "source_id": "example_banking",
                            "target_id": "example_accounts",
                            "label": "Reads",
                            "direction": "Rel_Down",
                        },
                    ),
                    FixtureCommand(
                        "add_relationship",
                        {
                            "id": "banking_payments",
                            "source_id": "example_accounts",
                            "target_id": "example_notifications",
                            "label": "Publishes",
                            "direction": "Rel_Down",
                        },
                    ),
                    FixtureCommand(
                        "add_relationship",
                        {
                            "id": "payments_fraud",
                            "source_id": "example_auth",
                            "target_id": "example_payments",
                            "label": "Authorizes",
                            "direction": "Rel_Down",
                        },
                    ),
                    FixtureCommand(
                        "add_relationship",
                        {
                            "id": "payments_billing",
                            "source_id": "example_payments",
                            "target_id": "example_fraud",
                            "label": "Scores",
                            "direction": "Rel_Down",
                        },
                    ),
                    FixtureCommand(
                        "add_relationship",
                        {
                            "id": "reporting_accounts",
                            "source_id": "example_reporting",
                            "target_id": "example_audit",
                            "label": "Writes",
                            "direction": "Rel_Down",
                        },
                    ),
                ),
            ),
            FixtureDefinition(
                "ishikawa-beta",
                (
                    FixtureCommand("add_effect", {"id": "example_effect", "label": "Example blurry photo"}),
                    FixtureCommand("add_category", {"id": "example_process", "label": "Example process"}),
                    FixtureCommand(
                        "add_cause",
                        {
                            "id": "example_focus",
                            "label": "Example focus issue",
                            "parent_id": "example_process",
                        },
                    ),
                    FixtureCommand("add_category", {"id": "example_people", "label": "Example people"}),
                    FixtureCommand(
                        "add_cause",
                        {"id": "example_training", "label": "Example training gap", "parent_id": "example_people"},
                    ),
                    FixtureCommand(
                        "add_cause",
                        {"id": "example_fatigue", "label": "Example fatigue", "parent_id": "example_people"},
                    ),
                    FixtureCommand("add_category", {"id": "example_equipment", "label": "Example equipment"}),
                    FixtureCommand(
                        "add_cause",
                        {"id": "example_lens", "label": "Example dirty lens", "parent_id": "example_equipment"},
                    ),
                    FixtureCommand(
                        "add_cause",
                        {"id": "example_tripod", "label": "Example unstable tripod", "parent_id": "example_equipment"},
                    ),
                    FixtureCommand("add_category", {"id": "example_environment", "label": "Example environment"}),
                    FixtureCommand(
                        "add_cause",
                        {"id": "example_light", "label": "Example low light", "parent_id": "example_environment"},
                    ),
                    FixtureCommand(
                        "add_cause", {"id": "example_wind", "label": "Example wind", "parent_id": "example_environment"}
                    ),
                    FixtureCommand(
                        "add_cause",
                        {
                            "id": "example_shutter",
                            "label": "Example shutter issue",
                            "parent_id": "example_process",
                        },
                    ),
                ),
            ),
            FixtureDefinition(
                "cynefin-beta",
                (
                    FixtureCommand(
                        "add_item",
                        {"id": "example_investigate", "label": "Example investigation", "domain": "complex"},
                    ),
                    FixtureCommand(
                        "add_item",
                        {"id": "example_analyze", "label": "Example analysis", "domain": "complicated"},
                    ),
                    FixtureCommand(
                        "add_item",
                        {"id": "example_restart", "label": "Example restart", "domain": "clear"},
                    ),
                    FixtureCommand(
                        "add_transition",
                        {
                            "id": "example_pattern",
                            "source_id": "example_investigate",
                            "target_id": "example_analyze",
                            "label": "Example pattern",
                        },
                    ),
                    FixtureCommand("add_item", {"id": "example_probe", "label": "Example probe", "domain": "complex"}),
                    FixtureCommand(
                        "add_item", {"id": "example_model", "label": "Example model", "domain": "complicated"}
                    ),
                    FixtureCommand(
                        "add_item", {"id": "example_standard", "label": "Example standard", "domain": "clear"}
                    ),
                    FixtureCommand(
                        "add_item", {"id": "example_stabilize", "label": "Example stabilize", "domain": "chaotic"}
                    ),
                    FixtureCommand(
                        "add_item", {"id": "example_triage", "label": "Example triage", "domain": "confusion"}
                    ),
                    FixtureCommand(
                        "add_item", {"id": "example_experiment", "label": "Example experiment", "domain": "complex"}
                    ),
                    FixtureCommand(
                        "add_item", {"id": "example_expert", "label": "Example expert review", "domain": "complicated"}
                    ),
                    FixtureCommand(
                        "add_item", {"id": "example_runbook", "label": "Example runbook", "domain": "clear"}
                    ),
                ),
            ),
            FixtureDefinition(
                "kanban",
                (
                    FixtureCommand("add_column", {"id": "example_todo", "label": "Example todo"}),
                    FixtureCommand("add_column", {"id": "example_doing", "label": "Example in progress"}),
                    FixtureCommand(
                        "add_task",
                        {
                            "id": "example_docs",
                            "label": "Example documentation",
                            "column_id": "example_todo",
                            "ticket": "EXAMPLE-1",
                            "priority": "High",
                        },
                    ),
                    FixtureCommand("add_column", {"id": "example_review", "label": "Example review"}),
                    FixtureCommand("add_column", {"id": "example_done", "label": "Example done"}),
                    FixtureCommand(
                        "add_task", {"id": "example_design", "label": "Example design", "column_id": "example_todo"}
                    ),
                    FixtureCommand(
                        "add_task", {"id": "example_code", "label": "Example code", "column_id": "example_doing"}
                    ),
                    FixtureCommand(
                        "add_task", {"id": "example_tests", "label": "Example tests", "column_id": "example_doing"}
                    ),
                    FixtureCommand(
                        "add_task", {"id": "example_audit", "label": "Example audit", "column_id": "example_review"}
                    ),
                    FixtureCommand(
                        "add_task", {"id": "example_fix", "label": "Example fix", "column_id": "example_review"}
                    ),
                    FixtureCommand(
                        "add_task", {"id": "example_release", "label": "Example release", "column_id": "example_done"}
                    ),
                    FixtureCommand(
                        "add_task", {"id": "example_archive", "label": "Example archive", "column_id": "example_done"}
                    ),
                ),
            ),
            FixtureDefinition(
                "railroad-ebnf-beta",
                (
                    FixtureCommand("add_rule", {"id": "example_rule", "label": "example"}),
                    FixtureCommand("add_alternative", {"id": "example_choices", "parent_id": "example_rule"}),
                    FixtureCommand(
                        "add_special",
                        {"id": "example_first", "label": "first", "parent_id": "example_choices"},
                    ),
                    FixtureCommand(
                        "add_special",
                        {"id": "example_second", "label": "second", "parent_id": "example_choices"},
                    ),
                    FixtureCommand("add_optional", {"id": "example_optional", "parent_id": "example_choices"}),
                    FixtureCommand(
                        "add_terminal",
                        {"id": "example_optional_value", "label": "optional", "rule_id": "example_optional"},
                    ),
                    FixtureCommand("add_repetition", {"id": "example_repetition", "parent_id": "example_choices"}),
                    FixtureCommand(
                        "add_non_terminal", {"id": "example_repeated", "label": "item", "rule_id": "example_repetition"}
                    ),
                    FixtureCommand("add_group", {"id": "example_group", "parent_id": "example_choices"}),
                    FixtureCommand(
                        "add_terminal", {"id": "example_grouped", "label": "grouped", "rule_id": "example_group"}
                    ),
                    FixtureCommand("add_rule", {"id": "value_rule", "label": "value"}),
                    FixtureCommand("add_terminal", {"id": "value_number", "label": "number", "rule_id": "value_rule"}),
                    FixtureCommand("add_terminal", {"id": "value_string", "label": "string", "rule_id": "value_rule"}),
                ),
            ),
            FixtureDefinition(
                "wardley-beta",
                (
                    FixtureCommand(
                        "add_anchor",
                        {
                            "id": "example_business",
                            "label": "Example Business",
                            "visibility": 0.95,
                            "evolution": 0.63,
                        },
                    ),
                    FixtureCommand(
                        "add_component",
                        {
                            "id": "example_product",
                            "label": "Example Product",
                            "visibility": 0.79,
                            "evolution": 0.61,
                            "decorators": ["build"],
                        },
                    ),
                    FixtureCommand(
                        "add_component",
                        {
                            "id": "example_service",
                            "label": "Example Service",
                            "visibility": 0.52,
                            "evolution": 0.8,
                        },
                    ),
                    FixtureCommand(
                        "add_dependency",
                        {
                            "id": "example_business_product",
                            "source_id": "example_business",
                            "target_id": "example_product",
                        },
                    ),
                    FixtureCommand(
                        "add_component",
                        {
                            "id": "example_identity",
                            "label": "Example Identity",
                            "visibility": 0.72,
                            "evolution": 0.82,
                            "decorators": ["buy"],
                        },
                    ),
                    FixtureCommand(
                        "add_component",
                        {"id": "example_data", "label": "Example Data", "visibility": 0.46, "evolution": 0.58},
                    ),
                    FixtureCommand(
                        "add_component",
                        {
                            "id": "example_compute",
                            "label": "Example Compute",
                            "visibility": 0.35,
                            "evolution": 0.91,
                            "decorators": ["outsource"],
                        },
                    ),
                    FixtureCommand(
                        "add_component",
                        {"id": "example_network", "label": "Example Network", "visibility": 0.25, "evolution": 0.97},
                    ),
                    FixtureCommand(
                        "add_component",
                        {
                            "id": "example_observability",
                            "label": "Example Observability",
                            "visibility": 0.58,
                            "evolution": 0.76,
                        },
                    ),
                    FixtureCommand(
                        "add_dependency",
                        {
                            "id": "example_product_identity",
                            "source_id": "example_product",
                            "target_id": "example_identity",
                            "label": "authenticates",
                        },
                    ),
                    FixtureCommand(
                        "add_dependency",
                        {
                            "id": "example_product_data",
                            "source_id": "example_product",
                            "target_id": "example_data",
                            "label": "stores",
                        },
                    ),
                    FixtureCommand(
                        "add_dependency",
                        {
                            "id": "example_service_compute",
                            "source_id": "example_service",
                            "target_id": "example_compute",
                            "label": "runs on",
                        },
                    ),
                    FixtureCommand(
                        "add_dependency",
                        {
                            "id": "example_compute_network",
                            "source_id": "example_compute",
                            "target_id": "example_network",
                            "label": "connects",
                        },
                    ),
                    FixtureCommand(
                        "add_dependency",
                        {
                            "id": "example_service_observability",
                            "source_id": "example_service",
                            "target_id": "example_observability",
                            "label": "emits",
                        },
                    ),
                ),
            ),
        )
        return (
            definitions[0].build(self.application, builder),
            GitGraphFixture().build(self.application, builder),
            *(definition.build(self.application, builder) for definition in definitions[1:]),
        )
