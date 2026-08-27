from ...diagrams.application import DiagramsApplication
from ...diagrams.domain import DiagramModel
from ...diagrams.er.diagram import EntityRelationshipDiagram
from ...diagrams.mindmap.diagram import Mindmap
from ...diagrams.packet.diagram import Packet
from ...diagrams.pie.diagram import PieDiagram
from ...diagrams.radar.diagram import Radar
from ...diagrams.requirement.diagram import RequirementDiagram
from ...diagrams.requirement.elements import RequirementType, Risk, VerificationMethod
from ...diagrams.requirement.relations import RequirementRelationKind
from ...diagrams.sankey.diagram import Sankey
from ...diagrams.venn.diagram import Venn


def build_analytical_fixtures(registry: DiagramsApplication) -> dict[str, DiagramModel]:
    requirements = registry.get_diagram("requirementDiagram")
    assert isinstance(requirements, RequirementDiagram)
    requirements.add_requirement(
        "system",
        "REQ-001",
        "The system provides secure access.",
        RequirementType.REQUIREMENT,
        Risk.HIGH,
        VerificationMethod.TEST,
    )
    requirements.add_requirement(
        "login",
        "REQ-002",
        "Users can sign in.",
        RequirementType.FUNCTIONAL,
        Risk.MEDIUM,
        VerificationMethod.DEMONSTRATION,
    )
    requirements.add_requirement(
        "api",
        "REQ-003",
        "The API is documented.",
        RequirementType.INTERFACE,
        Risk.LOW,
        VerificationMethod.INSPECTION,
    )
    requirements.add_requirement(
        "latency",
        "REQ-004",
        "Responses complete within 100ms.",
        RequirementType.PERFORMANCE,
        Risk.HIGH,
        VerificationMethod.ANALYSIS,
    )
    requirements.add_requirement(
        "device",
        "REQ-005",
        "The device withstands heat.",
        RequirementType.PHYSICAL,
        Risk.MEDIUM,
        VerificationMethod.TEST,
    )
    requirements.add_requirement(
        "policy",
        "REQ-006",
        "Access follows policy.",
        RequirementType.DESIGN_CONSTRAINT,
        Risk.LOW,
        VerificationMethod.INSPECTION,
    )
    requirements.add_element("service", "software", "docs/service.md")
    requirements.add_element("test_suite", "test", "tests/requirements.py")
    requirements.add_relation("system_contains_login", "system", "login", RequirementRelationKind.CONTAINS)
    requirements.add_relation("login_copies_api", "login", "api", RequirementRelationKind.COPIES)
    requirements.add_relation("api_derives_latency", "api", "latency", RequirementRelationKind.DERIVES)
    requirements.add_relation("service_satisfies_system", "service", "system", RequirementRelationKind.SATISFIES)
    requirements.add_relation("test_verifies_login", "test_suite", "login", RequirementRelationKind.VERIFIES)
    requirements.add_relation("policy_refines_system", "policy", "system", RequirementRelationKind.REFINES)
    requirements.add_relation("device_traces_policy", "device", "policy", RequirementRelationKind.TRACES)

    mindmap = registry.get_diagram("mindmap")
    assert isinstance(mindmap, Mindmap)
    mindmap.add_root("root", "Mermaiden")
    mindmap.add_node("domain", "Domain model", "root")
    mindmap.add_square("contracts", "Contracts", "domain")
    mindmap.add_rounded_square("services", "Services", "domain")
    mindmap.add_circle("runtime", "Runtime", "root")
    mindmap.add_bang("warning", "Important", "runtime")
    mindmap.add_cloud("cloud", "Cloud", "runtime")
    mindmap.add_hexagon("quality", "Quality", "root")

    pie = registry.get_diagram("pie")
    assert isinstance(pie, PieDiagram)
    pie.set_title("Adopted pets")
    pie.show_values()
    pie.add_slice("dogs", "Dogs", 386)
    pie.add_slice("cats", "Cats", 85)
    pie.add_slice("rats", "Rats", 15)

    sankey = registry.get_diagram("sankey")
    assert isinstance(sankey, Sankey)
    sankey.add_node("grid", "Electricity grid")
    sankey.add_node("industry", "Industry")
    sankey.add_node("homes", "Homes")
    sankey.add_flow("grid_industry", "grid", "industry", 342.165)
    sankey.add_flow("grid_homes", "grid", "homes", 113.726)

    venn = registry.get_diagram("venn-beta")
    assert isinstance(venn, Venn)
    venn.add_set("frontend", "Frontend", 20)
    venn.add_text("react", "React", "frontend")
    venn.add_set("backend", "Backend", 12)
    venn.add_text("api", "API", "backend")
    venn.add_union("shared", "Shared", ("frontend", "backend"), 3)
    venn.add_text("openapi", "OpenAPI", "shared")

    radar = registry.get_diagram("radar-beta")
    assert isinstance(radar, Radar)
    radar.set_title("Restaurant comparison")
    radar.add_axis("food", "Food quality")
    radar.add_axis("service", "Service")
    radar.add_axis("price", "Price")
    radar.add_curve("restaurant_a", "Restaurant A", (4, 3, 2))
    radar.add_curve("restaurant_b", "Restaurant B", (3, 4, 3))
    radar.set_range(0, 5)
    radar.set_graticule("polygon")
    radar.set_ticks(5)

    packet = registry.get_diagram("packet")
    assert isinstance(packet, Packet)
    packet.set_title("UDP packet")
    packet.add_bits("source", "Source port", 16)
    packet.add_bits("destination", "Destination port", 16)
    packet.add_field("length", "Length", 32, 47)
    packet.add_field("checksum", "Checksum", 48, 63)

    er = registry.get_diagram("erDiagram")
    assert isinstance(er, EntityRelationshipDiagram)
    er.add_entity("CUSTOMER", "Customer")
    er.add_attribute("customer_id", "id", "int", "CUSTOMER", ("PK",))
    er.add_entity("ORDER", "Order")
    er.add_attribute("order_id", "id", "int", "ORDER", ("PK",))
    er.add_relationship("places", "CUSTOMER", "ORDER", "places", "||--o{")

    return {
        "requirement": requirements,
        "mindmap": mindmap,
        "pie": pie,
        "sankey": sankey,
        "venn": venn,
        "radar": radar,
        "packet": packet,
        "er": er,
    }
