# Baseline and Changed-only Audits

Create a baseline:

```bash
repoverity baseline create . --output .trust-baseline.json
```

Audit later state:

```bash
repoverity audit . --baseline .trust-baseline.json --fail-on high
```

Fingerprints are built from rule ID, repository-relative path and semantic anchors, not raw line numbers. Inserting unrelated lines therefore does not normally convert an existing finding into a new one. A file rename changes the path component and is intentionally treated as a new/resolved pair in v0.1.

Duplicate fingerprints and unsupported baseline schema versions are rejected rather than silently normalized.

`--changed-only BASE_REF` unions the committed `BASE_REF...HEAD` delta, staged/unstaged changes relative to HEAD and untracked files. Deleted files cannot produce current static findings. If the base ref is missing or the target is not a Git repository, RepoVerity emits a warning and runs a full audit rather than silently returning an empty result.
