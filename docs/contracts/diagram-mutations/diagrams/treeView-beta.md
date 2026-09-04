# `treeView-beta` mutation matrix

Generated from public `Application` discovery. Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `tree_item` | `update_element` | parents: `$root`; move: `move_element` | updateable: `label`, `item_type`; immutable: `id` |

## Relations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `tree_branch` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`; immutable: `id` |

## Annotations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `tree_annotation` | `update_annotation` | `targets` via `update_annotation`; ordered: `true` | updateable: `targets`, `highlight`, `icon`, `description`; immutable: `id` |
