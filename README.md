# claude-arsenal

> Claude Code 技能武器库 — 个人自用的高纪律工作流 skill 集合，以 Marketplace 形式发布，方便安装和持续更新。

## 已收录 Skill（可安装）

| Skill | 触发 | 说明 |
|---|---|---|
| **fix** | `/fix` | 纪律性 Bug 修复。强制根因分析，零猜测执行。5+1 阶段主流程：研究门控 → 根因调查 → 模式分析 → 假设验证 → 实现修复 → 防御加固 |
| **quick-fix** | 自动 / `/quick-fix` | 改代码时强制触发的工作流，L0→L4 阶梯调查深度，覆盖 fix/debug/optimize/refactor/UI 调整/设计稿还原/迁移/测试修复全场景 |

## 待发布 Skill（源码已收录，未上架 marketplace）

| Skill | 状态 | 阻塞项 |
|---|---|---|
| **cocos-cli** | WIP | 依赖外部 Node CLI（`cocos` 命令），CLI 本身需要先发布为独立 npm 包或 GitHub 仓库，之后才能上架 |

未来会持续增补更多 skill（类型和功能不限）。

## 安装

### 一次加仓库（添加 Marketplace）

```bash
/plugin marketplace add hubluesky/claude-arsenal
```

### 挑着装 plugin

```bash
/plugin install fix@claude-arsenal
/plugin install quick-fix@claude-arsenal
```

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
│   ├── cocos-cli/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/cocos-cli/SKILL.md
│   ├── fix/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/fix/SKILL.md
│   └── quick-fix/
│       ├── .claude-plugin/plugin.json
│       └── skills/quick-fix/SKILL.md
├── LICENSE
└── README.md
```

每个 plugin 独立版本，互不影响。

## 为什么这样拆？

- **每个 skill 独立 plugin**：用户可按需安装（只想要 `fix` 的人不会被迫装 `quick-fix`），各自独立版本，升级互不干扰，未来加任何类型的 skill 都能自然归位。
- **hubluesky 是 marketplace 命名空间**：通过 `hubluesky/claude-arsenal` 安装后，skill 名字就是原名（`fix`、`quick-fix`），不加前缀。

## 开发者：怎么加新 Skill

1. 在 `plugins/` 下新建 `<skill-name>/` 目录
2. 按上面的结构放入 `.claude-plugin/plugin.json` 和 `skills/<skill-name>/SKILL.md`
3. 在根 `.claude-plugin/marketplace.json` 的 `plugins` 数组追加条目
4. 提 commit 推上去，用户 `/plugin marketplace update claude-arsenal` 就能看到

## License

MIT
