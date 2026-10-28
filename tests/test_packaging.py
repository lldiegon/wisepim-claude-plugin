"""Regression checks for public-artifact boundaries and reproducibility."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from sync_skills import collect, sync, EXPECTED_SKILLS
from validate import validate
from build import build

REPO = SCRIPTS.parent


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        self.source.mkdir()
        for name in EXPECTED_SKILLS:
            folder = self.source / "skills" / name
            folder.mkdir(parents=True)
            (folder / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Test workflow.\n---\nSynthetic data only.\n")
        self.destination = self.base / "plugin"
        self.destination.mkdir()
        for name in (".claude-plugin", "submission"):
            shutil.copytree(REPO / name, self.destination / name)
        for name in (".mcp.json", "README.md", "LICENSE"):
            shutil.copyfile(REPO / name, self.destination / name)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.source), *args], capture_output=True, text=True, check=True).stdout

    def commit_source(self):
        self.git("init", "-q")
        self.git("add", "skills")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "Synthetic fixture")

    def test_release_requires_committed_source(self):
        with self.assertRaisesRegex(ValueError, "clean reviewed Git commit"):
            sync(self.source, self.destination)
        sync(self.source, self.destination, allow_uncommitted=True)
        validate(self.destination, preview=True)
        with self.assertRaisesRegex(ValueError, "clean canonical Git commit"):
            validate(self.destination)

    def test_reproducible_archive_excludes_private_files(self):
        self.commit_source()
        sync(self.source, self.destination)
        (self.destination / ".env").write_text("PRIVATE_SYNTHETIC_SENTINEL=not-a-real-secret")
        first = build(self.destination)
        digest = hashlib.sha256(first.read_bytes()).hexdigest()
        self.assertEqual(digest, hashlib.sha256(build(self.destination).read_bytes()).hexdigest())
        with ZipFile(first) as archive:
            self.assertNotIn(".env", archive.namelist())
            self.assertFalse(any(name.startswith("scripts/") for name in archive.namelist()))
            self.assertIn(".claude-plugin/plugin.json", archive.namelist())
            self.assertEqual(len([name for name in archive.namelist() if name.endswith("SKILL.md")]), 3)

    def test_modified_or_extra_vendored_skill_fails(self):
        self.commit_source()
        sync(self.source, self.destination)
        skill = next((self.destination / "skills").rglob("SKILL.md"))
        skill.write_text(skill.read_text() + "Modified after sync\n")
        with self.assertRaisesRegex(ValueError, "differ from source lock"):
            validate(self.destination)

    def test_symlink_source_refused_before_replacing_vendor(self):
        self.commit_source()
        sync(self.source, self.destination)
        existing_lock = (self.destination / "skills.lock.json").read_bytes()
        (self.source / "skills" / "linked.md").symlink_to(self.source / "skills" / next(iter(EXPECTED_SKILLS)) / "SKILL.md")
        with self.assertRaisesRegex(ValueError, "Symlinks"):
            sync(self.source, self.destination)
        self.assertEqual(existing_lock, (self.destination / "skills.lock.json").read_bytes())

    def test_arbitrary_script_in_source_refused(self):
        (self.source / "skills" / next(iter(EXPECTED_SKILLS)) / "surprise.py").write_text("raise RuntimeError('never execute')")
        with self.assertRaisesRegex(ValueError, "Unsupported skill file"):
            collect(self.source)

    def test_ignored_source_file_cannot_hide_outside_commit(self):
        self.commit_source()
        (self.source / ".git" / "info" / "exclude").write_text("hidden.md\n")
        (self.source / "skills" / next(iter(EXPECTED_SKILLS)) / "hidden.md").write_text("Ignored synthetic file")
        with self.assertRaisesRegex(ValueError, "not present verbatim"):
            sync(self.source, self.destination)

    def test_mcp_headers_or_destination_changes_refused(self):
        self.commit_source()
        sync(self.source, self.destination)
        config = json.loads((self.destination / ".mcp.json").read_text())
        config["mcpServers"]["wisepim"]["headers"] = {"Authorization": "synthetic"}
        (self.destination / ".mcp.json").write_text(json.dumps(config))
        with self.assertRaisesRegex(ValueError, "embedded headers"):
            validate(self.destination)
