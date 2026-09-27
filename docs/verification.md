# Verification evidence

The repository separates package validation, regression checks, trigger-corpus structure, and actual model behavior.

## Recorded checks

| Layer | Evidence | Interpretation |
| --- | --- | --- |
| Repository invariants | `scripts/validate.py` completes without errors | Metadata, local paths, links and selected release-hygiene rules agree |
| Regression tests | 12 passing tests, including one clean baseline | Eleven intentionally corrupted repository cases are rejected |
| Trigger corpus | 16 authored prompts: 8 trigger / 8 skip | The corpus is structurally checked; these are not 16 executed model evaluations |
| CI compatibility | Python 3.9 and 3.13 jobs | The same validation and regression suite runs on both configured interpreters |
| Model forward evaluation | Not run in this presentation update | No planning-quality or routing-accuracy score is claimed |

The source-addressed [JSON snapshot](assets/verification.json) lists individual passing test IDs, Python version, corpus counts, and SHA-256 hashes for the tested validator, tests and skill. The live [CI workflow](https://github.com/yuanjuju/project-planner/actions/workflows/validate.yml) remains the source for each commit's remote result.

## Failure injection matrix

| Injected change | Expected rejection |
| --- | --- |
| Manifest version differs from `VERSION` | Version mismatch |
| Marketplace source points outside the repository | Root escape |
| README refers to a missing document | Broken local link |
| Release text contains an unresolved marker | Placeholder detection |
| JSON repeats a key | Duplicate object key |
| Documentation contains a machine-specific user path | Non-portable path |
| A release file is a symlink | Symlink prohibition |
| Trigger cases reuse an ID | Duplicate corpus ID |
| All negative trigger examples are removed | Missing negative coverage |
| Skill frontmatter repeats a metadata key | Duplicate frontmatter |
| UI invocation policy is removed | Missing UI policy |

Each regression mutates a temporary copy. The working repository is not modified by these cases. This is a hand-authored mutation-style suite, not an exhaustive mutation-testing score.

## Reproduce

```bash
make check
python3 scripts/build_evidence.py
```

The second command reruns validation and tests, then writes the JSON snapshot only after success. It does not call a model or network service. Use the [forward-evaluation protocol](evaluation.md) before changing or making claims about planning behavior.
