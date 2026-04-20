---
name: cocos-cli
description: "Cocos Creator CLI — 编译、预览、构建 Cocos Creator 3.8.7 项目。仅通过 /cocos-cli 手动调用。"
---

# Cocos CLI

Control Cocos Creator 3.8.7 from the command line. The `cocos` command is globally installed.

## Commands

| Command | What it does |
|---------|-------------|
| `cocos dev -p <project>` | Start CocosCreator as a headless background service (no GUI window). Enables CDP for compile/preview. |
| `cocos compile -p <project>` | Trigger resource compilation (~2s). Requires dev service running. |
| `cocos preview -p <project>` | Open preview URL in default browser. |
| `cocos build -p <project>` | Full release build (web-mobile). Slower, produces optimized output. |
| `cocos batch -p <project>` | Multi-channel batch build from `cocos-batch.yml`. |
| `cocos stop -p <project>` | Stop the background CocosCreator process. |

All commands accept `-p <project-path>`. If omitted, uses current directory.

## Workflow: Compile and Preview

This is the most common workflow when editing Cocos project code/assets.

### Step 1: Ensure dev service is running

Before compiling, the dev service must be running. Check by attempting a compile:

```bash
cocos compile -p <project-path>
```

If it fails with "socket hang up" or connection error, start the dev service first:

```bash
cocos dev -p <project-path>
```

Wait for the "Dev service is running" message before proceeding. The first startup takes ~30s as CocosCreator loads all packages.

### Step 2: Compile after code changes

```bash
cocos compile -p <project-path>
```

This takes ~2 seconds. The output shows the preview URL (e.g., `http://10.0.134.7:7456`).

### Step 3: Verify visuals (screenshot)

After compiling, take a screenshot to verify the game renders correctly:

```
# Using chrome-devtools MCP:
1. navigate_page to the preview URL
2. wait 2-3 seconds for the game to load
3. take_screenshot to capture the current frame
```

This is especially important after visual changes (UI layout, animations, textures).

### Step 4: Iterate

Repeat steps 2-3 after each code change. The preview browser auto-refreshes via socket.io LiveReload, but a screenshot confirms the actual visual state.

## Workflow: Release Build

For producing a final web-mobile build:

```bash
cocos build -p <project-path>
```

This takes 10-60 seconds. Build artifacts go to `<project>/build/web-mobile/`.

CocosCreator may exit with a non-zero code (e.g., 36) even on success due to editor plugins. The CLI checks for build artifacts and reports success if `index.html` exists.

## Key Options

| Option | Commands | Description |
|--------|----------|-------------|
| `--gui` | dev | Show CocosCreator GUI window (default: headless) |
| `--port <n>` | dev, compile, preview | CDP debugging port (default: 9222) |
| `--platform <name>` | build | Target platform (default: web-mobile) |
| `--debug` | build | Enable debug mode |
| `--editor <path>` | dev, build, batch | Path to CocosCreator.exe |

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `socket hang up` on compile | Dev service not ready or not started | Run `cocos dev` and wait 30s, then retry |
| `Editor.Message not available` | IDE still loading packages | Wait and retry — IDE needs ~30s to fully initialize |
| Build exit code non-zero but artifacts exist | CocosCreator plugin (e.g., playable-build) non-zero exit | Normal behavior — CLI handles this automatically |
| `CocosCreator.exe not found` | Not installed at default path | Use `--editor <path>` or set `COCOS_CREATOR` env var |

## Important Notes

- The dev service runs CocosCreator in headless mode by default (no visible window). Use `--gui` if you need to see the IDE.
- Only one dev service can run per project at a time. Use `cocos stop` before starting a new one.
- The preview URL is a local HTTP server started by CocosCreator's preview plugin. It supports socket.io LiveReload.
- For batch builds, create a `cocos-batch.yml` in the project root with channel definitions.
