# HomelabOS-Plugins

Official plugin catalog and packages for [HomelabOS](https://github.com/Matff4/HomelabOS).

HomelabOS kiosks fetch [`index.json`](index.json) from this repository and install plugins from the tarball URLs listed there.

## Layout

```
HomelabOS-Plugins/
├── index.json              # Store catalog (committed to git)
├── plugins/                # Plugin source trees
│   └── uptime/
├── releases/               # Versioned .tar.gz packages (committed for v0.1)
└── scripts/
    └── build-release.py    # Pack plugins → releases/
```

## Adding a plugin

1. Create `plugins/<id>/` with `manifest.json`, widget HTML, optional `main.py` backend.
2. Run `python scripts/build-release.py` (or `python scripts/build-release.py uptime`).
3. Add an entry to `index.json` with the matching `releases/<id>-<version>.tar.gz` raw URL.
4. Commit, push to `master`.

See HomelabOS [PLUGIN_AUTHOR.md](https://github.com/Matff4/HomelabOS/blob/master/docs/PLUGIN_AUTHOR.md) for manifest and SDK details.

## Build a release tarball

```bash
python scripts/build-release.py
```

Output: `releases/<plugin-id>-<version>.tar.gz` (manifest at archive root).

## Catalog URL (HomelabOS default)

```
https://raw.githubusercontent.com/Matff4/HomelabOS-Plugins/master/index.json
```

After pushing, verify on a Pi: **Plugin store** (taskbar) → Browse → Install.

Restart after install:

```bash
sudo systemctl restart homelabos
```

## Plugins

| Id | Name | Description |
|----|------|-------------|
| `uptime` | Uptime | Host uptime from live system stats |
