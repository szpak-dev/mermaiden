# `railroad-ebnf-beta` mutation matrix

Generated from public `Application` discovery. Do not edit directly.

Root ordering: `reorder_elements` over the exact direct-member permutation.

## Elements

| Kind | Update command | Placement or retargeting | Fields |
| --- | --- | --- | --- |
| `alternative_expression` | `update_element` | parents: `alternative_expression`, `composite_expression`, `group_expression`, `optional_expression`, `repetition_expression`, `sequence_expression`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`; move_or_reorder_only: `elements`; immutable: `id` |
| `composite_expression` | `update_element` | parents: `alternative_expression`, `composite_expression`, `group_expression`, `optional_expression`, `repetition_expression`, `sequence_expression`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`; move_or_reorder_only: `elements`; immutable: `id` |
| `group_expression` | `update_element` | parents: `alternative_expression`, `composite_expression`, `group_expression`, `optional_expression`, `repetition_expression`, `sequence_expression`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`; move_or_reorder_only: `elements`; immutable: `id` |
| `non_terminal` | `update_element` | parents: `alternative_expression`, `composite_expression`, `group_expression`, `optional_expression`, `repetition_expression`, `sequence_expression`; move: `move_element` | updateable: `label`; immutable: `id` |
| `optional_expression` | `update_element` | parents: `alternative_expression`, `composite_expression`, `group_expression`, `optional_expression`, `repetition_expression`, `sequence_expression`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`; move_or_reorder_only: `elements`; immutable: `id` |
| `repetition_expression` | `update_element` | parents: `alternative_expression`, `composite_expression`, `group_expression`, `optional_expression`, `repetition_expression`, `sequence_expression`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`; move_or_reorder_only: `elements`; immutable: `id` |
| `sequence_expression` | `update_element` | parents: `$root`, `alternative_expression`, `composite_expression`, `group_expression`, `optional_expression`, `repetition_expression`, `sequence_expression`; move: `move_element`; direct children use `reorder_elements` | updateable: `label`; move_or_reorder_only: `elements`; immutable: `id` |
| `special` | `update_element` | parents: `alternative_expression`, `composite_expression`, `group_expression`, `optional_expression`, `repetition_expression`, `sequence_expression`; move: `move_element` | updateable: `label`; immutable: `id` |
| `terminal` | `update_element` | parents: `alternative_expression`, `composite_expression`, `group_expression`, `optional_expression`, `repetition_expression`, `sequence_expression`; move: `move_element` | updateable: `label`; immutable: `id` |

## Relations

None.

## Annotations

None.
