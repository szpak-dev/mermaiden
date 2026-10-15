# Command-line interface

Mermaiden exposes one command-line operation:

```sh
python -m mermaiden.cli compat
```

`compat` compares Mermaiden's registered diagram configuration models with the checked-in Mermaid configuration
schema. It prints each implemented diagram as `valid` or `invalid`, reports schema definitions that do not have an
implementation, and exits unsuccessfully when the complete compatibility report is invalid.

The command reads the Mermaid version and schema pinned by the package. It does not render SVG or modify repository
files.
