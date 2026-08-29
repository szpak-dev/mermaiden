# `classDiagram` mutation matrix

Generated from [`classDiagram.json`](classDiagram.json). Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `class` | `update_element` | parents: `$root`, `class_namespace`; move: `move_element` | updateable: `label`, `attributes`, `methods`, `annotations`, `comment`; immutable: `id` |
| `class_namespace` | `update_element` | parents: `$root`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`, `comment`; move_or_reorder_only: `elements`; immutable: `id` |

## Relations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `class_relation` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`, `relation_kind`, `source_label`, `target_label`; immutable: `id` |

## Annotations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `class_note` | `update_annotation` | `targets` via `update_annotation`; ordered: `true` | updateable: `targets`, `text`; immutable: `id` |
