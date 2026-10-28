"""Build a deterministic manual-install artifact from validated runtime files."""

from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from validate import ROOT, contained_file, validate


def build(root=ROOT):
    validate(root)
    names = [".claude-plugin/plugin.json", ".claude-plugin/icon.png", ".mcp.json", "LICENSE", "README.md", "skills.lock.json"]
    names.extend(path.relative_to(root).as_posix() for path in (root / "skills").rglob("*") if path.is_file())
    # README's relative documentation links remain usable in manual installs.
    names.extend(path.relative_to(root).as_posix() for path in (root / "submission").rglob("*.md"))
    destination = root / "dist" / "wisepim-claude-plugin.zip"
    destination.parent.mkdir(exist_ok=True)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
        for name in sorted(names):
            source = contained_file(root, name)
            info = ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes())
    return destination


if __name__ == "__main__":
    print(build())
