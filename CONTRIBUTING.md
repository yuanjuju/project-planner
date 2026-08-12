# Contributing

Thank you for helping improve Project Planner.

## Before opening a pull request

- Keep the skill limited to project planning and phased specifications.
- Prefer technology-neutral guidance; put ecosystem-specific material in an explicitly routed reference.
- Do not add product implementation code or runtime dependencies without first discussing the change in an issue.
- Keep user-authored files safe: new instructions must never encourage silent overwrites.
- Update the plugin version when behavior changes.

Run the validators from a checkout that also has Codex's built-in creator tools available:

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py \
  plugins/project-planner/skills/project-planner
python3 /path/to/plugin-creator/scripts/validate_plugin.py \
  plugins/project-planner
```

Also try at least one greenfield prompt, one existing-repository prompt, and one prompt that should not trigger the skill.
