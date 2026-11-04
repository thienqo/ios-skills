import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / ".github" / "scripts" / "build_claude_directory.py"


class ClaudeDirectoryBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.out = Path(cls.temporary.name) / "plugin"
        cls.result = subprocess.run(
            [sys.executable, str(BUILDER), "--out", str(cls.out)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_build_passes_checks(self) -> None:
        self.assertEqual(self.result.returncode, 0, msg=self.result.stderr)

    def test_root_holds_only_the_plugin(self) -> None:
        entries = {path.name for path in self.out.iterdir()}
        self.assertEqual(entries, {".claude-plugin", "LICENSE", "README.md", "skills"})

    def test_icon_is_at_the_default_listing_path(self) -> None:
        icon = (self.out / ".claude-plugin" / "icon.png").read_bytes()
        self.assertEqual(icon[:8], b"\x89PNG\r\n\x1a\n")

    def test_every_skill_is_included_without_evals(self) -> None:
        source = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
        built = {path.parent.name for path in (self.out / "skills").glob("*/SKILL.md")}
        self.assertEqual(built, source)
        self.assertEqual(list(self.out.rglob("evals")), [])

    def test_manifest_tracks_package_version_and_skill_count(self) -> None:
        manifest = json.loads((self.out / ".claude-plugin" / "plugin.json").read_text())
        package = json.loads((ROOT / "package.json").read_text())
        skill_count = len(list((ROOT / "skills").glob("*/SKILL.md")))
        self.assertEqual(manifest["version"], package["version"])
        self.assertIn(f"{skill_count} skills", manifest["description"])


if __name__ == "__main__":
    unittest.main()
