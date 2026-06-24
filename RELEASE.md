# 发布规则

## Commit 规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Type 类型

| Type | 说明 | 版本变更 |
|------|------|---------|
| `feat` | 新功能 | minor (1.0.0 → 1.1.0) |
| `fix` | 修复bug | patch (1.0.0 → 1.0.1) |
| `docs` | 文档更新 | patch |
| `style` | 代码格式 | patch |
| `refactor` | 重构 | patch |
| `perf` | 性能优化 | patch |
| `test` | 测试 | patch |
| `chore` | 构建/工具 | patch |
| `ci` | CI配置 | patch |
| `revert` | 回滚 | patch |

### 示例

```bash
# 新功能
git commit -m "feat: 添加影评模板"

# 修复bug
git commit -m "fix: 修复中文书名URL编码问题"

# 带范围
git commit -m "feat(cover): 支持电影封面获取"
git commit -m "fix(api): 修复token过期问题"

# Breaking Change
git commit -m "feat!: 重构API接口

BREAKING CHANGE: 移除旧版接口"
```

## 发布流程

```bash
# 1. 提交代码
git add -A
git commit -m "feat: 新功能描述"

# 2. 更新版本
npm version patch   # fix, docs, style, refactor, perf, test, chore
npm version minor   # feat
npm version major   # BREAKING CHANGE

# 3. 推送
git push origin main --tags

# 4. 发布
npm publish
```

## 快捷命令

```bash
# patch 版本 (fix)
npm run release:patch

# minor 版本 (feat)
npm run release:minor

# major 版本 (breaking)
npm run release:major
```
