---
paths:
  - "data/**"
  - "src/store/**"
---

## Data and storage

- `data/` holds input and runtime data. Code never lives in `data/`, and data never lives in `src/`.
- Raw input is read-only. Never modify or overwrite an input file. Generated output goes to a
  separate folder under `data/`, and a script can regenerate it. Caches are disposable.
- Exactly one module reads and writes each data store or file format. It parses and validates at
  that boundary and hands typed objects to the rest of the code. No other module parses raw fields.
- The data folder and file paths come from config. Tests use temporary folders.
- Document the data model in `docs/design.md`, and update it in the same change that changes the
  data.
- Use UUID strings for IDs and ISO 8601 UTC strings for timestamps.
- Before a change rewrites stored data in place (a migration, an import), copy the data to
  `<name>.before-<change>`. Never delete these backups.
