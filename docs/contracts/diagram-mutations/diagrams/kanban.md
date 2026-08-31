# `kanban` mutation matrix

Generated from public `Application` discovery. Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `column` | `update_element` | parents: `$root`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`; move_or_reorder_only: `elements`; immutable: `id` |
| `task` | `update_element` | parents: `column`; move: `move_element` | updateable: `label`, `assigned`, `ticket`, `priority`; immutable: `id` |

## Relations

None.

## Annotations

None.
