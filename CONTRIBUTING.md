# Contributing

Thank you for helping improve Project Planner.

## Before opening a pull request

- Keep the skill limited to project planning and phased specifications.
- Prefer technology-neutral guidance; put ecosystem-specific material in an explicitly routed reference.
- Do not add product implementation code or runtime dependencies without first discussing the change in an issue.
- Keep user-authored files safe: new instructions must never encourage silent overwrites.
- Update the plugin version when behavior changes.

Run the repository's dependency-free quality gates:

```bash
make check
```

When Codex's built-in creator tools are available, also cross-check the package with `quick_validate.py` from `skill-creator` and `validate_plugin.py` from `plugin-creator`.

## Behavior changes

For changes to triggering, workflow, templates, or output rules:

1. Update [`tests/trigger-cases.json`](tests/trigger-cases.json) when a trigger boundary intentionally changes.
2. Replay the relevant cases in a fresh Codex task.
3. Try at least one greenfield prompt and one existing-repository prompt.
4. Confirm the skill creates planning artifacts only and preserves existing user content.
5. Update `VERSION` and `CHANGELOG.md` for a release-worthy behavior change.

See [`docs/evaluation.md`](docs/evaluation.md) for the full evaluation protocol.

## Pull requests

Keep commits focused and explain the planning failure mode the change addresses. Include the commands you ran and summarize forward-evaluation results. Do not include private repositories, generated credentials, or machine-specific paths in fixtures.
