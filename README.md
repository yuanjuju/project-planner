# Project Planner for Codex

An open-source Codex plugin and standalone skill that turns a software-project idea or an existing repository into a durable `PROJECT_PLAN.md` and implementation-ready phase specifications under `specs/`.

It plans; it does not implement product code.

## What it produces

```text
your-project/
├── PROJECT_PLAN.md
└── specs/
    ├── 01-project-foundation.md
    ├── 02-core-capability.md
    └── ...
```

The planner adapts the sections to the project instead of assuming every project has a browser client, server, and database. It also inspects existing repositories before writing and does not silently replace existing planning documents.

## Install as a plugin

Add this repository as a Codex marketplace, then install the plugin:

```bash
codex plugin marketplace add yuanjuju/project-planner --ref main
codex plugin add project-planner@project-planner
```

If your Codex version does not yet expose plugin commands, use the standalone-skill method below.

## Install only the skill

Ask Codex to install the skill from this repository:

```text
Use $skill-installer to install the project-planner skill from
https://github.com/yuanjuju/project-planner/tree/main/plugins/project-planner/skills/project-planner
```

For manual user-level installation:

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

## Design choices

- `PROJECT_PLAN.md` stores architecture and delivery planning.
- `AGENTS.md` remains a concise Codex instruction file rather than a project-design dump.
- Phase dependencies may form a directed acyclic graph instead of an artificial linear sequence.
- Sections such as databases, APIs, UI states, migrations, and observability are included only when relevant.
- Existing files are read and merged deliberately; they are not silently overwritten.

## Repository layout

```text
.
├── marketplace.json
└── plugins/project-planner/
    ├── .codex-plugin/plugin.json
    └── skills/project-planner/
        ├── SKILL.md
        ├── agents/openai.yaml
        └── references/
```

## Privacy and dependencies

This plugin contains instructions and Markdown templates only. It has no runtime dependencies, telemetry, network service, or credential requirements. Codex may read and write planning files in the repository the user places in scope.

## Contributing

Issues and pull requests are welcome. Keep the skill focused on planning artifacts, preserve technology-neutral defaults, and validate both the skill and plugin structure before submitting changes.

## License

[MIT](LICENSE)

This is an unofficial community project and is not affiliated with or endorsed by OpenAI.
