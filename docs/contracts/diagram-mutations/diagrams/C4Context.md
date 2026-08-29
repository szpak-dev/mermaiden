# `C4Context` mutation matrix

Generated from [`C4Context.json`](C4Context.json). Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `c4_element` | `update_element` | parents: `$root`; move: `move_element` | updateable: `label`, `description`, `technology`; immutable: `id` |
| `person` | `update_element` | parents: `$root`; move: `move_element` | updateable: `label`, `description`, `technology`; immutable: `id` |
| `system` | `update_element` | parents: `$root`; move: `move_element` | updateable: `label`, `description`, `technology`; immutable: `id` |
| `system_db` | `update_element` | parents: `$root`; move: `move_element` | updateable: `label`, `description`, `technology`; immutable: `id` |
| `system_queue` | `update_element` | parents: `$root`; move: `move_element` | updateable: `label`, `description`, `technology`; immutable: `id` |

## Relations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `relationship` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`, `direction`, `offset_x`, `offset_y`; immutable: `id` |

## Annotations

None.
