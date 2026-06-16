# claude-arsenal

> Claude Code 技能武器库 — 个人自用的高纪律工作流 skill 集合，以 Marketplace 形式发布，方便安装和持续更新。

## 已收录 Skill（可安装）

| Skill | 触发 | 说明 |
|---|---|---|
| **fix-quick** | 自动 / `/fix-quick` | 极轻快修，改代码时默认触发。覆盖 fix/debug/optimize/refactor/UI 调整/设计稿还原/迁移/测试修复全场景。L0→L1→L2 阶梯，L2 硬停弹用户选择 |
| **fix-deep** | `/fix-deep` | 重量深修。强制根因分析，零猜测执行。Phase 0-5 + L0-L4 阶梯 + Heavy 对齐 + 证据对称强制 + 死代码清理。仅手动调用或 fix-quick L2 升级时激活 |
| **tts-notify** | 自动(跨平台) | TTS 语音通知 hook。Stop / Notification / PermissionRequest / AskUserQuestion 四事件触发。装了 edge-tts 用神经语音(缓存 MP3),未装/失败回退系统自带 TTS。Stop 事件按助手最后消息动态生成 |

> **tts-notify 前置依赖**：跨平台(Windows / macOS / Linux),仅需 Python 3.x。`edge-tts` 为**可选增强**——`pip install edge-tts` 后用神经语音(需联网,MP3 缓存到 `~/.claude/cache/tts-notify/`,经各平台原生播放器播放,**已不再需要 ffmpeg**)。未装 edge-tts、离线或生成失败时,自动回退到系统自带 TTS:Windows 用 SAPI(MediaPlayer 播放)、macOS 用 `say`、Linux 用 `espeak-ng` / `spd-say`。Windows/macOS 的系统 TTS 零安装即用;Linux 中文需自行安装 `espeak-ng` 及中文语音数据(或装播放器 `mpg123`/`ffplay` 以走 edge-tts 路径)。


## 安装

### 一次加仓库（添加 Marketplace）

```bash
/plugin marketplace add hubluesky/claude-arsenal
```

### 挑着装 plugin

```bash
/plugin install fix-quick@claude-arsenal
/plugin install fix-deep@claude-arsenal
```

### 更新

```bash
/plugin update fix-quick@claude-arsenal
# 或一次性更新仓库下所有已装 plugin
/plugin marketplace update claude-arsenal
```

### 卸载

```bash
/plugin uninstall fix-quick@claude-arsenal
```

## 仓库结构

```
claude-arsenal/
├── .claude-plugin/
│   └── marketplace.json       # 仓库声明，列出所有 plugin
├── plugins/
│   ├── fix-deep/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/fix-deep/
│   │       ├── SKILL.md
│   │       └── references/
│   ├── fix-quick/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/fix-quick/
│   │       ├── SKILL.md
│   │       └── references/
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

- **每个 skill 独立 plugin**：用户可按需安装，各自独立版本，升级互不干扰。
- **fix-quick + fix-deep 联动**：fix-quick L2 失败后弹用户选择，可升级到 fix-deep 继续深挖。
- **hubluesky 是 marketplace 命名空间**：通过 `hubluesky/claude-arsenal` 安装后，skill 名就是原名，不加前缀。

## 开发者：怎么加新 Skill

1. 在 `plugins/` 下新建 `<skill-name>/` 目录
2. 按上面的结构放入 `.claude-plugin/plugin.json` 和 `skills/<skill-name>/SKILL.md`
3. 在根 `.claude-plugin/marketplace.json` 的 `plugins` 数组追加条目
4. 提 commit 推上去，用户 `/plugin marketplace update claude-arsenal` 就能看到

## License

MIT
