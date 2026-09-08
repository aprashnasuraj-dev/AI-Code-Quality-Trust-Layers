# Security Model

The analyzed repository is untrusted input.

## Guarantees enforced by the implementation
- Target Python files are read and parsed; they are not imported or executed.
- User modules are never imported for symbol verification.
- Symlinked source files/directories are not followed.
- Per-file, total-byte and Python-file count limits bound ordinary repository traversal.
- Git subprocesses use argument arrays, `shell=False`, read-only commands and a timeout.
- Shareable reporters use repository-relative locations; SARIF paths are URI-encoded.
- Core audits make no network request and emit no telemetry.

## Best-effort boundaries
Malformed encodings and syntax become analysis issues. Extremely pathological parser inputs may still consume CPython parser resources until the configured file-size limit is reached.

## Out of scope
Archive extraction, remote repository cloning, dependency installation, target test execution and sandboxing arbitrary user programs are not part of v0.1.
