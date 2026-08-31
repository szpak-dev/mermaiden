# `ishikawa-beta` mutation matrix

Generated from public `Application` discovery. Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `category` | `update_element` | parents: `$root`, `category`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`; move_or_reorder_only: `elements`; immutable: `id` |
| `cause` | `update_element` | parents: `category`; move: `move_element` | updateable: `label`; immutable: `id` |
| `effect` | `update_element` | parents: `$root`; move: `move_element` | updateable: `label`; immutable: `id` |

## Relations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `cause_relation` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`; immutable: `id` |

## Annotations

None.
