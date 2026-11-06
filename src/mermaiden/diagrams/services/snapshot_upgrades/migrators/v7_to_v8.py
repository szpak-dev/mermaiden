from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
from wireup import injectable

from .....runtime.snapshot.value_validator import SnapshotMapping
from ..domain import SnapshotMigrationState, SnapshotMigrator, SnapshotUpgradeError


class LegacyLineHops(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    discriminator: Literal["mermaiden/enum/swimlane-beta/line_hops"] = Field(alias="$enum")
    value: Literal["arc", "gap"]


@injectable(as_type=SnapshotMigrator, qualifier="v7_to_v8", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class SnapshotV7ToV8Migrator(SnapshotMigrator):
    def source_version(self) -> int:
        return 7

    def target_version(self) -> int:
        return 8

    def migrate(self, state: SnapshotMigrationState) -> SnapshotMigrationState:
        snapshot = state.current
        fields = dict(SnapshotMapping.model_validate(snapshot.configuration["fields"]).root)
        differences = sorted(fields.keys() ^ set(self.source_fields(snapshot.kind)))
        if differences:
            raise SnapshotUpgradeError(
                "Missing or unsupported v7 configuration fields.",
                tuple(f"/configuration/fields/{name.replace('~', '~0').replace('/', '~1')}" for name in differences),
            )
        if snapshot.kind == "C4Context":
            value = TypeAdapter[float | str](float | str).validate_python(fields["message_font_size"], strict=True)
            fields["message_font_size"] = {
                "$type": "mermaiden/value/C4Context/positive_number_or_numeric_text",
                "fields": {"root": value},
            }
        if snapshot.kind == "swimlane-beta":
            TypeAdapter[bool | LegacyLineHops](bool | LegacyLineHops).validate_python(fields["line_hops"], strict=True)
            fields["line_hops"] = {
                "$type": "mermaiden/value/swimlane-beta/line_hops_value",
                "fields": {"root": fields["line_hops"]},
            }
        if snapshot.kind == "packet":
            width = TypeAdapter(float).validate_python(fields["bits_per_row"], strict=True)
            if width < 1 or not width.is_integer():
                raise SnapshotUpgradeError(
                    "Packet row width must be a positive integral number.",
                    ("/configuration/fields/bits_per_row",),
                )
            fields["bits_per_row"] = int(width)
        fields.update(self.additions(snapshot.kind))
        candidate = replace(snapshot, version=8, configuration={**snapshot.configuration, "fields": fields})
        return SnapshotMigrationState(state.original, candidate, state.changes)

    def source_fields(self, kind: str) -> tuple[str, ...]:
        fields: Mapping[str, tuple[str, ...]] = {
            "C4Context": (
                "wrap",
                "diagram_margin_x",
                "diagram_margin_y",
                "c4_shape_margin",
                "c4_shape_padding",
                "width",
                "height",
                "box_margin",
                "use_max_width",
                "c4_shape_in_row",
                "next_line_padding_x",
                "c4_boundary_in_row",
                "message_font_size",
            ),
            "architecture-beta": (
                "wrap",
                "use_max_width",
                "padding",
                "icon_size",
                "font_size",
                "randomize",
                "node_separation",
                "ideal_edge_length_multiplier",
                "edge_elasticity",
                "num_iter",
                "seed",
            ),
            "block": ("wrap", "padding"),
            "classDiagram": ("wrap",),
            "cynefin-beta": (
                "wrap",
                "width",
                "height",
                "padding",
                "show_domain_descriptions",
                "boundary_amplitude",
                "seed",
            ),
            "erDiagram": (
                "wrap",
                "title_top_margin",
                "diagram_padding",
                "layout_direction",
                "min_entity_width",
                "min_entity_height",
                "entity_padding",
                "stroke",
                "fill",
                "use_max_width",
            ),
            "eventmodeling": ("wrap",),
            "flowchart": ("wrap",),
            "gantt": (
                "wrap",
                "title_top_margin",
                "bar_height",
                "top_padding",
                "right_padding",
                "left_padding",
                "grid_line_start_padding",
                "font_size",
                "section_font_size",
                "number_section_styles",
                "axis_format",
                "use_max_width",
                "top_axis",
                "weekday",
            ),
            "gitGraph": (
                "wrap",
                "title_top_margin",
                "diagram_padding",
                "node_label",
                "main_branch_name",
                "main_branch_order",
                "show_commit_label",
                "show_branches",
                "rotate_commit_label",
                "parallel_commits",
                "arrow_marker_absolute",
            ),
            "ishikawa-beta": ("wrap",),
            "journey": ("wrap",),
            "kanban": ("wrap", "padding", "section_width", "ticket_base_url"),
            "mindmap": ("wrap", "use_max_width", "padding", "max_node_width", "layout_algorithm"),
            "packet": ("wrap", "row_height", "bit_width", "bits_per_row", "show_bits", "padding_x", "padding_y"),
            "pie": ("wrap", "text_position", "donut_hole", "legend_position", "highlight_slice"),
            "radar-beta": (
                "wrap",
                "width",
                "height",
                "margin_top",
                "margin_right",
                "margin_bottom",
                "margin_left",
                "axis_scale_factor",
                "axis_label_factor",
                "curve_tension",
            ),
            "railroad-ebnf-beta": (
                "wrap",
                "compact_mode",
                "padding",
                "vertical_separation",
                "horizontal_separation",
                "arc_radius",
                "font_size",
                "font_family",
            ),
            "requirementDiagram": (
                "wrap",
                "use_max_width",
                "rect_fill",
                "text_color",
                "rect_border_size",
                "rect_border_color",
                "rect_min_width",
                "rect_min_height",
                "font_size",
                "rect_padding",
                "line_height",
            ),
            "sankey": ("wrap",),
            "sequenceDiagram": ("wrap",),
            "stateDiagram-v2": ("wrap", "title_top_margin", "use_max_width", "default_renderer"),
            "swimlane-beta": (
                "wrap",
                "line_hops",
                "ignore_cross_lane_edges",
                "optimize_ranks_by_crossings",
                "automatic_lane_ordering",
            ),
            "timeline": ("wrap",),
            "treeView-beta": ("wrap",),
            "venn-beta": ("wrap", "width", "height", "padding", "use_debug_layout"),
            "wardley-beta": ("wrap",),
        }
        return fields[kind]

    def additions(self, kind: str) -> Mapping[str, object]:
        values: Mapping[str, Mapping[str, object]] = {
            "C4Context": {
                "use_width": {
                    "$type": "mermaiden/value/C4Context/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/C4Context/unconfigured", "fields": {}}},
                },
                "person_font_size": {"$type": "mermaiden/value/C4Context/number_or_text", "fields": {"root": 14.0}},
                "person_font_family": '"Open Sans", sans-serif',
                "person_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "external_person_font_size": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": 14.0},
                },
                "external_person_font_family": '"Open Sans", sans-serif',
                "external_person_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "system_font_size": {"$type": "mermaiden/value/C4Context/number_or_text", "fields": {"root": 14.0}},
                "system_font_family": '"Open Sans", sans-serif',
                "system_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "external_system_font_size": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": 14.0},
                },
                "external_system_font_family": '"Open Sans", sans-serif',
                "external_system_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "system_db_font_size": {"$type": "mermaiden/value/C4Context/number_or_text", "fields": {"root": 14.0}},
                "system_db_font_family": '"Open Sans", sans-serif',
                "system_db_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "external_system_db_font_size": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": 14.0},
                },
                "external_system_db_font_family": '"Open Sans", sans-serif',
                "external_system_db_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "system_queue_font_size": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": 14.0},
                },
                "system_queue_font_family": '"Open Sans", sans-serif',
                "system_queue_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "external_system_queue_font_size": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": 14.0},
                },
                "external_system_queue_font_family": '"Open Sans", sans-serif',
                "external_system_queue_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "boundary_font_size": {
                    "$type": "mermaiden/value/C4Context/positive_number_or_numeric_text",
                    "fields": {"root": 14.0},
                },
                "boundary_font_family": '"Open Sans", sans-serif',
                "boundary_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "message_font_family": '"Open Sans", sans-serif',
                "message_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "container_font_size": {"$type": "mermaiden/value/C4Context/number_or_text", "fields": {"root": 14.0}},
                "container_font_family": '"Open Sans", sans-serif',
                "container_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "external_container_font_size": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": 14.0},
                },
                "external_container_font_family": '"Open Sans", sans-serif',
                "external_container_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "container_db_font_size": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": 14.0},
                },
                "container_db_font_family": '"Open Sans", sans-serif',
                "container_db_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "external_container_db_font_size": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": 14.0},
                },
                "external_container_db_font_family": '"Open Sans", sans-serif',
                "external_container_db_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "container_queue_font_size": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": 14.0},
                },
                "container_queue_font_family": '"Open Sans", sans-serif',
                "container_queue_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "external_container_queue_font_size": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": 14.0},
                },
                "external_container_queue_font_family": '"Open Sans", sans-serif',
                "external_container_queue_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "component_font_size": {"$type": "mermaiden/value/C4Context/number_or_text", "fields": {"root": 14.0}},
                "component_font_family": '"Open Sans", sans-serif',
                "component_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "external_component_font_size": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": 14.0},
                },
                "external_component_font_family": '"Open Sans", sans-serif',
                "external_component_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "component_db_font_size": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": 14.0},
                },
                "component_db_font_family": '"Open Sans", sans-serif',
                "component_db_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "external_component_db_font_size": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": 14.0},
                },
                "external_component_db_font_family": '"Open Sans", sans-serif',
                "external_component_db_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "component_queue_font_size": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": 14.0},
                },
                "component_queue_font_family": '"Open Sans", sans-serif',
                "component_queue_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "external_component_queue_font_size": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": 14.0},
                },
                "external_component_queue_font_family": '"Open Sans", sans-serif',
                "external_component_queue_font_weight": {
                    "$type": "mermaiden/value/C4Context/number_or_text",
                    "fields": {"root": "normal"},
                },
                "wrap_padding": 10.0,
                "person_bg_color": "#08427B",
                "person_border_color": "#073B6F",
                "external_person_bg_color": "#686868",
                "external_person_border_color": "#8A8A8A",
                "system_bg_color": "#1168BD",
                "system_border_color": "#3C7FC0",
                "system_db_bg_color": "#1168BD",
                "system_db_border_color": "#3C7FC0",
                "system_queue_bg_color": "#1168BD",
                "system_queue_border_color": "#3C7FC0",
                "external_system_bg_color": "#999999",
                "external_system_border_color": "#8A8A8A",
                "external_system_db_bg_color": "#999999",
                "external_system_db_border_color": "#8A8A8A",
                "external_system_queue_bg_color": "#999999",
                "external_system_queue_border_color": "#8A8A8A",
                "container_bg_color": "#438DD5",
                "container_border_color": "#3C7FC0",
                "container_db_bg_color": "#438DD5",
                "container_db_border_color": "#3C7FC0",
                "container_queue_bg_color": "#438DD5",
                "container_queue_border_color": "#3C7FC0",
                "external_container_bg_color": "#B3B3B3",
                "external_container_border_color": "#A6A6A6",
                "external_container_db_bg_color": "#B3B3B3",
                "external_container_db_border_color": "#A6A6A6",
                "external_container_queue_bg_color": "#B3B3B3",
                "external_container_queue_border_color": "#A6A6A6",
                "component_bg_color": "#85BBF0",
                "component_border_color": "#78A8D8",
                "component_db_bg_color": "#85BBF0",
                "component_db_border_color": "#78A8D8",
                "component_queue_bg_color": "#85BBF0",
                "component_queue_border_color": "#78A8D8",
                "external_component_bg_color": "#CCCCCC",
                "external_component_border_color": "#BFBFBF",
                "external_component_db_bg_color": "#CCCCCC",
                "external_component_db_border_color": "#BFBFBF",
                "external_component_queue_bg_color": "#CCCCCC",
                "external_component_queue_border_color": "#BFBFBF",
            },
            "architecture-beta": {
                "use_width": {
                    "$type": "mermaiden/value/architecture-beta/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/architecture-beta/unconfigured", "fields": {}}},
                }
            },
            "block": {
                "use_width": {
                    "$type": "mermaiden/value/block/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/block/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
            },
            "classDiagram": {
                "use_width": {
                    "$type": "mermaiden/value/classDiagram/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/classDiagram/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
                "title_top_margin": 25,
                "arrow_marker_absolute": False,
                "divider_margin": 10.0,
                "padding": 5.0,
                "text_height": 10.0,
                "default_renderer": {"$enum": "mermaiden/enum/classDiagram/class_renderer", "value": "dagre-wrapper"},
                "node_spacing": {
                    "$type": "mermaiden/value/classDiagram/omittable_non_negative_integer",
                    "fields": {"root": {"$type": "mermaiden/value/classDiagram/unconfigured", "fields": {}}},
                },
                "rank_spacing": {
                    "$type": "mermaiden/value/classDiagram/omittable_non_negative_integer",
                    "fields": {"root": {"$type": "mermaiden/value/classDiagram/unconfigured", "fields": {}}},
                },
                "diagram_padding": 20,
                "html_labels": False,
                "hide_empty_members_box": False,
                "hierarchical_namespaces": True,
            },
            "cynefin-beta": {
                "use_width": {
                    "$type": "mermaiden/value/cynefin-beta/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/cynefin-beta/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
            },
            "erDiagram": {
                "use_width": {
                    "$type": "mermaiden/value/erDiagram/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/erDiagram/unconfigured", "fields": {}}},
                },
                "node_spacing": 140,
                "rank_spacing": 80,
                "font_size": 12,
            },
            "eventmodeling": {
                "use_width": {
                    "$type": "mermaiden/value/eventmodeling/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/eventmodeling/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
                "padding": 30.0,
                "row_height": 32.0,
            },
            "flowchart": {
                "use_width": {
                    "$type": "mermaiden/value/flowchart/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/flowchart/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
                "title_top_margin": 25,
                "sub_graph_title_margin": {
                    "$type": "mermaiden/value/flowchart/flowchart_subgraph_title_margin",
                    "fields": {
                        "top": {
                            "$type": "mermaiden/value/flowchart/omittable_non_negative_integer",
                            "fields": {"root": 0},
                        },
                        "bottom": {
                            "$type": "mermaiden/value/flowchart/omittable_non_negative_integer",
                            "fields": {"root": 0},
                        },
                    },
                },
                "arrow_marker_absolute": {
                    "$type": "mermaiden/value/flowchart/omittable_boolean",
                    "fields": {"root": {"$type": "mermaiden/value/flowchart/unconfigured", "fields": {}}},
                },
                "diagram_padding": 8,
                "node_spacing": 50,
                "rank_spacing": 50,
                "curve": {"$enum": "mermaiden/enum/flowchart/flowchart_curve", "value": "basis"},
                "padding": 15.0,
                "default_renderer": {"$enum": "mermaiden/enum/flowchart/flowchart_renderer", "value": "dagre-wrapper"},
                "wrapping_width": 200.0,
                "inherit_dir": False,
            },
            "gantt": {
                "use_width": {
                    "$type": "mermaiden/value/gantt/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/gantt/unconfigured", "fields": {}}},
                },
                "bar_gap": 4,
                "tick_interval": {
                    "$type": "mermaiden/value/gantt/omittable_text",
                    "fields": {"root": {"$type": "mermaiden/value/gantt/unconfigured", "fields": {}}},
                },
                "display_mode": {"$enum": "mermaiden/enum/gantt/gantt_display_mode", "value": ""},
            },
            "gitGraph": {
                "use_width": {
                    "$type": "mermaiden/value/gitGraph/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/gitGraph/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
            },
            "ishikawa-beta": {
                "use_width": {
                    "$type": "mermaiden/value/ishikawa-beta/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/ishikawa-beta/unconfigured", "fields": {}}},
                },
                "use_max_width": False,
                "diagram_padding": 20,
            },
            "journey": {
                "use_width": {
                    "$type": "mermaiden/value/journey/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/journey/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
                "diagram_margin_x": 50,
                "diagram_margin_y": 10,
                "left_margin": 150,
                "max_label_width": 360,
                "width": 150,
                "height": 50,
                "box_margin": 10,
                "box_text_margin": 5,
                "note_margin": 10,
                "message_margin": 35,
                "message_align": {"$enum": "mermaiden/enum/journey/journey_message_alignment", "value": "center"},
                "bottom_margin_adj": 1,
                "right_angles": False,
                "task_font_size": {"$type": "mermaiden/value/journey/number_or_numeric_text", "fields": {"root": 14.0}},
                "task_font_family": '"Open Sans", sans-serif',
                "task_margin": 50.0,
                "activation_width": 10.0,
                "text_placement": "fo",
                "actor_colours": {
                    "$type": "mermaiden/value/journey/journey_colour_palette",
                    "fields": {"root": ["#8FBC8F", "#7CFC00", "#00FFFF", "#20B2AA", "#B0E0E6", "#FFFFE0"]},
                },
                "section_fills": {
                    "$type": "mermaiden/value/journey/journey_colour_palette",
                    "fields": {"root": ["#191970", "#8B008B", "#4B0082", "#2F4F4F", "#800000", "#8B4513", "#00008B"]},
                },
                "section_colours": {
                    "$type": "mermaiden/value/journey/journey_colour_palette",
                    "fields": {"root": ["#fff"]},
                },
                "title_color": "",
                "title_font_family": '"trebuchet ms", verdana, arial, sans-serif',
                "title_font_size": "4ex",
            },
            "kanban": {
                "use_width": {
                    "$type": "mermaiden/value/kanban/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/kanban/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
            },
            "mindmap": {
                "use_width": {
                    "$type": "mermaiden/value/mindmap/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/mindmap/unconfigured", "fields": {}}},
                }
            },
            "packet": {
                "use_width": {
                    "$type": "mermaiden/value/packet/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/packet/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
            },
            "pie": {
                "use_width": {
                    "$type": "mermaiden/value/pie/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/pie/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
            },
            "radar-beta": {
                "use_width": {
                    "$type": "mermaiden/value/radar-beta/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/radar-beta/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
            },
            "railroad-ebnf-beta": {
                "use_width": {
                    "$type": "mermaiden/value/railroad-ebnf-beta/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/railroad-ebnf-beta/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
                "terminal_fill": "#FFFFC0",
                "terminal_stroke": "#000000",
                "terminal_text_color": "#000000",
                "non_terminal_fill": "#FFFFFF",
                "non_terminal_stroke": "#000000",
                "non_terminal_text_color": "#000000",
                "line_color": "#000000",
                "stroke_width": 2.0,
                "marker_fill": "#000000",
                "comment_fill": "#E8E8E8",
                "comment_stroke": "#888888",
                "comment_text_color": "#666666",
                "special_fill": "#F0E0FF",
                "special_stroke": "#8800CC",
                "rule_name_color": "#000066",
                "show_markers": True,
                "marker_radius": 5.0,
            },
            "requirementDiagram": {
                "use_width": {
                    "$type": "mermaiden/value/requirementDiagram/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/requirementDiagram/unconfigured", "fields": {}}},
                }
            },
            "sankey": {
                "use_width": {
                    "$type": "mermaiden/value/sankey/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/sankey/unconfigured", "fields": {}}},
                },
                "use_max_width": False,
                "width": 600.0,
                "height": 400.0,
                "link_color": "gradient",
                "node_alignment": {"$enum": "mermaiden/enum/sankey/sankey_node_alignment", "value": "justify"},
                "show_values": True,
                "prefix": "",
                "suffix": "",
                "node_width": 10.0,
                "node_padding": 12.0,
                "label_style": {"$enum": "mermaiden/enum/sankey/sankey_label_style", "value": "legacy"},
                "node_colors": {
                    "$type": "mermaiden/value/sankey/omittable_sankey_node_colours",
                    "fields": {"root": {"$type": "mermaiden/value/sankey/unconfigured", "fields": {}}},
                },
            },
            "sequenceDiagram": {
                "use_width": {
                    "$type": "mermaiden/value/sequenceDiagram/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/sequenceDiagram/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
                "arrow_marker_absolute": {
                    "$type": "mermaiden/value/sequenceDiagram/omittable_boolean",
                    "fields": {"root": {"$type": "mermaiden/value/sequenceDiagram/unconfigured", "fields": {}}},
                },
                "hide_unused_participants": False,
                "activation_width": 10,
                "diagram_margin_x": 50,
                "diagram_margin_y": 10,
                "actor_margin": 50,
                "width": 150,
                "height": 65,
                "box_margin": 10,
                "box_text_margin": 5,
                "note_margin": 10,
                "message_margin": 35,
                "message_align": {
                    "$enum": "mermaiden/enum/sequenceDiagram/sequence_message_alignment",
                    "value": "center",
                },
                "mirror_actors": True,
                "force_menus": False,
                "bottom_margin_adj": 1,
                "right_angles": False,
                "show_sequence_numbers": False,
                "actor_font_size": {
                    "$type": "mermaiden/value/sequenceDiagram/number_or_text",
                    "fields": {"root": 14.0},
                },
                "actor_font_family": '"Open Sans", sans-serif',
                "actor_font_weight": {
                    "$type": "mermaiden/value/sequenceDiagram/number_or_text",
                    "fields": {"root": 400.0},
                },
                "note_font_size": {"$type": "mermaiden/value/sequenceDiagram/number_or_text", "fields": {"root": 14.0}},
                "note_font_family": '"trebuchet ms", verdana, arial, sans-serif',
                "note_font_weight": {
                    "$type": "mermaiden/value/sequenceDiagram/number_or_text",
                    "fields": {"root": 400.0},
                },
                "note_align": {"$enum": "mermaiden/enum/sequenceDiagram/sequence_note_alignment", "value": "center"},
                "message_font_size": {
                    "$type": "mermaiden/value/sequenceDiagram/number_or_text",
                    "fields": {"root": 16.0},
                },
                "message_font_family": '"trebuchet ms", verdana, arial, sans-serif',
                "message_font_weight": {
                    "$type": "mermaiden/value/sequenceDiagram/number_or_text",
                    "fields": {"root": 400.0},
                },
                "wrap_padding": 10.0,
                "label_box_width": 50.0,
                "label_box_height": 20.0,
            },
            "stateDiagram-v2": {
                "use_width": {
                    "$type": "mermaiden/value/stateDiagram-v2/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/stateDiagram-v2/unconfigured", "fields": {}}},
                },
                "arrow_marker_absolute": {
                    "$type": "mermaiden/value/stateDiagram-v2/omittable_boolean",
                    "fields": {"root": {"$type": "mermaiden/value/stateDiagram-v2/unconfigured", "fields": {}}},
                },
                "divider_margin": 10.0,
                "size_unit": 5.0,
                "padding": 8.0,
                "text_height": 10.0,
                "title_shift": -15.0,
                "note_margin": 10.0,
                "node_spacing": {
                    "$type": "mermaiden/value/stateDiagram-v2/omittable_non_negative_integer",
                    "fields": {"root": {"$type": "mermaiden/value/stateDiagram-v2/unconfigured", "fields": {}}},
                },
                "rank_spacing": {
                    "$type": "mermaiden/value/stateDiagram-v2/omittable_non_negative_integer",
                    "fields": {"root": {"$type": "mermaiden/value/stateDiagram-v2/unconfigured", "fields": {}}},
                },
                "fork_width": 70.0,
                "fork_height": 7.0,
                "mini_padding": 2.0,
                "font_size_factor": 5.02,
                "font_size": 24.0,
                "label_height": 16.0,
                "edge_length_factor": "20",
                "composit_title_size": 35.0,
                "radius": 5.0,
            },
            "swimlane-beta": {
                "use_width": {
                    "$type": "mermaiden/value/swimlane-beta/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/swimlane-beta/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
            },
            "timeline": {
                "use_width": {
                    "$type": "mermaiden/value/timeline/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/timeline/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
                "diagram_margin_x": 50,
                "diagram_margin_y": 10,
                "left_margin": 150,
                "width": 150,
                "height": 50,
                "padding": {
                    "$type": "mermaiden/value/timeline/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/timeline/unconfigured", "fields": {}}},
                },
                "box_margin": 10,
                "box_text_margin": 5,
                "note_margin": 10,
                "message_margin": 35,
                "message_align": {"$enum": "mermaiden/enum/timeline/timeline_message_alignment", "value": "center"},
                "bottom_margin_adj": 1,
                "right_angles": False,
                "task_font_size": {"$type": "mermaiden/value/timeline/number_or_text", "fields": {"root": 14.0}},
                "task_font_family": '"Open Sans", sans-serif',
                "task_margin": 50.0,
                "activation_width": 10.0,
                "text_placement": "fo",
                "actor_colours": {
                    "$type": "mermaiden/value/timeline/timeline_colour_palette",
                    "fields": {"root": ["#8FBC8F", "#7CFC00", "#00FFFF", "#20B2AA", "#B0E0E6", "#FFFFE0"]},
                },
                "section_fills": {
                    "$type": "mermaiden/value/timeline/timeline_colour_palette",
                    "fields": {"root": ["#191970", "#8B008B", "#4B0082", "#2F4F4F", "#800000", "#8B4513", "#00008B"]},
                },
                "section_colours": {
                    "$type": "mermaiden/value/timeline/timeline_colour_palette",
                    "fields": {"root": ["#fff"]},
                },
                "disable_multicolor": False,
            },
            "treeView-beta": {
                "use_width": {
                    "$type": "mermaiden/value/treeView-beta/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/treeView-beta/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
                "row_indent": 10.0,
                "padding_x": 5.0,
                "padding_y": 5.0,
                "line_thickness": 1.0,
                "show_icons": False,
                "default_icon_pack": "",
                "filename_icons": {"$type": "mermaiden/value/treeView-beta/tree_view_icon_map", "fields": {"root": {}}},
                "extension_icons": {
                    "$type": "mermaiden/value/treeView-beta/tree_view_icon_map",
                    "fields": {"root": {}},
                },
            },
            "venn-beta": {
                "use_width": {
                    "$type": "mermaiden/value/venn-beta/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/venn-beta/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
            },
            "wardley-beta": {
                "use_width": {
                    "$type": "mermaiden/value/wardley-beta/omittable_number",
                    "fields": {"root": {"$type": "mermaiden/value/wardley-beta/unconfigured", "fields": {}}},
                },
                "use_max_width": True,
                "width": 900.0,
                "height": 600.0,
                "padding": 48.0,
                "node_radius": 6.0,
                "node_label_offset": 8.0,
                "axis_font_size": 12.0,
                "label_font_size": 10.0,
                "show_grid": False,
            },
        }
        return values[kind]
