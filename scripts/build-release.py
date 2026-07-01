#!/usr/bin/env python3
"""Pack plugin source trees into release tarballs."""

from __future__ import annotations

import argparse
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = ROOT / "plugins"
RELEASES_DIR = ROOT / "releases"


def build_plugin(plugin_dir: Path) -> Path:
    manifest_path = plugin_dir / "manifest.json"
    if not manifest_path.is_file():
        raise SystemExit(f"Missing manifest: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    plugin_id = manifest["id"]
    version = manifest["version"]
    if plugin_dir.name != plugin_id:
        raise SystemExit(f"Folder {plugin_dir.name} must match manifest id {plugin_id}")

    RELEASES_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = RELEASES_DIR / f"{plugin_id}-{version}.tar.gz"

    with tarfile.open(archive_path, "w:gz") as archive:
        for path in sorted(plugin_dir.rglob("*")):
            if not path.is_file():
                continue
            if path.name.endswith(".pyc") or "__pycache__" in path.parts:
                continue
            archive.add(path, arcname=path.relative_to(plugin_dir).as_posix())

    print(f"Built {archive_path.relative_to(ROOT)}")
    return archive_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build plugin release tarballs")
    parser.add_argument(
        "plugin_id",
        nargs="?",
        help="Build one plugin (default: all under plugins/)",
    )
    args = parser.parse_args()

    if not PLUGINS_DIR.is_dir():
        raise SystemExit(f"Plugins directory not found: {PLUGINS_DIR}")

    built: list[Path] = []
    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir():
            continue
        if args.plugin_id and plugin_dir.name != args.plugin_id:
            continue
        built.append(build_plugin(plugin_dir))

    if not built:
        raise SystemExit("No plugins built")


if __name__ == "__main__":
    main()
