# `architecture-beta` mutation matrix

Generated from [`architecture-beta.json`](architecture-beta.json). Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `architecture_group` | `update_element` | parents: `$root`, `architecture_group`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`, `columns`; move_or_reorder_only: `elements`; immutable: `id` |
| `junction` | `update_element` | parents: `$root`, `architecture_group`; move: `move_element` | updateable: `label`; immutable: `id` |
| `service` | `update_element` | parents: `$root`, `architecture_group`; move: `move_element` | updateable: `label`; immutable: `id` |

## Relations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `alignment` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`, `axis`; immutable: `id` |
| `edge` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`, `source_port`, `target_port`; immutable: `id` |

## Annotations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `architecture_note` | `update_annotation` | `targets` via `update_annotation`; ordered: `true` | updateable: `targets`, `text`; immutable: `id` |
