#!/usr/bin/env python3
"""Pack plugin source trees into release tarballs and sync index.json."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = ROOT / "plugins"
RELEASES_DIR = ROOT / "releases"
INDEX_PATH = ROOT / "index.json"


def tarball_url_for(plugin_id: str, version: str, existing_url: str | None) -> str:
    filename = f"{plugin_id}-{version}.tar.gz"
    if existing_url:
        base = existing_url.rsplit("/", 1)[0]
        return f"{base}/{filename}"
    return (
        "https://raw.githubusercontent.com/Matff4/HomelabOS-Plugins/master"
        f"/releases/{filename}"
    )


def sync_index(plugin_id: str, version: str) -> None:
    if not INDEX_PATH.is_file():
        print(f"Skip index sync: {INDEX_PATH.name} not found")
        return

    catalog = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    matched = False
    for entry in catalog.get("plugins", []):
        if entry.get("id") != plugin_id:
            continue
        matched = True
        entry["version"] = version
        entry["tarball_url"] = tarball_url_for(plugin_id, version, entry.get("tarball_url"))
        break

    if not matched:
        print(f"Warning: {plugin_id!r} not found in {INDEX_PATH.name} — add a catalog entry manually")
        return

    catalog["updated_at"] = datetime.now(UTC).replace(microsecond=0).isoformat()
    INDEX_PATH.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {INDEX_PATH.name} → {plugin_id} v{version}")


def build_plugin(plugin_dir: Path, *, sync_catalog: bool) -> Path:
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
    if sync_catalog:
        sync_index(plugin_id, version)
    return archive_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build plugin release tarballs")
    parser.add_argument(
        "plugin_id",
        nargs="?",
        help="Build one plugin (default: all under plugins/)",
    )
    parser.add_argument(
        "--no-sync-index",
        action="store_true",
        help="Do not update index.json version/tarball_url",
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
        built.append(build_plugin(plugin_dir, sync_catalog=not args.no_sync_index))

    if not built:
        raise SystemExit("No plugins built")


if __name__ == "__main__":
    main()
