# claude-arsenal

> Claude Code 技能武器库 — 个人自用的高纪律工作流 skill 集合，以 Marketplace 形式发布，方便安装和持续更新。

## 已收录 Plugin（可安装）

| Plugin | 含 Skill | 触发 | 说明 |
|---|---|---|---|
| **fix** | `fix:fix-quick`、`fix:fix-deep` | 自动 / `/fix-quick`、`/fix-deep` | 修 bug 技能组：fix-quick 极轻快修（改代码默认触发，L0→L1→L2 阶梯，L2 硬停弹用户选择）+ fix-deep 重量深修（根因驱动，Phase 0-5 + L0-L4 + Heavy 对齐，仅手动或 fix-quick L2 升级激活） |
| **tts-notify** | — | 自动(跨平台) | TTS 语音通知 hook。Stop / Notification / PermissionRequest / AskUserQuestion 四事件触发。装了 edge-tts 用神经语音(缓存 MP3)，未装/失败回退系统自带 TTS。Stop 事件按助手最后消息动态生成 |

> **tts-notify 前置依赖**：跨平台 (Windows / macOS / Linux)，仅需 Python 3.x。`edge-tts` 为**可选增强**—— `pip install edge-tts` 后用神经语音 (需联网，MP3 缓存到 `~/.claude/cache/tts-notify/`，经各平台原生播放器播放)。未装 edge-tts、离线或生成失败时，自动回退到系统自带 TTS：Windows 用 SAPI、macOS 用 `say`、Linux 用 `espeak-ng` / `spd-say`。


## 安装

### 一次加仓库（添加 Marketplace）

```bash
/plugin marketplace add hubluesky/claude-arsenal
```

### 挑着装 plugin

```bash
/plugin install fix@claude-arsenal
/plugin install tts-notify@claude-arsenal
```

> 装好后调用前缀就是 plugin 名：`fix:fix-quick`、`fix:fix-deep`。

### 更新

```bash
/plugin update fix@claude-arsenal
# 或一次性更新仓库下所有已装 plugin
/plugin marketplace update claude-arsenal
```

### 卸载

```bash
/plugin uninstall fix@claude-arsenal
```

## 仓库结构

```
claude-arsenal/
├── .claude-plugin/
│   └── marketplace.json       # 仓库声明，列出所有 plugin
├── plugins/
│   ├── fix/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/
│   │       ├── fix-quick/
│   │       │   ├── SKILL.md
│   │       │   └── references/
│   │       └── fix-deep/
│   │           ├── SKILL.md
│   │           └── references/
│   └── tts-notify/
│       ├── .claude-plugin/plugin.json
│       └── hooks/
│           ├── hooks.json
│           └── tts_notify.py
├── LICENSE
└── README.md
```

每个 plugin 独立版本，互不影响。

## 为什么这样拆？

- **按主题打 plugin**：紧密联动的 skill 合到同一 plugin（如 `fix` 含 `fix-quick`/`fix-deep`），独立功能各自一个 plugin（如 `tts-notify`）。
- **fix-quick + fix-deep 联动**：fix-quick L2 失败后弹用户选择，可升级到 fix-deep 继续深挖。
- **调用前缀 = plugin 名**：在 `fix` plugin 下两个 skill 调用名为 `fix:fix-quick`、`fix:fix-deep`。

## 开发者：怎么加新 Skill / Plugin

- **加 skill 到现有 plugin**：在 `plugins/<plugin-name>/skills/` 下新建 `<skill-name>/SKILL.md`，无需改 `marketplace.json`。
- **加新 plugin**：
  1. 在 `plugins/` 下新建 `<plugin-name>/` 目录
  2. 放入 `.claude-plugin/plugin.json` 和 `skills/<skill-name>/SKILL.md`
  3. 在根 `.claude-plugin/marketplace.json` 的 `plugins` 数组追加条目
  4. 提 commit 推上去，用户 `/plugin marketplace update claude-arsenal` 就能看到

## License

MIT
