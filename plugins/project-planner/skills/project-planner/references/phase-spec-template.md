# Phase specification template

Use one file for one independently reviewable delivery phase. Scale the detail to the work; omit sections that do not apply.

```markdown
# Phase XX: <Name>

## Outcome

State the user-visible or system-level result of this phase.

**Depends on:** Phase identifiers or `None`
**Produces:** Concrete artifacts or capabilities

## Scope

### In scope
- ...

### Out of scope
- ...

## Assumptions and decisions

- Confirmed decision, proposed decision, or assumption with its consequence.

## Tasks

### X.1 <Task name>

**Files or modules:** `path/to/file` (existing) or `path/to/file` (proposed)

Describe the behavior, relevant contracts, design constraints, and important edge cases. Avoid full implementation code.

### X.2 <Task name>

...

## Contracts and data changes

Document new or changed APIs, events, schemas, configuration, migrations, or public interfaces. State `None` when the absence matters to downstream phases.

## States and failure modes

| State or failure | Expected behavior | Recovery or fallback |
|---|---|---|
| ... | ... | ... |

Use UI states such as loading, empty, error, and success for interactive work. Use operational failure modes for services, CLIs, libraries, data pipelines, and infrastructure.

## Verification

- Automated checks and their scope.
- Manual or visual checks when required.
- Evidence to retain, such as test output, screenshots, or migration logs.

## Acceptance criteria

- [ ] Observable criterion tied to a requirement.
- [ ] Negative or edge-case behavior is verified.
- [ ] Documentation, migration, or rollback work is complete when applicable.

## Risks and notes

- Phase-specific risk, follow-up, or production consideration.
```

## Quality checks

- Every task names an outcome, not merely an activity.
- Proposed paths are distinguishable from verified existing paths.
- Acceptance criteria can be evaluated without interpreting intent.
- Downstream phases can rely on the declared outputs.
- The specification does not duplicate implementation code.
