# claude-arsenal

> Claude Code 技能武器库 — 个人自用的高纪律工作流 skill 集合，以 Marketplace 形式发布，方便安装和持续更新。

## 已收录 Skill（可安装）

| Skill | 触发 | 说明 |
|---|---|---|
| **fix-quick** | 自动 / `/fix-quick` | 极轻快修，改代码时默认触发。覆盖 fix/debug/optimize/refactor/UI 调整/设计稿还原/迁移/测试修复全场景。L0→L1→L2 阶梯，L2 硬停弹用户选择 |
| **fix-deep** | `/fix-deep` | 重量深修。强制根因分析，零猜测执行。Phase 0-5 + L0-L4 阶梯 + Heavy 对齐 + 证据对称强制 + 死代码清理。仅手动调用或 fix-quick L2 升级时激活 |


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
│   └── fix-quick/
│       ├── .claude-plugin/plugin.json
│       └── skills/fix-quick/
│           ├── SKILL.md
│           └── references/
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
