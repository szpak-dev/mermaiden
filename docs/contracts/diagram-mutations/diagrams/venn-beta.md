# `venn-beta` mutation matrix

Generated from public `Application` discovery. Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `venn_set` | `update_element` | parents: `$root`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`, `size`; move_or_reorder_only: `elements`; immutable: `id` |
| `venn_text` | `update_element` | parents: `venn_set`, `venn_union`; move: `move_element` | updateable: `label`; immutable: `id` |
| `venn_union` | `update_element` | parents: `$root`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`, `set_ids`, `size`; move_or_reorder_only: `elements`; immutable: `id` |

## Relations

None.

## Annotations

None.
