# `gitGraph` mutation matrix

Generated from public `Application` discovery. Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `branch` | `update_element` | parents: `$root`; move: `move_element` | updateable: `label`, `order`; immutable: `id` |
| `checkout` | `update_element` | parents: `$root`; move: `move_element` | updateable: `label`; immutable: `id` |
| `commit` | `update_element` | parents: `$root`; move: `move_element` | updateable: `label`, `commit_type`, `tag`; immutable: `id` |

## Relations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `commit_relation` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`; immutable: `id` |

## Annotations

None.
