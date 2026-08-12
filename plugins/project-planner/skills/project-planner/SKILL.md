---
name: project-planner
description: "Create or update durable project-planning documents for a software project: a repository-level PROJECT_PLAN.md plus phased specifications under specs/. Use when the user explicitly asks to plan, scope, architect, decompose, or write implementation specifications for a project before coding. Do not use for a quick verbal outline, ordinary task tracking, or when the user asks to implement code without requesting planning artifacts."
---

# Project Planner

Turn a project idea or an existing codebase into reviewable planning artifacts. Produce planning and specifications only; do not implement the project in the same task unless the user separately asks for implementation.

Match the user's language. Keep filenames and identifiers portable unless the repository already uses another convention.

## Workflow

### 1. Establish scope

- Locate the project root. Use the current repository when the user does not name another destination.
- Inspect existing instructions, manifests, documentation, source layout, and `specs/` before proposing architecture.
- Identify goals, users, core flows, platform, constraints, dependencies, non-goals, and success criteria.
- Ask only questions whose answers would materially change the plan. Otherwise record the assumption and continue.
- For a new project, distinguish user requirements from inferred defaults.
- For an existing project, preserve established architecture and conventions unless the user explicitly requests a redesign.

### 2. Plan the artifacts

Create or update:

```text
<project-root>/
├── PROJECT_PLAN.md
└── specs/
    ├── 01-<phase-name>.md
    ├── 02-<phase-name>.md
    └── ...
```

Use `PROJECT_PLAN.md` for the durable project blueprint. Do not create or replace `AGENTS.md` with architecture content: Codex loads `AGENTS.md` as working instructions on every run. If the user requests agent instructions, keep `AGENTS.md` concise and point it to the plan and relevant specs.

Before changing an existing planning file:

- Read it completely.
- Preserve useful user-authored content and naming.
- Merge changes deliberately; never silently overwrite it.
- Call out contradictions or obsolete decisions.

Read [references/project-plan-template.md](references/project-plan-template.md) when drafting or substantially revising `PROJECT_PLAN.md`. Read [references/phase-spec-template.md](references/phase-spec-template.md) when drafting phase files.

### 3. Write `PROJECT_PLAN.md`

Cover, as applicable:

- overview, users, value, and core flows;
- goals, non-goals, assumptions, and open questions;
- current-state constraints for an existing project;
- architecture and key technical decisions;
- data model or interface shapes;
- service or API contracts;
- security, privacy, accessibility, observability, migration, and rollback concerns;
- expected repository structure;
- phase dependency graph and deliverables;
- project-wide verification strategy and risks.

Adapt sections to the project. A CLI may have no client/server diagram; a library may have no database; an infrastructure project may need deployment topology instead of UI state.

### 4. Write phase specifications

- Create one focused file per independently reviewable phase.
- Default to 3-6 phases, roughly 100-180 lines for `PROJECT_PLAN.md`, and 50-90 lines per phase. Use fewer or shorter artifacts for small projects; exceed these ranges only when complexity or the user warrants it.
- Number files in dependency order with two digits.
- Model dependencies as a directed acyclic graph; do not force every phase into a linear chain.
- Include concrete files or modules when they can be inferred reliably. Mark proposed paths as proposed.
- Define failure modes, operational states, or user-interface states only when relevant.
- Make acceptance criteria observable and testable.
- Include testing and rollout work in the phase that owns it; create a separate integration phase only when it adds real value.
- Avoid full implementation code. Use short schemas, signatures, protocols, or pseudocode only when they remove ambiguity.

### 5. Validate and hand off

- Check that every requirement maps to a phase or is explicitly out of scope.
- Check that dependencies are acyclic and that phase outputs satisfy downstream inputs.
- Check filenames, terminology, contracts, and acceptance criteria for consistency.
- Summarize created or updated files, assumptions, open decisions, and the recommended first phase.
- Stop after the planning artifacts. Offer implementation as a separate next task.

## Output rules

- Keep the plan implementation-ready but technology-neutral when the stack is undecided.
- Prefer explicit tradeoffs over unsupported certainty.
- Separate confirmed facts, decisions, assumptions, and open questions.
- Never invent existing repository files or capabilities; verify them first.
- Do not add dependencies, initialize frameworks, or write product code while using this skill.
