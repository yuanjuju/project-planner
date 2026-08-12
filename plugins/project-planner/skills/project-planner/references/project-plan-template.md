# Project plan template

Use this as a menu, not a mandatory form. Omit inapplicable sections and preserve an existing project's terminology.

````markdown
# <Project name> plan

## Overview

What is being built, for whom, and why.

## Goals and non-goals

### Goals
- Outcome with a measurable or observable definition of success.

### Non-goals
- Explicitly excluded capability or concern.

## Users and core flows

| User or system | Core flow | Expected outcome |
|---|---|---|
| ... | ... | ... |

## Assumptions and open questions

### Confirmed assumptions
- Assumption and its source.

### Open questions
- Question, owner if known, and what decision it blocks.

## Existing-system constraints

For a brownfield project, summarize relevant architecture, conventions, compatibility constraints, and known debt. Omit for a greenfield project.

## Architecture

Use the smallest useful diagram. Adapt the components to the project rather than forcing a client/server shape.

```text
[Component] --> [Component] --> [External dependency]
      |               |
      +----------> [Storage]
```

### Technical decisions

| Decision | Choice or proposal | Rationale | Status |
|---|---|---|---|
| ... | ... | ... | Confirmed / Proposed / Open |

## Data and contracts

Document only applicable shapes: relational tables, collections, messages, configuration, domain entities, or library interfaces. Short examples are preferable to speculative exhaustive schemas.

## Service and API conventions

| Operation | Input | Output | Failure behavior |
|---|---|---|---|
| ... | ... | ... | ... |

Omit when the project has no service or API boundary.

## Cross-cutting concerns

Address applicable concerns such as security, privacy, accessibility, localization, performance, observability, deployment, migration, backup, and rollback.

## Proposed repository structure

Mark paths as proposed when they do not yet exist.

```text
project/
├── PROJECT_PLAN.md
├── specs/
└── ...
```

## Delivery phases

| Phase | Name | Dependencies | Deliverable | Verification |
|---|---|---|---|---|
| 01 | ... | None | ... | ... |

## Verification strategy

Describe the project-wide testing layers, quality gates, and evidence required for release.

## Risks

| Risk | Impact | Mitigation or experiment |
|---|---|---|
| ... | ... | ... |
````

## Quality checks

- Every declared goal maps to a phase or is intentionally deferred.
- The architecture matches known repository facts.
- Decisions and assumptions are labeled separately.
- Phase dependencies form an acyclic graph.
- The plan records material unresolved questions instead of guessing.
