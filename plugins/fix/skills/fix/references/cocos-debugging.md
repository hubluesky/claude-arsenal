# CocosCreator / Playable 专用调试指南

## 概述

当项目使用 CocosCreator 引擎或开发 Playable 互动广告时，在标准调试流程（Phase 0-5）基础上参考本指南。

## 组件生命周期调试

### 生命周期顺序

```
onLoad → onEnable → start → update → lateUpdate → onDisable → onDestroy
```

### 常见陷阱

| 陷阱 | 场景 | 诊断方法 |
|------|------|----------|
| onLoad 中访问其他节点 | 被访问的节点可能尚未初始化 | 在 onLoad 中 log 目标节点是否为 null |
| start 中假设所有 onLoad 完成 | 动态加载的节点 onLoad 时序不确定 | 改用回调或事件通知替代时序假设 |
| update 中做一次性逻辑 | 每帧都执行导致重复 | 用 flag 控制或移到 start |
| onDestroy 中访问已销毁节点 | 销毁顺序不保证 | 加 isValid 检查 |
| scheduleOnce 时序假设 | 假设延迟后某状态一定存在 | 在回调中检查目标是否仍然有效 |

### 调试步骤

遇到初始化相关 bug 时：
1. 确认问题出在哪个生命周期阶段（加 console.log 标记）
2. 检查节点树中的父子关系和加载顺序
3. 检查是否有动态加载的节点影响时序
4. 如果涉及跨节点通信，绘制时序关系

## 场景树状态检查

遇到 "节点不存在" 或 "组件为 null" 错误时：

### 检查步骤

1. **验证节点是否存在**
   - `cc.find("/Canvas/预期路径")` 检查运行时节点
   - 如有 MCP 工具（cocos-game-intelligence），用 `getSceneTree` 查看运行时场景树

2. **检查 active 状态链**
   - `node.active === true?`
   - `node.parent.active === true?`（递归向上检查每一级）
   - `component.enabled === true?`

3. **检查节点路径**
   - 路径是否因场景结构调整而变化？
   - 是否使用了硬编码路径而非引用？

4. **检查组件是否挂载**
   - `node.getComponent(ComponentName)` 是否返回 null？
   - 组件是否在编辑器中正确添加？
   - 是否拼写错误或引用了错误的组件类？

## Playable 广告特化

### 单 HTML 打包问题

| 问题类型 | 排查方向 |
|----------|----------|
| 资源加载失败 | base64 内联是否正确？资源路径是否被打包工具改写？ |
| 图片不显示 | base64 编码是否完整？MIME type 是否正确？ |
| 音频不播放 | 各渠道对自动播放的限制不同，需用户交互触发 |
| 包体超限 | 检查 base64 膨胀（约 33%），压缩图片质量，减少资源数量 |
| 字体缺失 | 字体是否正确内联？是否使用了系统字体回退？ |

### 多渠道适配（10 渠道）

| 排查维度 | 方法 |
|----------|------|
| SDK 注入时序 | 各渠道 mraid/dapi 等 SDK ready 事件时序不同，不能假设同步可用 |
| API 兼容性 | mraid.open() vs dapi.openStoreOverlay() 等 API 差异 |
| 尺寸适配 | 各渠道容器尺寸不同，需用 `cc.view.setResizeCallback` 监听 |
| 关闭按钮 | 部分渠道强制要求自定义关闭按钮位置和样式 |
| 横竖屏 | 部分渠道固定方向，部分允许旋转，需分别处理 |
| 安全区域 | iPhone 刘海屏等安全区域在不同渠道的处理方式不同 |

**渠道调试优先级**：先在目标渠道的测试工具中复现，再查看渠道文档确认 API 行为差异。

### 多语言适配（16 种语言）

| 问题 | 排查 |
|------|------|
| 字体回退 | 检查字体文件是否包含目标语言字符集（阿拉伯语、日语、韩语等） |
| 文本溢出 | 德语/俄语等长文本是否超出容器，需动态调整字号或容器大小 |
| RTL 布局 | 阿拉伯语/希伯来语的从右到左布局是否正确处理 |
| 换行规则 | 日语/中文的换行规则与英语不同（不能在任意位置断词） |
| 占位符 | 动态文本中的 {0} 等占位符在不同语言中位置可能不同 |
| 缺失翻译 | 检查语言包是否覆盖所有 key，fallback 到默认语言是否正常 |

## 渲染问题排查

### 元素不显示 — 检查链

按顺序检查，找到第一个异常即为根因：

1. `node.active === true?`
2. 父节点链上所有节点 `active === true?`
3. `opacity > 0?` / `color.a > 0?`
4. `UITransform` 的 `contentSize` 是否为 0?
5. 节点位置是否在可视区域内（Canvas 范围）?
6. Camera 的 `culling mask` 是否包含该节点的 layer?
7. Z-order / `siblingIndex` 是否被其他节点遮挡?
8. 材质/shader 是否正常（透明度、混合模式）?

### 性能问题

- `cc.debug.setDisplayStats(true)` 查看 draw call 数和 FPS
- **Draw call 过高** → 检查是否可以合批（同 atlas、同材质、同 layer）
- **FPS 低** → 检查 `update` 中是否有重计算，是否有节点频繁创建/销毁
- **内存泄漏** → 检查是否有未释放的事件监听、未销毁的节点池、未回收的纹理

## 事件系统取证

### 触摸不响应

1. 检查是否有 `BlockInputEvents` 组件阻挡（自身或祖先节点）
2. 检查节点层级是否被其他透明节点遮挡（即使透明也会吃事件）
3. 检查 `UITransform` 的 `contentSize` 是否覆盖了期望的触摸区域
4. 检查 `Button` 组件的 `interactable` 是否为 true
5. 检查是否有全局触摸监听吞噬了事件（`cc.input.on` 或 `node.on` 在父节点）

### 自定义事件问题

- `cc.director.on/off` 或 `EventTarget` 是否正确配对？
- 事件名拼写是否一致（大小写敏感）？
- 是否在 `onDestroy` 中正确 `off` 了监听（防泄漏）？
- 多实例场景下，事件是否发给了正确的目标？
