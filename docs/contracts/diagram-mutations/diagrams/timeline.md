# `timeline` mutation matrix

Generated from [`timeline.json`](timeline.json). Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `timeline_event` | `update_element` | parents: `timeline_period`; move: `move_element` | updateable: `label`; immutable: `id` |
| `timeline_period` | `update_element` | parents: `$root`, `timeline_section`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`; move_or_reorder_only: `elements`; immutable: `id` |
| `timeline_section` | `update_element` | parents: `$root`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`; move_or_reorder_only: `elements`; immutable: `id` |

## Relations

None.

## Annotations

None.
