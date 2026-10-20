from dataclasses import dataclass, field

from mermaiden import Application


@dataclass(frozen=True, slots=True)
class C4HumanLayout:
    diagram_margin_x: int = 40
    diagram_margin_y: int = 40
    c4_shape_margin: int = 25
    c4_shape_padding: int = 14
    width: int = 190
    height: int = 72
    box_margin: int = 16
    next_line_padding_x: int = 0
    person_font_size: int = 12
    system_font_size: int = 12
    system_db_font_size: int = 12
    system_queue_font_size: int = 12
    boundary_font_size: int = 14
    message_font_size: int = 11
    container_font_size: int = 12
    container_db_font_size: int = 12
    container_queue_font_size: int = 12
    component_font_size: int = 12
    component_db_font_size: int = 12
    component_queue_font_size: int = 12
    wrap_padding: int = 8

    def values(self, shape_in_row: int, boundary_in_row: int) -> dict[str, object]:
        return {
            "diagramMarginX": self.diagram_margin_x,
            "diagramMarginY": self.diagram_margin_y,
            "c4ShapeMargin": self.c4_shape_margin,
            "c4ShapePadding": self.c4_shape_padding,
            "width": self.width,
            "height": self.height,
            "boxMargin": self.box_margin,
            "c4ShapeInRow": shape_in_row,
            "nextLinePaddingX": self.next_line_padding_x,
            "c4BoundaryInRow": boundary_in_row,
            "personFontSize": self.person_font_size,
            "systemFontSize": self.system_font_size,
            "system_dbFontSize": self.system_db_font_size,
            "system_queueFontSize": self.system_queue_font_size,
            "boundaryFontSize": self.boundary_font_size,
            "messageFontSize": self.message_font_size,
            "containerFontSize": self.container_font_size,
            "container_dbFontSize": self.container_db_font_size,
            "container_queueFontSize": self.container_queue_font_size,
            "componentFontSize": self.component_font_size,
            "component_dbFontSize": self.component_db_font_size,
            "component_queueFontSize": self.component_queue_font_size,
            "wrapPadding": self.wrap_padding,
        }


@dataclass(frozen=True, slots=True)
class C4HumanProof:
    id: str
    body: tuple[str, ...]
    shape_in_row: int = 3
    boundary_in_row: int = 2

    def source(self, application: Application, layout: C4HumanLayout) -> str:
        diagram = application.create_diagram("C4Context")
        application.execute(
            diagram,
            "configure",
            layout.values(self.shape_in_row, self.boundary_in_row),
        )
        application.execute(
            diagram,
            "add_person",
            {"id": "frontmatter_witness", "label": "Frontmatter witness"},
        )
        rendered = application.render(diagram)
        frontmatter = rendered.split("C4Context\n", 1)[0]
        layout_directive = (
            f'UpdateLayoutConfig($c4ShapeInRow="{self.shape_in_row}", $c4BoundaryInRow="{self.boundary_in_row}")'
        )
        content = "\n".join((self.body[0], layout_directive, *self.body[1:]))
        return f"{frontmatter}{content}\n"


