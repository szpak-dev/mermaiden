# `block` mutation matrix

Generated from public `Application` discovery. Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `block_group` | `update_element` | parents: `$root`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`, `columns`, `span`; move_or_reorder_only: `elements`; immutable: `id` |
| `block_node` | `update_element` | parents: `$root`, `block_group`; move: `move_element` | updateable: `label`, `span`; immutable: `id` |
| `block_space` | `update_element` | parents: `$root`, `block_group`; move: `move_element` | updateable: `label`, `span`; immutable: `id` |

## Relations

None.

## Annotations

None.
