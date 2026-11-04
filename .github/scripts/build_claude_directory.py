#!/usr/bin/env python3
"""Build the plugin folder submitted to Anthropic's directory.

The repository root cannot be submitted as it stands: a top-level `bin/` makes
claude.ai and Cowork refuse the plugin, `package.json` with a lockfile holds it
for review, `.mcp.json` would start a maintainer tool for users, and
`marketplace.json` lists several plugins. This script writes a clean plugin
folder from the tracked skills, and can commit it to a branch without touching
the working tree or the current checkout.

Checks follow https://claude.com/docs/plugins/pre-submission-checklist.md.

    build_claude_directory.py --out DIR
    build_claude_directory.py --branch claude-directory
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Permanent once published: users install and configure the plugin by this name.
PLUGIN_NAME = "thienqo-ios-skills"
DISPLAY_NAME = "thienqo iOS Skills"
REPOSITORY = "https://github.com/thienqo/ios-skills"

MAX_FILES = 512
MAX_FILE_BYTES = 256 * 1024
MIN_README_WORDS = 40
SYSTEM_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}
FORBIDDEN_ROOT_ENTRIES = {"bin", ".mcp.json", "package.json", "package-lock.json"}

# The directory takes a listing icon only once: the first time the plugin is saved or submitted.
ICON_SOURCE = ROOT / ".github" / "claude-directory" / "icon.png"
ICON_PATH = ".claude-plugin/icon.png"
MAX_ICON_BYTES = 2 * 1024 * 1024
ICON_SIDE_RANGE = range(512, 2049)

PRIVACY_SOURCE = ROOT / ".github" / "claude-directory" / "PRIVACY.md"
PRIVACY_URL = f"{REPOSITORY}/blob/claude-directory/PRIVACY.md"

README = """\
# {display_name}

{skill_count} Agent Skills for Swift, SwiftUI, and Apple-platform development, built
against Xcode 27, Swift 6.4, and the iOS 27 SDK, with a deployment floor of iOS
and iPadOS 26. Claude loads a skill when a task matches it, covering SwiftUI,
concurrency, data, testing, app frameworks, on-device AI, hardware, performance
diagnostics, and App Store delivery.

Skills are namespaced under the plugin, for example
`{name}:swiftui-navigation`.

## What this plugin runs and fetches

This plugin contains instructions and reference documents. It has no hooks, MCP
servers, agents, or background processes, and it collects no data.

- **Local scripts.** Two skills include Python scripts that run only when Claude
  uses them for that task, on your machine. `ios-ettrace-performance` calls
  `xcrun dwarfdump` to match dSYM files. `ios-memgraph-analysis` calls
  `xcrun simctl` and `leaks` to capture and summarize memory graphs. These
  scripts read and write local files and make no network requests.
- **Documentation links.** Skills link to Apple documentation through
  `sosumi.ai`, which serves it as Markdown, and to a few `developer.apple.com`
  pages. Claude may open these links when it needs more detail.
- **Third-party tools.** Some skills describe installing or using tools such as
  Homebrew packages. Those tools contact their own services if you choose to
  install or run them.

See `PRIVACY.md` for the privacy policy.

## Source and license

Source and issues: <{repository}>

