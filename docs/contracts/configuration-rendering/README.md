# Configuration rendering proof

This directory contains executable evidence for Mermaiden's typed Mermaid configuration contract.

- `sources/` contains one populated Mermaid source for every registered diagram kind. Every source explicitly
  serializes every configuration field supported by that kind.
- `rendered/` contains the corresponding SVG produced by the Mermaid CLI version pinned in
  `src/mermaiden/mermaid/compatibility/schema.lock.json`.
- `manifest.json` binds each source and SVG by SHA-256 and records every configuration field and valid probe value.
- `enclosure-corpus-audit.json` records the revision-pinned audit of every diagram stored in Enclosure on
  2026-10-19. Empty drafts are distinguished from renderer failures.

Regenerate the proof with:

```console
make configuration-proofs
```

The checked-in files are evidence, not the test oracle. Tests regenerate Mermaid source through the public
`Application` boundary, render it with the pinned browser-backed CLI, reject Mermaid error placeholders, and inspect
the resulting SVG.
