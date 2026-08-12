# Evaluation strategy

Project Planner uses three complementary quality layers. The distinction is
intentional: package structure is deterministic, while language-model behavior
is not.

## 1. Deterministic package checks

`python scripts/validate.py` verifies invariants that should never depend on a
model response:

- plugin, marketplace, skill, and version metadata agree;
- referenced plugin and skill paths stay inside the repository;
- required skill metadata and UI metadata exist;
- local Markdown links resolve;
- release files contain no placeholders, machine-specific paths, or common
  secret formats;
- the trigger-case corpus is structurally valid and contains positive and
  negative cases.

The validator uses only the Python standard library so contributors and CI run
the same checks without a dependency bootstrap.

## 2. Trigger-boundary contract

[`tests/trigger-cases.json`](../tests/trigger-cases.json) records prompts that
should and should not activate the skill. CI validates the corpus itself; it
does not pretend that a lexical script can prove a model-routing decision.

When changing the skill description, replay these cases with a fresh Codex
task and record any intentional expectation change in the pull request.

## 3. Forward evaluations

Before a behavior release, test the skill in fresh tasks with no leaked target
answer:

| Scenario | Minimum assertion |
|---|---|
| Greenfield | Produces a scoped plan, a valid phase DAG, and no product code |
| Existing repository | Inspects real files, preserves conventions, and does not silently overwrite |
| Negative trigger | Answers normally without creating planning artifacts |
| Ambiguous requirements | Labels assumptions and asks only material questions |

Review generated artifacts for requirement coverage, verified versus proposed
paths, testable acceptance criteria, dependency correctness, and a clear
implementation handoff.

## Release gate

A release is ready when:

1. `make check` passes;
2. the built-in Codex skill and plugin validators pass when available;
3. the trigger-boundary cases have no unexplained regressions;
4. at least one greenfield and one existing-repository forward evaluation pass;
5. `VERSION`, the plugin manifest, and the changelog describe the same release.