Licensed under the PolyForm Perimeter License 1.0.0; see `LICENSE`. Based on
work by dpearson2699. The adapted `swift-code-review` skill keeps its Apache-2.0
attribution. Apple frameworks, documentation, and trademarks belong to Apple
Inc. This project is independent and not endorsed by Apple.
"""


def git(*args: str, env: dict[str, str] | None = None, cwd: Path = ROOT) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        env={**os.environ, **(env or {})},
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def tracked_skill_files() -> list[str]:
    """Tracked files users need. Evals are maintainer test data and stay out."""
    files = git("ls-files", "skills").splitlines()
    return [path for path in files if "/evals/" not in path]


def manifest(version: str, skill_count: int) -> dict[str, object]:
    return {
        "name": PLUGIN_NAME,
        "displayName": DISPLAY_NAME,
        "version": version,
        "description": (
            f"{skill_count} skills for Swift, SwiftUI, and Apple-platform development, "
            "built for Xcode 27, Swift 6.4, and the iOS 27 SDK."
        ),
        "author": {"name": "Thien Ngo", "url": "https://github.com/thienqo"},
        "homepage": REPOSITORY,
        "repository": REPOSITORY,
        "supportUrl": f"{REPOSITORY}/issues",
        "privacyPolicyUrl": PRIVACY_URL,
        "keywords": ["ios", "swift", "swiftui", "xcode", "apple"],
    }


def build(out: Path) -> None:
    files = tracked_skill_files()
    version = json.loads((ROOT / "package.json").read_text())["version"]
    skill_count = sum(1 for path in files if re.fullmatch(r"skills/[^/]+/SKILL\.md", path))

    for relative in files:
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    shutil.copyfile(ROOT / "LICENSE", out / "LICENSE")
    shutil.copyfile(PRIVACY_SOURCE, out / "PRIVACY.md")

    (out / ".claude-plugin").mkdir()
    shutil.copyfile(ICON_SOURCE, out / ICON_PATH)
    (out / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(manifest(version, skill_count), indent=2) + "\n"
    )
    (out / "README.md").write_text(
        README.format(
            display_name=DISPLAY_NAME,
            skill_count=skill_count,
            name=PLUGIN_NAME,
            repository=REPOSITORY,
        )
    )


def check_icon(icon: Path) -> list[str]:
    data = icon.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return [f"{ICON_PATH} is not a PNG"]
    problems: list[str] = []
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if width != height or width not in ICON_SIDE_RANGE:
        problems.append(f"{ICON_PATH} must be square, 512 to 2048 px, not {width}x{height}")
    if len(data) >= MAX_ICON_BYTES:
        problems.append(f"{ICON_PATH} must be under {MAX_ICON_BYTES} bytes")
    return problems


def check(out: Path) -> list[str]:
    problems: list[str] = check_icon(out / ICON_PATH)
    files = [path for path in out.rglob("*") if path.is_file() or path.is_symlink()]

    if len(files) > MAX_FILES:
        problems.append(f"{len(files)} files exceeds the limit of {MAX_FILES}")
    for entry in FORBIDDEN_ROOT_ENTRIES:
        if (out / entry).exists():
            problems.append(f"{entry} must not be in the plugin folder")

    for path in files:
        relative = path.relative_to(out)
        if path.is_symlink():
            problems.append(f"{relative} is a symbolic link")
            continue
        if relative.as_posix() == ICON_PATH:
            continue
        if path.name in SYSTEM_FILES or "__MACOSX" in relative.parts:
            problems.append(f"{relative} is a system file")
        if path.stat().st_size > MAX_FILE_BYTES:
            problems.append(f"{relative} is larger than {MAX_FILE_BYTES} bytes")
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append(f"{relative} is not a text file")

    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?", PLUGIN_NAME):
        problems.append(f"plugin name {PLUGIN_NAME!r} is invalid")

    readme = re.sub(r"```.*?```", "", (out / "README.md").read_text(), flags=re.S)
    if len(readme.split()) < MIN_README_WORDS:
        problems.append(f"README has fewer than {MIN_README_WORDS} words")

    skills = list((out / "skills").iterdir())
    for skill in skills:
        if not (skill / "SKILL.md").is_file():
            problems.append(f"{skill.relative_to(out)} has no SKILL.md")
    if not skills:
        problems.append("no skills were copied")
    return problems


def commit_to_branch(out: Path, branch: str) -> str:
    """Commit `out` as the whole tree of `branch`, leaving the checkout alone."""
    with tempfile.TemporaryDirectory() as index_dir:
        env = {
            "GIT_DIR": git("rev-parse", "--absolute-git-dir"),
            "GIT_INDEX_FILE": str(Path(index_dir) / "index"),
            "GIT_WORK_TREE": str(out),
        }
        git("add", "--all", "--force", ".", env=env, cwd=out)
        tree = git("write-tree", env=env, cwd=out)

    parent = None
    for ref in (f"refs/heads/{branch}", f"refs/remotes/origin/{branch}"):
        try:
            parent = git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
            break
        except RuntimeError:
            continue

    if parent and git("rev-parse", f"{parent}^{{tree}}") == tree:
        git("update-ref", f"refs/heads/{branch}", parent)
        return f"{branch} is already up to date at {parent[:7]}"

    source = git("rev-parse", "--short", "HEAD")
    arguments = ["commit-tree", tree, "-m", f"chore: build Claude directory plugin from {source}"]
    if parent:
        arguments += ["-p", parent]
    commit = git(*arguments)
    git("update-ref", f"refs/heads/{branch}", commit)
    return f"{branch} is now {commit[:7]}, built from {source}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--out", type=Path, help="empty or missing folder to write to")
    target.add_argument("--branch", help="branch to commit the plugin folder to")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as temporary:
        out = args.out.resolve() if args.out else Path(temporary) / "plugin"
        if out.exists() and any(out.iterdir()):
            parser.error(f"{out} is not empty")
        out.mkdir(parents=True, exist_ok=True)

        build(out)
        problems = check(out)
        if problems:
            print("\n".join(problems), file=sys.stderr)
            return 1

        file_count = sum(1 for path in out.rglob("*") if path.is_file())
        print(f"{PLUGIN_NAME}: {file_count} files passed the local checks")
        if args.branch:
            print(commit_to_branch(out, args.branch))
    return 0


if __name__ == "__main__":
    sys.exit(main())
