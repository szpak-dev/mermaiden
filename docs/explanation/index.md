# Explanation

Mermaiden is easier to use once four boundaries are clear:

- [The typed semantic model](typed-semantic-model.md) separates diagram meaning from Mermaid syntax.
- [Transactions and drafts](transactions-and-drafts.md) explain when incomplete state may persist and when it may
  render.
- [Snapshot identity](snapshot-identity.md) makes persisted types explicit without importing Python paths.
- [The Mermaid boundary](mermaid-boundary.md) separates deterministic source generation from external SVG validation.
