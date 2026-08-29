# `stateDiagram-v2` mutation matrix

Generated from [`stateDiagram-v2.json`](stateDiagram-v2.json). Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `choice` | `update_element` | parents: `$root`, `composite_state`; move: `move_element` | updateable: `label`; immutable: `id` |
| `composite_state` | `update_element` | parents: `$root`, `composite_state`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`; move_or_reorder_only: `elements`; immutable: `id` |
| `final` | `update_element` | parents: `$root`, `composite_state`; move: `move_element` | updateable: `label`; immutable: `id` |
| `fork` | `update_element` | parents: `$root`, `composite_state`; move: `move_element` | updateable: `label`; immutable: `id` |
| `initial` | `update_element` | parents: `$root`, `composite_state`; move: `move_element` | updateable: `label`; immutable: `id` |
| `join` | `update_element` | parents: `$root`, `composite_state`; move: `move_element` | updateable: `label`; immutable: `id` |
| `state` | `update_element` | parents: `$root`, `composite_state`; move: `move_element` | updateable: `label`; immutable: `id` |
| `state_node` | `update_element` | parents: `$root`, `composite_state`; move: `move_element` | updateable: `label`; immutable: `id` |

## Relations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `state_transition` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`, `scope_id`, `source_terminal`, `target_terminal`; immutable: `id` |

## Annotations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `state_note` | `update_annotation` | `targets` via `update_annotation`; ordered: `true` | updateable: `targets`, `text`, `position`, `scope_id`; immutable: `id` |
