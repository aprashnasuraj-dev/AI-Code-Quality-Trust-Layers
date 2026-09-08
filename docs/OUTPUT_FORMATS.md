# Output Formats

`repoverity audit` supports `terminal`, `json`, `markdown`, and `sarif`.

## Terminal
Concise human summary. Color is used only for a TTY and is disabled by `--no-color` or `NO_COLOR`.

## JSON
Schema version `1.0`. Top-level keys include tool, repository, summary, findings, analysis issues, warnings, timing and resolved fingerprints. Paths are repository-relative.

## Markdown
A portable Code Trust Receipt plus category summary and finding evidence. Untrusted multiline finding text is flattened so it cannot inject report structure.

## SARIF
SARIF 2.1.0 with rule descriptors, severity mapping, relative URI-safe artifact locations and RepoVerity partial fingerprints. Local structural tests do not imply GitHub ingestion; hosted validation is tracked in the release audit.
