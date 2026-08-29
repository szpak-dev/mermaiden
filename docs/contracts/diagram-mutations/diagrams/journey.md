# `journey` mutation matrix

Generated from [`journey.json`](journey.json). Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `journey_section` | `update_element` | parents: `$root`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`; move_or_reorder_only: `elements`; immutable: `id` |
| `journey_task` | `update_element` | parents: `journey_section`; move: `move_element` | updateable: `label`, `score`, `actors`; immutable: `id` |

## Relations

None.

## Annotations

None.
