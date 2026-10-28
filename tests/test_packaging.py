"""Regression checks for public-artifact boundaries and reproducibility."""

import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from sync_skills import collect, sync, EXPECTED_SKILLS
from validate import validate, validate_installable
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
            self.assertIn(".claude-plugin/icon.png", archive.namelist())
            self.assertEqual(len([name for name in archive.namelist() if name.endswith("SKILL.md")]), 3)

    def test_modified_or_extra_vendored_skill_fails(self):
        self.commit_source()
        sync(self.source, self.destination)
        skill = next((self.destination / "skills").rglob("SKILL.md"))
        skill.write_text(skill.read_text() + "Modified after sync\n")
        with self.assertRaisesRegex(ValueError, "differ from source lock"):
            validate(self.destination)

    def test_generated_directory_contains_only_runtime_payload_and_exact_copies(self):
        self.commit_source()
        sync(self.source, self.destination)
        build(self.destination)
        generated = self.destination / "plugin"
        validate_installable(self.destination)
        self.assertFalse((generated / "scripts").exists())
        self.assertFalse((generated / "tests").exists())
        self.assertFalse((generated / ".github").exists())
        self.assertFalse((generated / "AGENTS.md").exists())
        (generated / "unexpected.py").write_text("Never execute developer code")
        with self.assertRaisesRegex(ValueError, "payload differs"):
            validate_installable(self.destination)
        (generated / "unexpected.py").unlink()
        (generated / "README.md").write_text("Stale generated document")
        with self.assertRaisesRegex(ValueError, "payload differs"):
            validate_installable(self.destination)

    def test_symlinked_build_output_is_refused(self):
        self.commit_source()
        sync(self.source, self.destination)
        outside = self.base / "output-target"
        outside.mkdir()
        (self.destination / "dist").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "outputs must not be symlinks"):
            build(self.destination)
        self.assertEqual(list(outside.iterdir()), [])

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

    def test_overlapping_repositories_never_replace_canonical_source(self):
        nested = self.destination / "skills" / "canonical"
        shutil.copytree(self.source, nested)
        original = {p.relative_to(nested): p.read_bytes() for p in nested.rglob("*") if p.is_file()}
        for source, destination in ((nested, self.destination), (self.source, self.source), (self.base, self.destination)):
            with self.subTest(source=source, destination=destination):
                with self.assertRaisesRegex(ValueError, "separate repositories"):
                    sync(source, destination, allow_uncommitted=True)
        self.assertEqual(original, {p.relative_to(nested): p.read_bytes() for p in nested.rglob("*") if p.is_file()})

    def test_symlinked_manifest_parent_is_rejected(self):
        self.commit_source()
        sync(self.source, self.destination)
        outside = self.base / "external-manifest"
        shutil.move(str(self.destination / ".claude-plugin"), outside)
        (self.destination / ".claude-plugin").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "escapes its root|symlink"):
            validate(self.destination)

    def test_internal_manifest_parent_symlink_is_rejected(self):
        self.commit_source()
        sync(self.source, self.destination)
        shutil.move(str(self.destination / ".claude-plugin"), self.destination / "hidden-manifest")
        (self.destination / ".claude-plugin").symlink_to("hidden-manifest", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            validate(self.destination)

    def test_listing_icon_dimensions_and_privacy_policy_are_required(self):
        self.commit_source()
        sync(self.source, self.destination)
        icon_path = self.destination / ".claude-plugin/icon.png"
        original_icon = icon_path.read_bytes()
        icon_path.write_bytes(original_icon[:16] + struct.pack(">II", 500, 500) + original_icon[24:])
        with self.assertRaisesRegex(ValueError, "512 to 2048"):
            validate(self.destination)
        icon_path.write_bytes(original_icon)
        manifest_path = self.destination / ".claude-plugin/plugin.json"
        manifest = json.loads(manifest_path.read_text())
        del manifest["privacyPolicyUrl"]
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "privacy policy URL"):
            validate(self.destination)

    def test_mcp_headers_or_destination_changes_refused(self):
        self.commit_source()
        sync(self.source, self.destination)
        config = json.loads((self.destination / ".mcp.json").read_text())
        config["mcpServers"]["wisepim"]["headers"] = {"Authorization": "synthetic"}
        (self.destination / ".mcp.json").write_text(json.dumps(config))
        with self.assertRaisesRegex(ValueError, "embedded headers"):
            validate(self.destination)
