#!/usr/bin/env python3
"""Validate Project Planner's release invariants with no third-party packages."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import unquote


PLUGIN_NAME = "project-planner"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
TEXT_SUFFIXES = {".md", ".json", ".py", ".yaml", ".yml", ".txt"}
TEXT_NAMES = {".gitignore", "Makefile", "VERSION"}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})"),
    "OpenAI-style token": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}
LOCAL_PATH_PATTERNS = {
    "macOS user path": re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    "Linux user path": re.compile(r"/home/[A-Za-z0-9._-]+/"),
    "Windows user path": re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\"),
}


class DuplicateKeyError(ValueError):
    """Raised when JSON repeats an object key."""


def reject_duplicate_keys(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate object key {key!r}")
        result[key] = value
    return result


def read_json(path: Path, errors: List[str]) -> Optional[Any]:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
        return None


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def resolve_inside(root: Path, raw_path: str, label: str, errors: List[str]) -> Optional[Path]:
    candidate = (root / raw_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        errors.append(f"{label}: path escapes repository root: {raw_path}")
        return None
    return candidate


def parse_frontmatter(path: Path, errors: List[str]) -> Dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        errors.append(f"{path}: cannot read frontmatter: {exc}")
        return {}

    if not lines or lines[0] != "---":
        errors.append(f"{path}: missing opening YAML frontmatter delimiter")
        return {}
    try:
        closing = lines.index("---", 1)
    except ValueError:
        errors.append(f"{path}: missing closing YAML frontmatter delimiter")
        return {}

    values: Dict[str, str] = {}
    for number, line in enumerate(lines[1:closing], start=2):
        if not line.strip():
            continue
        if line.startswith((" ", "\t")) or ":" not in line:
            errors.append(f"{path}:{number}: unsupported frontmatter syntax")
            continue
        key, raw_value = line.split(":", 1)
        key, raw_value = key.strip(), raw_value.strip()
        if key in values:
            errors.append(f"{path}:{number}: duplicate frontmatter key {key!r}")
            continue
        if raw_value.startswith('"'):
            try:
                value = json.loads(raw_value)
            except json.JSONDecodeError as exc:
                errors.append(f"{path}:{number}: invalid quoted value: {exc}")
                continue
        elif raw_value.startswith("'") and raw_value.endswith("'"):
            value = raw_value[1:-1].replace("''", "'")
        else:
            value = raw_value
        if not isinstance(value, str):
            errors.append(f"{path}:{number}: frontmatter value must be text")
            continue
        values[key] = value
    return values


def validate_marketplace(root: Path, plugin_dir: Path, errors: List[str]) -> None:
    path = root / "marketplace.json"
    data = read_json(path, errors)
    if not isinstance(data, dict):
        return
    if data.get("name") != PLUGIN_NAME:
        errors.append(f"{path}: marketplace name must be {PLUGIN_NAME!r}")
    interface = data.get("interface")
    if not isinstance(interface, dict) or not interface.get("displayName"):
        errors.append(f"{path}: interface.displayName is required")
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        errors.append(f"{path}: plugins must be an array")
        return
    entry = next((item for item in plugins if isinstance(item, dict) and item.get("name") == PLUGIN_NAME), None)
    if entry is None:
        errors.append(f"{path}: missing {PLUGIN_NAME!r} plugin entry")
        return
    source = entry.get("source")
    if not isinstance(source, dict) or source.get("source") != "local":
        errors.append(f"{path}: plugin source must be local")
    else:
        raw_source = source.get("path")
        if not isinstance(raw_source, str):
            errors.append(f"{path}: plugin source.path must be text")
        else:
            resolved = resolve_inside(root, raw_source, f"{path}: source.path", errors)
            if resolved is not None and resolved != plugin_dir.resolve():
                errors.append(f"{path}: source.path must resolve to {relative(plugin_dir, root)}")
    policy = entry.get("policy")
    expected_policy = {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}
    if policy != expected_policy:
        errors.append(f"{path}: policy must be {expected_policy}")
    if not isinstance(entry.get("category"), str) or not entry["category"].strip():
        errors.append(f"{path}: category is required")
    else:
        manifest_path = plugin_dir / ".codex-plugin" / "plugin.json"
        manifest = read_json(manifest_path, errors)
        manifest_interface = manifest.get("interface") if isinstance(manifest, dict) else None
        manifest_category = manifest_interface.get("category") if isinstance(manifest_interface, dict) else None
        if manifest_category is not None and entry["category"] != manifest_category:
            errors.append(f"{path}: category must match plugin interface category {manifest_category!r}")


def validate_plugin(root: Path, plugin_dir: Path, version: str, errors: List[str]) -> None:
    path = plugin_dir / ".codex-plugin" / "plugin.json"
    data = read_json(path, errors)
    if not isinstance(data, dict):
        return
    if plugin_dir.name != PLUGIN_NAME or data.get("name") != PLUGIN_NAME:
        errors.append(f"{path}: folder and manifest name must both be {PLUGIN_NAME!r}")
    manifest_version = data.get("version")
    if manifest_version != version:
        errors.append(f"{path}: version {manifest_version!r} does not match VERSION {version!r}")
    if not isinstance(manifest_version, str) or not SEMVER.fullmatch(manifest_version):
        errors.append(f"{path}: version must be semantic version text")
    if data.get("license") != "MIT":
        errors.append(f"{path}: license must match repository MIT license")
    if not isinstance(data.get("description"), str) or not data["description"].strip():
        errors.append(f"{path}: description is required")
    author = data.get("author")
    if not isinstance(author, dict) or not author.get("name"):
        errors.append(f"{path}: author.name is required")
    skills_path = data.get("skills")
    if not isinstance(skills_path, str):
        errors.append(f"{path}: skills path is required")
    else:
        resolved = resolve_inside(plugin_dir, skills_path, f"{path}: skills", errors)
        if resolved is not None and not resolved.is_dir():
            errors.append(f"{path}: skills directory does not exist: {skills_path}")
    interface = data.get("interface")
    required_interface = {
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
        "capabilities",
        "defaultPrompt",
    }
    if not isinstance(interface, dict):
        errors.append(f"{path}: interface object is required")
    else:
        missing = sorted(required_interface - interface.keys())
        if missing:
            errors.append(f"{path}: missing interface keys: {', '.join(missing)}")


def validate_skill(skill_dir: Path, errors: List[str]) -> None:
    path = skill_dir / "SKILL.md"
    frontmatter = parse_frontmatter(path, errors)
    extra = sorted(set(frontmatter) - {"name", "description"})
    if extra:
        errors.append(f"{path}: unsupported frontmatter keys: {', '.join(extra)}")
    if frontmatter.get("name") != PLUGIN_NAME:
        errors.append(f"{path}: frontmatter name must be {PLUGIN_NAME!r}")
    description = frontmatter.get("description", "")
    if not description.strip():
        errors.append(f"{path}: frontmatter description is required")
    for phrase in ("PROJECT_PLAN.md", "specs/"):
        if phrase not in description:
            errors.append(f"{path}: description must mention {phrase!r}")
    try:
        line_count = len(path.read_text(encoding="utf-8").splitlines())
        if line_count > 500:
            errors.append(f"{path}: {line_count} lines exceeds the 500-line skill budget")
    except (OSError, UnicodeError):
        pass

    yaml_path = skill_dir / "agents" / "openai.yaml"
    try:
        yaml_text = yaml_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{yaml_path}: cannot read UI metadata: {exc}")
        return
    required_patterns = {
        "interface.display_name": r"(?m)^\s{2}display_name:\s*\S.+$",
        "interface.short_description": r"(?m)^\s{2}short_description:\s*\S.+$",
        "interface.default_prompt": r"(?m)^\s{2}default_prompt:\s*.*\$project-planner.+$",
        "policy.allow_implicit_invocation": r"(?m)^\s{2}allow_implicit_invocation:\s*(?:true|false)\s*$",
    }
    for label, pattern in required_patterns.items():
        if re.search(pattern, yaml_text) is None:
            errors.append(f"{yaml_path}: missing or invalid {label}")


def validate_trigger_cases(root: Path, errors: List[str]) -> None:
    path = root / "tests" / "trigger-cases.json"
    data = read_json(path, errors)
    if not isinstance(data, list):
        errors.append(f"{path}: root must be an array")
        return
    seen: Set[str] = set()
    counts = {"trigger": 0, "skip": 0}
    for index, case in enumerate(data):
        label = f"{path}: case {index + 1}"
        if not isinstance(case, dict):
            errors.append(f"{label} must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not re.fullmatch(r"[a-z0-9-]+", case_id):
            errors.append(f"{label} has an invalid id")
        elif case_id in seen:
            errors.append(f"{label} duplicates id {case_id!r}")
        else:
            seen.add(case_id)
        expected = case.get("expected")
        if expected not in counts:
            errors.append(f"{label} expected must be 'trigger' or 'skip'")
        else:
            counts[expected] += 1
        for key in ("prompt", "why"):
            if not isinstance(case.get(key), str) or not case[key].strip():
                errors.append(f"{label} requires non-empty {key}")
    for expected, count in counts.items():
        if count < 3:
            errors.append(f"{path}: requires at least three {expected!r} cases")


def iter_text_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.name == ".DS_Store":
            continue
        if path.suffix in TEXT_SUFFIXES or path.name in TEXT_NAMES:
            files.append(path)
    return sorted(files)


def validate_markdown_links(root: Path, files: List[Path], errors: List[str]) -> None:
    for path in (item for item in files if item.suffix == ".md"):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{path}: cannot read Markdown: {exc}")
            continue
        for match in MARKDOWN_LINK.finditer(text):
            raw_target = match.group(1).strip()
            if raw_target.startswith("<") and raw_target.endswith(">"):
                raw_target = raw_target[1:-1]
            target = raw_target.split(maxsplit=1)[0].split("#", 1)[0]
            if not target or target.startswith(("#", "http://", "https://", "mailto:", "codex://")):
                continue
            decoded = unquote(target)
            candidate = path.parent / decoded
            try:
                raw_relative = str(candidate.relative_to(root))
            except ValueError:
                errors.append(f"{path}: local link escapes repository root: {raw_target}")
                continue
            resolved = resolve_inside(root, raw_relative, f"{path}: link", errors)
            if resolved is not None and not resolved.exists():
                errors.append(f"{path}: broken local link: {raw_target}")


def validate_hygiene(root: Path, files: List[Path], errors: List[str]) -> None:
    placeholder = re.compile(r"\[(?:TODO|TBD)(?::[^\]]*)?\]", re.IGNORECASE)
    lowercase_agents = re.compile(r"(?<![A-Z])\bagents\.md\b")
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{path}: cannot read text: {exc}")
            continue
        display = relative(path, root)
        if placeholder.search(text):
            errors.append(f"{display}: contains an unresolved placeholder")
        if lowercase_agents.search(text):
            errors.append(f"{display}: use canonical AGENTS.md casing")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{display}: contains a possible {label}")
        for label, pattern in LOCAL_PATH_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{display}: contains a machine-specific {label}")
        for number, line in enumerate(text.splitlines(), start=1):
            if line.endswith((" ", "\t")):
                errors.append(f"{display}:{number}: trailing whitespace")


def validate_repository(root: Path) -> List[str]:
    root = root.resolve()
    errors: List[str] = []
    plugin_dir = root / "plugins" / PLUGIN_NAME
    skill_dir = plugin_dir / "skills" / PLUGIN_NAME
    required = [
        root / "VERSION",
        root / "LICENSE",
        root / "README.md",
        root / "CHANGELOG.md",
        root / "marketplace.json",
        plugin_dir / ".codex-plugin" / "plugin.json",
        skill_dir / "SKILL.md",
        skill_dir / "agents" / "openai.yaml",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing required file: {relative(path, root)}")

    for path in root.rglob("*"):
        if ".git" not in path.parts and path.is_symlink():
            errors.append(f"{relative(path, root)}: repository release files must not be symlinks")

    version = ""
    version_path = root / "VERSION"
    if version_path.is_file():
        version = version_path.read_text(encoding="utf-8").strip()
        if not SEMVER.fullmatch(version):
            errors.append("VERSION must contain one semantic version")

    validate_marketplace(root, plugin_dir, errors)
    validate_plugin(root, plugin_dir, version, errors)
    validate_skill(skill_dir, errors)
    validate_trigger_cases(root, errors)
    files = iter_text_files(root)
    validate_markdown_links(root, files, errors)
    validate_hygiene(root, files, errors)
    return sorted(set(errors))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    errors = validate_repository(args.root)
    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"OK: package invariants hold for {args.root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
