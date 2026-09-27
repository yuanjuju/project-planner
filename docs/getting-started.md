# Installation and usage

## Install as a plugin

Add this repository as a Codex marketplace, then install the plugin:

```bash
codex plugin marketplace add yuanjuju/project-planner --ref v1.0.0
codex plugin add project-planner@project-planner
```

Use `--ref main` instead of the version tag to track the latest unreleased changes.

If your Codex version does not yet expose plugin commands, use the standalone-skill method below.

## Install only the skill

Ask Codex to install the skill from this repository:

```text
Use $skill-installer to install the project-planner skill from
https://github.com/yuanjuju/project-planner/tree/main/plugins/project-planner/skills/project-planner
```

For a first-time manual user-level installation:

```bash
git clone https://github.com/yuanjuju/project-planner.git
mkdir -p "$HOME/.agents/skills"
cp -R project-planner/plugins/project-planner/skills/project-planner "$HOME/.agents/skills/project-planner"
```

On Windows PowerShell:

```powershell
git clone https://github.com/yuanjuju/project-planner.git
New-Item -ItemType Directory -Force "$HOME/.agents/skills" | Out-Null
Copy-Item -Recurse project-planner/plugins/project-planner/skills/project-planner "$HOME/.agents/skills/project-planner"
```

Codex normally detects skill changes automatically. Restart Codex if the skill does not appear.

For upgrades, prefer the plugin command or `$skill-installer`; a recursive manual copy can retain stale files from an older version.

## Usage

Invoke the skill explicitly:

```text
Use $project-planner to plan a privacy-first expense tracker for iOS.
```

For an existing repository:

```text
Use $project-planner to inspect this codebase, preserve its conventions,
and create a phased plan for adding team workspaces.
```

Useful details to provide include the target platform, constraints, preferred stack, core flows, and non-goals. When details are missing, the planner records assumptions and only asks questions that materially change the plan.

Because the skill writes durable planning files, use it in a version-controlled repository and review the resulting diff before implementation. It reads only the project content placed in scope and does not run the planned product code.


[Back to overview](../README.md) · [Architecture](architecture.md)
