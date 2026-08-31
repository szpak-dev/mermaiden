# `flowchart` mutation matrix

Generated from public `Application` discovery. Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `action` | `update_element` | parents: `$root`, `flow_group`; move: `move_element` | updateable: `label`; immutable: `id` |
| `data_store` | `update_element` | parents: `$root`, `flow_group`; move: `move_element` | updateable: `label`; immutable: `id` |
| `decision` | `update_element` | parents: `$root`, `flow_group`; move: `move_element` | updateable: `label`; immutable: `id` |
| `document` | `update_element` | parents: `$root`, `flow_group`; move: `move_element` | updateable: `label`; immutable: `id` |
| `end` | `update_element` | parents: `$root`, `flow_group`; move: `move_element` | updateable: `label`; immutable: `id` |
| `flow_group` | `update_element` | parents: `$root`, `flow_group`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`, `direction`; move_or_reorder_only: `elements`; immutable: `id` |
| `flow_node` | `update_element` | parents: `$root`, `flow_group`; move: `move_element` | updateable: `label`; immutable: `id` |
| `input_output` | `update_element` | parents: `$root`, `flow_group`; move: `move_element` | updateable: `label`; immutable: `id` |
| `junction` | `update_element` | parents: `$root`, `flow_group`; move: `move_element` | updateable: `label`; immutable: `id` |
| `start` | `update_element` | parents: `$root`, `flow_group`; move: `move_element` | updateable: `label`; immutable: `id` |
| `subprocess` | `update_element` | parents: `$root`, `flow_group`; move: `move_element` | updateable: `label`; immutable: `id` |

## Relations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `conditional_flow` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`; immutable: `id` |
| `flow` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`; immutable: `id` |

## Annotations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `note` | `update_annotation` | `targets` via `update_annotation`; ordered: `true` | updateable: `targets`, `text`; immutable: `id` |
