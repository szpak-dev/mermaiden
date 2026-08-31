# `requirementDiagram` mutation matrix

Generated from public `Application` discovery. Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `requirement` | `update_element` | parents: `$root`; move: `move_element` | updateable: `label`, `requirement_id`, `text`, `requirement_type`, `risk`, `verification_method`; immutable: `id` |
| `requirement_element` | `update_element` | parents: `$root`; move: `move_element` | updateable: `label`, `element_type`, `document_reference`; immutable: `id` |

## Relations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `requirement_relation` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`, `relation_kind`; immutable: `id` |

## Annotations

None.
