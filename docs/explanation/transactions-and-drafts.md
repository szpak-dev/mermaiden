# Transactions and drafts

A diagram often becomes valid only after several related objects exist. Rejecting every incomplete intermediate step
would leave authoring awkward; rendering every incomplete step would produce unreliable output. Mermaiden separates
those concerns with drafts and transactions.

A draft is typed, persistable diagram state that still has blocking constraints. Callers may snapshot and restore it, so
an unfinished editing session is not lost. `Application.render()` refuses that same state until its blocking
constraints are resolved. Persistence answers “can this state be represented safely?” while rendering asks whether
this is a complete diagram.

Single-command execution validates the command and inspects the resulting diagram according to the command contract.
`apply_batch()` handles changes whose intermediate states should not be judged separately. It applies an ordered
sequence, checks the complete result once, and commits only when that result can commit.

The rollback boundary includes more than expected validation errors. Invalid payloads, unknown operations, constraint
failures, and unexpected command failures all restore the byte-for-byte pre-batch snapshot. A failed edit therefore does
not leave a relation retargeted, a subtree half-moved, or a collection partially reordered.

No-op operations remain successful. Reapplying an existing value or placement need not manufacture a change merely to
prove that the command ran. The caller gets stable state, and the same snapshot remains authoritative.
