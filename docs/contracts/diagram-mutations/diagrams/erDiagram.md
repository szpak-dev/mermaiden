# `erDiagram` mutation matrix

Generated from public `Application` discovery. Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `entity` | `update_element` | parents: `$root`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`; move_or_reorder_only: `elements`; immutable: `id` |
| `entity_attribute` | `update_element` | parents: `entity`; move: `move_element` | updateable: `label`, `data_type`, `keys`, `comment`; immutable: `id` |

## Relations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `entity_relationship` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`, `notation`; immutable: `id` |

## Annotations

None.
