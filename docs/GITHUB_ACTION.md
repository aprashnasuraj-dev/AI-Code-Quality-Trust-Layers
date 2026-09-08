# GitHub Action

Before the first release tag, development workflows can use:

```yaml
- uses: aprashnasuraj-dev/AI-Code-Quality-Trust-Layers@main
  with:
    path: .
    fail-on: high
```

After v0.1.0 is released, pin a released tag or immutable commit. The Action is composite and source-direct: it prepends its own `src/` directory to `PYTHONPATH` and passes user inputs through an argument array. It requires no secret and does not install RepoVerity from a package index.

For SARIF, generate a file with `--format sarif --output repoverity.sarif`, then upload it in a job granted `security-events: write`. The repository's `repoverity-sarif.yml` exercises this on pushes to `main`; acceptance by GitHub is remote evidence, not something local tests can prove.
