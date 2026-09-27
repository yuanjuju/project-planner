#!/usr/bin/env python3
"""Run package tests and export source-addressed evidence, using the standard library."""
from __future__ import annotations

import hashlib
import io
import json
import platform
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.validate import validate_repository  # noqa: E402


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed.append(test.id())


def main():
    errors = validate_repository(ROOT)
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, resultclass=RecordingResult).run(suite)
    sys.stderr.write(stream.getvalue())
    if errors or not result.wasSuccessful():
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    corpus = json.loads((ROOT / 'tests/trigger-cases.json').read_text(encoding='utf-8'))
    paths = [
        'scripts/validate.py', 'tests/test_validate.py', 'tests/trigger-cases.json',
        'plugins/project-planner/skills/project-planner/SKILL.md',
        'plugins/project-planner/skills/project-planner/agents/openai.yaml',
    ]
    evidence = {
        'scope': 'Deterministic repository checks; no model behavior evaluation performed.',
        'python': platform.python_version(),
        'package_validation_errors': errors,
        'tests_run': result.testsRun,
        'tests_passed': sorted(result.passed),
        'trigger_corpus_counts': dict(sorted(Counter(c['expected'] for c in corpus).items())),
        'model_forward_evaluation': 'not_run',
        'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths},
    }
    output = ROOT / 'docs/assets/verification.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Wrote docs/assets/verification.json')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
