"""Validate package structure and source integrity without contacting WisePIM."""

import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = {"catalog-quality-audit", "prepare-product-translations", "channel-readiness-review"}


def contained_file(root, name):
    """Reject symlinked files and parents before opening distributable content."""
    base = root.resolve()
    path = base / name
    if not path.resolve().is_relative_to(base):
        raise ValueError(f"Package path escapes its root: {name}")
    if not path.is_file():
        raise ValueError(f"Package file is missing: {name}")
    current = path
    while current != base:
        if current.is_symlink():
            raise ValueError(f"Package path contains a symlink: {name}")
        current = current.parent
    return path


def validate(root=ROOT, preview=False):
    root = root.resolve()
    for name in (".claude-plugin/plugin.json", ".mcp.json", "README.md", "LICENSE", "skills.lock.json"):
        contained_file(root, name)
    manifest = json.loads((root / ".claude-plugin/plugin.json").read_text())
    if manifest.get("name") != "wisepim" or not re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")):
        raise ValueError("Expected wisepim identity and explicit semantic version")
    if manifest.get("mcpServers") != "./.mcp.json":
        raise ValueError("Expected a contained MCP configuration path")
    if manifest.get("license") != "MIT" or not (root / "LICENSE").is_file():
        raise ValueError("Public package needs its MIT license")
    config = json.loads((root / ".mcp.json").read_text())
    if set(config) != {"mcpServers"} or set(config["mcpServers"]) != {"wisepim"}:
        raise ValueError("Exactly one declared WisePIM destination is allowed")
    server = config["mcpServers"]["wisepim"]
    if set(server) != {"type", "url"} or server["type"] != "http":
        raise ValueError("Remote OAuth-only HTTP transport required; no embedded headers or local execution")
    url = urlsplit(server["url"])
    if url.scheme != "https" or url.netloc != "wisepim.com" or url.path != "/mcp" or url.query or url.fragment:
        raise ValueError("MCP URL must exactly match the frontend resource audience https://wisepim.com/mcp")
    lock = json.loads((root / "skills.lock.json").read_text())
    if lock.get("formatVersion") != 1 or lock.get("repository") != "https://github.com/lldiegon/wisepim-skills":
        raise ValueError("Unrecognized canonical skills provenance")
    if not preview and (lock.get("sourceDirty") is not False or not re.fullmatch(r"[a-f0-9]{40,64}", lock.get("commit") or "")):
        raise ValueError("Release skills must come from a clean canonical Git commit")
    actual = {}
    found = set()
    for path in sorted((root / "skills").rglob("*")):
        if path.is_symlink():
            raise ValueError("Skill symlinks are forbidden")
        if not path.is_file():
            continue
        name = path.relative_to(root).as_posix()
        contained_file(root, name)
        actual[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        if path.name == "SKILL.md":
            skill = path.parent.name
            found.add(skill)
            body = path.read_text()
            if not body.startswith("---\n") or "\ndescription:" not in body.split("\n---", 1)[0]:
                raise ValueError(f"Missing skill frontmatter in {name}")
    if found != EXPECTED_SKILLS or actual != lock.get("files"):
        raise ValueError("Copied skills differ from source lock or expected skill set")
    if (root / "skills").is_symlink():
        raise ValueError("Root skills directory must not be a symlink")
    if any(key in manifest for key in ("hooks", "settings", "agents", "commands")):
        raise ValueError("Unexpected runtime component requires explicit review")
    if len((root / "README.md").read_text().split()) < 40:
        raise ValueError("Directory README is too short")
    return len(actual)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    try:
        count = validate(preview=args.preview)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"Validation failed: {exc}\n")
    print(f"Package structure and {count} locked skill files validated; live OAuth and directory review are separate gates")
