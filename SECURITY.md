# Security Policy

RepoVerity is a static analyzer for untrusted repositories. Please report vulnerabilities privately through GitHub Security Advisories after the repository is published rather than opening a public exploit issue.

Supported line: `0.1.x` during the initial alpha. Security-sensitive invariants include: never executing/importing target code, no core network/source upload, no symlink traversal, no shell interpolation of target filenames, and no default source mutation.

See [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md) for the threat model and residual risks.
