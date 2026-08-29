# `eventmodeling` mutation matrix

Generated from [`eventmodeling.json`](eventmodeling.json). Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `actor` | `update_element` | parents: `swimlane`; move: `move_element` | updateable: `label`; immutable: `id` |
| `command` | `update_element` | parents: `swimlane`; move: `move_element` | updateable: `label`; immutable: `id` |
| `event` | `update_element` | parents: `swimlane`; move: `move_element` | updateable: `label`; immutable: `id` |
| `swimlane` | `update_element` | parents: `$root`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`; move_or_reorder_only: `elements`; immutable: `id` |
| `view` | `update_element` | parents: `swimlane`; move: `move_element` | updateable: `label`; immutable: `id` |

## Relations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `flow` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`; immutable: `id` |

## Annotations

None.
