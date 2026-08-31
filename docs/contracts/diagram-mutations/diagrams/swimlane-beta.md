# `swimlane-beta` mutation matrix

Generated from public `Application` discovery. Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `activity` | `update_element` | parents: `swimlane`; move: `move_element` | updateable: `label`; immutable: `id` |
| `connector` | `update_element` | parents: `swimlane`; move: `move_element` | updateable: `label`; immutable: `id` |
| `decision` | `update_element` | parents: `swimlane`; move: `move_element` | updateable: `label`; immutable: `id` |
| `end` | `update_element` | parents: `swimlane`; move: `move_element` | updateable: `label`; immutable: `id` |
| `start` | `update_element` | parents: `swimlane`; move: `move_element` | updateable: `label`; immutable: `id` |
| `swimlane` | `update_element` | parents: `$root`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`; move_or_reorder_only: `elements`; immutable: `id` |
| `swimlane_node` | `update_element` | parents: `swimlane`; move: `move_element` | updateable: `label`; immutable: `id` |

## Relations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `conditional_flow` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`; immutable: `id` |
| `flow` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`; immutable: `id` |

## Annotations

None.
