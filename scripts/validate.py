"""Validate package structure and source integrity without contacting WISEPIM."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = {
    'start-with-wisepim',
    'analyze-commerce-performance',
    'assess-product-images',
    'catalog-quality-audit',
    'channel-readiness-review',
    'clean-catalog-data',
    'enrich-from-research',
    'enrich-from-supplier-documents',
    'enrich-product-content',
    'manage-enrichment-prompts',
    'optimize-seo-performance',
    'organize-product-taxonomy',
    'prepare-product-translations',
    'prioritize-catalog-opportunities',
    'remediate-channel-issues',
    'research-product-facts',
    'run-catalog-improvement-jobs',
}


def payload_names(root):
    names = [".claude-plugin/plugin.json", ".claude-plugin/icon.png", ".mcp.json", "LICENSE", "README.md", "skills.lock.json"]
    names.extend(path.relative_to(root).as_posix() for path in (root / "skills").rglob("*") if path.is_file())
    return sorted(names)


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


def validate_installable(root=ROOT):
    """Require exact byte parity with the allowlisted runtime payload."""
    generated = root / "plugin"
    if generated.is_symlink() or not generated.is_dir():
        raise ValueError("Generated plugin/ must be a real directory; run scripts/build.py")
    expected = set(payload_names(root))
    actual = set()
    for path in generated.rglob("*"):
        if path.is_symlink():
            raise ValueError("Generated plugin/ must not contain symlinks")
        if path.is_file():
            name = path.relative_to(generated).as_posix()
            actual.add(name)
            if name not in expected or contained_file(generated, name).read_bytes() != contained_file(root, name).read_bytes():
                raise ValueError(f"Generated plugin/ payload differs from its source: {name}")
    if actual != expected:
        raise ValueError("Generated plugin/ is incomplete; run scripts/build.py")
    return len(actual)


def has_private_review_metadata(value):
    if isinstance(value, dict):
        return bool({"review", "test_cases", "test_credentials", "reviewer_instructions"} & value.keys()) or any(
            has_private_review_metadata(item) for item in value.values()
        )
    if isinstance(value, list):
        return any(has_private_review_metadata(item) for item in value)
    return False


def validate(root=ROOT, preview=False, check_installable=True):
    root = root.resolve()
    for name in (".claude-plugin/plugin.json", ".mcp.json", "README.md", "LICENSE", "skills.lock.json"):
        contained_file(root, name)
    manifest = json.loads((root / ".claude-plugin/plugin.json").read_text())
    if has_private_review_metadata(manifest):
        raise ValueError("Public source must not contain private review metadata")
    if manifest.get("name") != "wisepim" or not re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")):
        raise ValueError("Expected wisepim identity and explicit semantic version")
    if manifest.get("mcpServers") != "./.mcp.json":
        raise ValueError("Expected a contained MCP configuration path")
    if manifest.get("license") != "MIT" or not (root / "LICENSE").is_file():
        raise ValueError("Public package needs its MIT license")
    if manifest.get("privacyPolicyUrl") != "https://wisepim.com/privacy":
        raise ValueError("Directory privacy policy URL is required")
    if manifest.get("icon") != "./.claude-plugin/icon.png":
        raise ValueError("Directory icon must be the bundled PNG")
    icon = contained_file(root, ".claude-plugin/icon.png").read_bytes()
    if len(icon) < 33 or icon[:8] != b"\x89PNG\r\n\x1a\n" or icon[12:16] != b"IHDR":
        raise ValueError("Directory icon must be a PNG image")
    width, height = struct.unpack(">II", icon[16:24])
    if width != height or not 512 <= width <= 2048 or len(icon) >= 2_000_000:
        raise ValueError("Directory icon must be square, 512 to 2048 pixels, and below 2 MB")
    config = json.loads((root / ".mcp.json").read_text())
    if set(config) != {"mcpServers"} or set(config["mcpServers"]) != {"wisepim"}:
        raise ValueError("Exactly one declared WISEPIM destination is allowed")
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
    if check_installable and (root / "plugin").exists():
        validate_installable(root)
    return len(actual)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--installable", action="store_true", help="Require the generated directory payload and exact parity")
    args = parser.parse_args()
    try:
        count = validate(preview=args.preview)
        if args.installable:
            validate_installable()
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"Validation failed: {exc}\n")
    print(f"Package structure and {count} locked skill files validated; live OAuth and directory review are separate gates")
