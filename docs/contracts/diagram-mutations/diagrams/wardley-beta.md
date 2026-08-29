# `wardley-beta` mutation matrix

Generated from [`wardley-beta.json`](wardley-beta.json). Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `component` | `update_element` | parents: `$root`; move: `move_element` | updateable: `label`, `visibility`, `evolution`, `decorator`, `anchor`; immutable: `id` |
| `evolution` | `update_element` | parents: `$root`; move: `move_element` | updateable: `label`, `target`; immutable: `id` |
| `pipeline` | `update_element` | parents: `$root`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`; move_or_reorder_only: `elements`; immutable: `id` |

## Relations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `dependency` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`, `operator`; immutable: `id` |

## Annotations

None.
