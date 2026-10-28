"""Build a deterministic manual-install artifact from validated runtime files."""

from pathlib import Path
import shutil
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from validate import ROOT, contained_file, payload_names, validate, validate_installable


def build(root=ROOT):
    root = root.resolve()
    validate(root, check_installable=False)
    names = payload_names(root)
    payload = {name: contained_file(root, name).read_bytes() for name in names}
    generated = root / "plugin"
    destination = root / "dist" / "wisepim-claude-plugin.zip"
    if generated.is_symlink() or destination.parent.is_symlink() or destination.is_symlink():
        raise ValueError("Build outputs must not be symlinks")
    if generated.exists():
        if any(path.is_symlink() for path in generated.rglob("*")):
            raise ValueError("Generated plugin/ contains a symlink; refusing replacement")
        shutil.rmtree(generated)
    for name, data in payload.items():
        output = generated / name
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
    validate_installable(root)
    destination.parent.mkdir(exist_ok=True)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in payload.items():
            info = ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return destination


if __name__ == "__main__":
    print(build())
