# `sequenceDiagram` mutation matrix

Generated from public `Application` discovery. Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `participant` | `update_element` | parents: `$root`, `participant_box`; move: `move_element` | updateable: `label`, `participant_kind`, `created`; immutable: `id` |
| `participant_box` | `update_element` | parents: `$root`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`, `color`; move_or_reorder_only: `elements`; immutable: `id` |

## Relations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `control` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`, `control_kind`; immutable: `id` |
| `directive` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`, `directive_kind`; immutable: `id` |
| `message` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`, `message_kind`, `activate`, `deactivate`; immutable: `id` |
| `participant_event` | `update_relation` | `element_ids` via `update_relation`; ordered: `true` | updateable: `element_ids`, `label`, `action`; immutable: `id` |

## Annotations

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `sequence_note` | `update_annotation` | `targets` via `update_annotation`; ordered: `true` | updateable: `targets`, `text`, `position`; immutable: `id` |