@dataclass(frozen=True, slots=True)
class C4HumanProofCatalog:
    layout: C4HumanLayout = field(default_factory=C4HumanLayout)

    def proofs(self) -> tuple[C4HumanProof, ...]:
        return (
            C4HumanProof(
                "C4Context-human",
                (
                    "C4Context",
                    'Person(customer, "Customer", "Uses everyday banking")',
                    'Person(advisor, "Advisor", "Supports customers")',
                    'Person(auditor, "Auditor", "Reviews controls")',
                    'Person(operator, "Operator", "Runs the platform")',
                    'System(portal, "Customer Portal", "Browser and mobile entry point")',
                    'System(advisor_console, "Advisor Console", "Customer support workspace")',
                    'System(risk, "Risk Engine", "Evaluates transactions")',
                    'System(operations, "Operations Console", "Platform supervision")',
                    'System(identity, "Identity Service", "Authenticates every actor")',
                    'System(payments, "Payments Service", "Moves and settles money")',
                    'System(reporting, "Reporting Service", "Builds regulatory reports")',
                    'System(observability, "Observability", "Collects platform signals")',
                    'SystemDb(accounts, "Accounts Database", "Balances and ledgers", "PostgreSQL")',
                    'SystemDb(warehouse, "Analytics Warehouse", "Historical reporting data", "ClickHouse")',
                    'SystemQueue(events, "Domain Events", "Reliable business events", "Kafka")',
                    'SystemQueue(alerts, "Alert Stream", "Operational notifications", "Kafka")',
                    'Rel_Down(customer, operator, "Requests help")',
                    'Rel_Down(advisor, portal, "Uses")',
                    'Rel_Down(auditor, advisor_console, "Reviews")',
                    'Rel_Down(operator, risk, "Escalates")',
                    'Rel_Down(portal, operations, "Calls")',
                    'Rel_Down(advisor_console, identity, "Authenticates")',
                    'Rel_Down(risk, payments, "Approves")',
                    'Rel_Down(operations, reporting, "Reports")',
                    'Rel_Down(identity, observability, "Audits")',
                    'Rel_Down(payments, accounts, "Stores")',
                    'Rel_Down(reporting, warehouse, "Writes")',
                    'Rel_Down(observability, events, "Publishes")',
                    'Rel_Down(accounts, alerts, "Raises alert")',
                ),
            ),
            C4HumanProof(
                "C4Container-human",
                (
                    "C4Container",
                    'Person(customer, "Customer", "Uses digital banking")',
                    'Person(operator, "Operator", "Runs the platform")',
                    'System_Ext(card_network, "Card Network", "External settlement")',
                    'System_Ext(regulator, "Regulator", "Receives reports")',
                    'System_Boundary(banking, "Digital Banking Platform") {',
                    'Container(web, "Web Application", "TypeScript", "Customer experience")',
                    'Container(mobile, "Mobile Application", "Kotlin and Swift", "Mobile experience")',
                    'Container(edge, "API Gateway", "Envoy", "Routes trusted requests")',
                    'Container(identity, "Identity API", "Python", "Authentication and sessions")',
                    'Container(accounts, "Accounts API", "Python", "Balances and ledgers")',
                    'Container(payments, "Payments API", "Python", "Payment orchestration")',
                    'Container(risk, "Risk Worker", "Python", "Transaction decisions")',
                    'Container(reporting, "Reporting Worker", "Python", "Regulatory reports")',
                    'ContainerDb(primary_db, "Primary Database", "PostgreSQL", "Transactional state")',
                    'ContainerDb(warehouse, "Analytics Warehouse", "ClickHouse", "Historical facts")',
                    'ContainerQueue(commands, "Command Queue", "Kafka", "Asynchronous work")',
                    'ContainerQueue(events, "Event Stream", "Kafka", "Business events")',
                    "}",
                    'Rel_Down(customer, web, "Uses")',
                    'Rel_Down(operator, mobile, "Supports")',
                    'Rel_Down(web, edge, "Calls")',
                    'Rel_Down(mobile, identity, "Authenticates")',
                    'Rel_Down(edge, accounts, "Routes")',
                    'Rel_Down(identity, payments, "Authorizes")',
                    'Rel_Down(accounts, risk, "Checks")',
                    'Rel_Down(payments, reporting, "Records")',
                    'Rel_Down(risk, primary_db, "Stores decisions")',
                    'Rel_Down(reporting, warehouse, "Writes reports")',
                    'Rel_Down(primary_db, commands, "Emits work")',
                    'Rel_Down(warehouse, events, "Publishes facts")',
                ),
            ),
            C4HumanProof(
                "C4Component-human",
                (
                    "C4Component",
                    'Person(customer, "Customer", "Initiates payments")',
                    'System_Ext(card_network, "Card Network", "External settlement")',
                    'System_Boundary(banking, "Digital Banking Platform") {',
                    'Container_Boundary(payments_api, "Payments API") {',
                    'Component(http, "HTTP Controller", "FastAPI", "Receives payment requests")',
                    'Component(authorizer, "Authorization Policy", "Python", "Checks permissions")',
                    'Component(orchestrator, "Payment Orchestrator", "Python", "Coordinates payment flow")',
                    'Component(risk_client, "Risk Client", "HTTP", "Requests risk decisions")',
                    'Component(ledger, "Ledger Service", "Python", "Records accounting entries")',
                    'Component(settlement, "Settlement Adapter", "ISO 8583", "Talks to card networks")',
                    'Component(outbox, "Outbox Publisher", "Python", "Publishes committed events")',
                    'Component(notifications, "Notification Adapter", "HTTP", "Sends customer updates")',
                    'ComponentDb(payment_store, "Payment Store", "PostgreSQL", "Payment state")',
                    'ComponentDb(ledger_store, "Ledger Store", "PostgreSQL", "Double-entry ledger")',
                    'ComponentQueue(command_bus, "Command Bus", "Kafka", "Payment commands")',
                    'ComponentQueue(event_bus, "Event Bus", "Kafka", "Payment events")',
                    "}",
                    "}",
                    'Rel_Down(customer, http, "Pays")',
                    'Rel_Down(http, orchestrator, "Dispatches")',
                    'Rel_Down(authorizer, risk_client, "Checks")',
                    'Rel_Down(orchestrator, ledger, "Posts")',
                    'Rel_Down(risk_client, settlement, "Approves")',
                    'Rel_Down(ledger, outbox, "Commits")',
                    'Rel_Down(settlement, notifications, "Notifies")',
                    'Rel_Down(outbox, payment_store, "Stores")',
                    'Rel_Down(notifications, ledger_store, "Balances")',
                    'Rel_Down(payment_store, command_bus, "Enqueues")',
                    'Rel_Down(ledger_store, event_bus, "Publishes")',
                ),
            ),
            C4HumanProof(
                "C4Dynamic-human",
                (
                    "C4Dynamic",
                    'Person(customer, "Customer", "Confirms a payment")',
                    'System(channel, "Banking Channel", "Web or mobile")',
                    'System(identity, "Identity Service", "Authenticates sessions")',
                    'System(payments, "Payments Service", "Coordinates payments")',
                    'System(risk, "Risk Service", "Evaluates fraud risk")',
                    'System(ledger, "Ledger Service", "Posts accounting entries")',
                    'System(settlement, "Settlement Service", "Moves funds")',
                    'System_Ext(card_network, "Card Network", "External authorization")',
                    'SystemDb(payment_db, "Payment Database", "Payment state", "PostgreSQL")',
                    'SystemDb(ledger_db, "Ledger Database", "Accounting entries", "PostgreSQL")',
                    'SystemQueue(commands, "Command Queue", "Asynchronous commands", "Kafka")',
                    'SystemQueue(events, "Event Stream", "Committed business events", "Kafka")',
                    'System(notifications, "Notification Service", "Informs the customer")',
                    'RelIndex(1, customer, channel, "Submits payment")',
                    'RelIndex(2, channel, identity, "Validates session")',
                    'RelIndex(3, identity, payments, "Forwards request")',
                    'RelIndex(4, payments, risk, "Requests decision")',
                    'RelIndex(5, risk, ledger, "Approves payment")',
                    'RelIndex(6, ledger, settlement, "Requests settlement")',
                    'RelIndex(7, settlement, card_network, "Authorizes funds")',
                    'RelIndex(8, card_network, payment_db, "Returns result")',
                    'RelIndex(9, payment_db, ledger_db, "Posts ledger")',
                    'RelIndex(10, ledger_db, commands, "Enqueues notification")',
                    'RelIndex(11, commands, events, "Publishes event")',
                    'RelIndex(12, events, notifications, "Delivers update")',
                ),
                shape_in_row=1,
            ),
            C4HumanProof(
                "C4Deployment-human",
                (
                    "C4Deployment",
                    'Person(customer, "Customer", "Uses digital banking")',
                    'Deployment_Node(device, "Customer Device", "iOS, Android, Browser") {',
                    'Container(channel, "Banking Client", "TypeScript or Native", "Customer interface")',
                    "}",
                    'Deployment_Node(edge_zone, "Edge Zone", "Kubernetes") {',
                    'Container(waf, "Web Application Firewall", "Cloud WAF", "Filters hostile traffic")',
                    'Container(edge, "API Gateway", "Envoy", "Routes trusted traffic")',
                    "}",
                    'Deployment_Node(application_zone, "Application Zone", "Kubernetes") {',
                    'Container(identity, "Identity Service", "Python", "Authenticates sessions")',
                    'Container(accounts, "Accounts Service", "Python", "Serves balances")',
                    'Container(payments, "Payments Service", "Python", "Coordinates payments")',
                    'Container(risk, "Risk Service", "Python", "Evaluates fraud risk")',
                    'Container(reporting, "Reporting Service", "Python", "Builds reports")',
                    'Container(notifications, "Notification Service", "Python", "Sends updates")',
                    "}",
                    'Deployment_Node(data_zone, "Data Zone", "Managed Services") {',
                    'ContainerDb(primary_db, "Primary Database", "PostgreSQL", "Transactional state")',
                    'ContainerDb(warehouse, "Analytics Warehouse", "ClickHouse", "Historical facts")',
                    'ContainerQueue(commands, "Command Queue", "Kafka", "Asynchronous commands")',
                    'ContainerQueue(events, "Event Stream", "Kafka", "Business events")',
                    "}",
                    'Rel_Down(customer, channel, "Uses")',
                    'Rel_Down(channel, waf, "Connects")',
                    'Rel_Down(waf, edge, "Forwards")',
                    'Rel_Down(edge, identity, "Authenticates")',
                    'Rel_Down(identity, accounts, "Authorizes")',
                    'Rel_Down(accounts, payments, "Initiates")',
                    'Rel_Down(payments, risk, "Assesses")',
                    'Rel_Down(risk, reporting, "Reports")',
                    'Rel_Down(reporting, notifications, "Notifies")',
                    'Rel_Down(primary_db, warehouse, "Replicates")',
                    'Rel_Down(warehouse, commands, "Schedules")',
                    'Rel_Down(commands, events, "Publishes")',
                ),
            ),
        )

    def sources(self, application: Application) -> dict[str, str]:
        return {proof.id: proof.source(application, self.layout) for proof in self.proofs()}
