"""Vendor reviewed canonical skills; never fetch credentials or execute skill content."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPOSITORY = "https://github.com/lldiegon/wisepim-skills"
EXPECTED_SKILLS = {
    "catalog-quality-audit", "prepare-product-translations", "channel-readiness-review"
}


def git(source, *args):
    return subprocess.run(
        ["git", "-C", str(source), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def collect(source):
    """Read only portable Markdown and per-skill OpenAI interface metadata."""
    skills = source / "skills"
    if skills.is_symlink() or not skills.is_dir():
        raise ValueError("Canonical source must contain a real skills/ directory")
    found = set()
    payload = {}
    for path in sorted(skills.rglob("*")):
        if path.is_symlink():
            raise ValueError("Symlinks are not allowed in canonical skills")
        if path.is_dir():
            continue
        relative = path.relative_to(source).as_posix()
        parts = Path(relative).parts
        if len(parts) < 3 or parts[1] not in EXPECTED_SKILLS:
            raise ValueError(f"Unexpected skill path: {relative}")
        if path.suffix != ".md" and parts[2:] != ("agents", "openai.yaml"):
            raise ValueError(f"Unsupported skill file: {relative}")
        data = path.read_bytes()
        data.decode("utf-8")
        if len(data) > 256 * 1024:
            raise ValueError(f"Skill file exceeds directory review threshold: {relative}")
        payload[relative] = data
        if parts[2:] == ("SKILL.md",):
            found.add(parts[1])
    if found != EXPECTED_SKILLS:
        raise ValueError(f"Expected exactly {sorted(EXPECTED_SKILLS)}")
    return payload


def sync(source, destination=ROOT, allow_uncommitted=False):
    source = source.resolve()
    if source == destination.resolve() or source in destination.resolve().parents:
        raise ValueError("Source and destination must be separate repositories")
    # Read and validate everything before replacing any generated copy.
    payload = collect(source)
    try:
        if Path(git(source, "rev-parse", "--show-toplevel")).resolve() != source:
            raise ValueError("Canonical source must be its own Git repository root")
        revision = git(source, "rev-parse", "HEAD")
        dirty = bool(git(source, "status", "--porcelain"))
    except subprocess.CalledProcessError:
        revision, dirty = None, True
    if dirty and not allow_uncommitted:
        raise ValueError("Canonical source must have a clean reviewed Git commit; use --allow-uncommitted for preview")
    if not dirty:
        for name, data in payload.items():
            committed = subprocess.run(
                ["git", "-C", str(source), "show", f"{revision}:{name}"],
                capture_output=True, check=False,
            )
            if committed.returncode or committed.stdout != data:
                raise ValueError(f"Skill file is not present verbatim in the source commit: {name}")
    lock = {
        "formatVersion": 1,
        "repository": SOURCE_REPOSITORY,
        "commit": revision,
        "sourceDirty": dirty,
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in payload.items()},
    }
    target = destination / "skills"
    if target.is_symlink():
        raise ValueError("Refusing to replace a symlink skills directory")
    if target.exists():
        shutil.rmtree(target)
    for name, data in payload.items():
        output = destination / name
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
    (destination / "skills.lock.json").write_text(json.dumps(lock, indent=2) + "\n")
    return lock


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--allow-uncommitted", action="store_true")
    args = parser.parse_args()
    try:
        lock = sync(args.source, allow_uncommitted=args.allow_uncommitted)
    except (ValueError, OSError, UnicodeError) as exc:
        parser.exit(1, f"Skill sync refused: {exc}\n")
    print(f"Synced {len(lock['files'])} files at {lock['commit'] or 'uncommitted preview'}")
