# Git工作流

---

## 1. 分支策略

### 1.1 分支类型

```
main                    # 主分支，生产环境
  │
  ├── develop           # 开发分支，日常开发
  │     │
  │     ├── feature/*   # 功能分支
  │     ├── fix/*       # 修复分支
  │     └── refactor/*  # 重构分支
  │
  └── hotfix/*          # 紧急修复（直接从main拉取）
```

### 1.2 分支说明

| 分支 | 用途 | 合并目标 |
|-----|------|---------|
| `main` | 生产代码，稳定版本 | - |
| `develop` | 开发集成，最新代码 | main |
| `feature/*` | 新功能开发 | develop |
| `fix/*` | Bug修复 | develop |
| `hotfix/*` | 生产紧急修复 | main + develop |

---

## 2. 开发流程

### 2.1 功能开发

```bash
# 1. 从develop创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/import-csv

# 2. 开发并提交
git add .
git commit -m "feat(import): 添加CSV导入功能"

# 3. 推送分支
git push origin feature/import-csv

# 4. 创建Pull Request
# 在GitHub/GitLab上创建PR，目标分支：develop

# 5. Code Review通过后合并
# 合并后删除功能分支
git branch -d feature/import-csv
```

### 2.2 Bug修复

```bash
# 1. 从develop创建修复分支
git checkout develop
git pull origin develop
git checkout -b fix/ranking-calculation

# 2. 修复并提交
git add .
git commit -m "fix(ranking): 修复排名计算错误"

# 3. 创建PR并合并
```

### 2.3 紧急修复

```bash
# 1. 从main创建hotfix分支
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# 2. 修复并提交
git add .
git commit -m "hotfix: 修复生产环境崩溃问题"

# 3. 合并到main
git checkout main
git merge hotfix/critical-bug
git push origin main

# 4. 同步到develop
git checkout develop
git merge hotfix/critical-bug
git push origin develop

# 5. 删除hotfix分支
git branch -d hotfix/critical-bug
```

---

## 3. Commit规范

### 3.1 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 3.2 Type类型

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | feat(import): 添加TXT导入 |
| `fix` | Bug修复 | fix(ranking): 修复排名错误 |
| `docs` | 文档 | docs: 更新API文档 |
| `style` | 格式 | style: 格式化代码 |
| `refactor` | 重构 | refactor(service): 重构查询逻辑 |
| `test` | 测试 | test: 添加导入测试 |
| `chore` | 构建/工具 | chore: 更新依赖 |

### 3.3 Scope范围

- `import` - 导入模块
- `ranking` - 排名模块
- `summary` - 汇总模块
- `auth` - 认证模块
- `api` - API层
- `db` - 数据库
- `ui` - 前端界面

### 3.4 示例

```bash
# 新功能
git commit -m "feat(import): 添加CSV文件导入功能

- 支持股票-概念映射CSV导入
- 添加数据校验和错误处理
- 自动创建新概念

Closes #123"

# Bug修复
git commit -m "fix(ranking): 修复排名计算中的空值问题

当交易值为0时，排名计算会出错。
添加空值检查和默认值处理。

Fixes #456"

# 文档更新
git commit -m "docs(api): 更新排名接口文档"
```

---

## 4. Pull Request

### 4.1 PR标题

```
[类型] 简短描述

示例：
[Feature] 添加CSV文件导入功能
[Fix] 修复排名计算错误
[Refactor] 重构查询服务
```

### 4.2 PR描述模板

```markdown
## 变更说明
简要描述本次变更的内容

## 变更类型
- [ ] 新功能
- [ ] Bug修复
- [ ] 重构
- [ ] 文档更新

## 测试
- [ ] 已添加单元测试
- [ ] 已手动测试
- [ ] 已测试边界情况

## 检查清单
- [ ] 代码符合规范
- [ ] 没有引入安全问题
- [ ] 更新了相关文档

## 关联Issue
Closes #xxx
```

### 4.3 Code Review要求

- 至少1人Approve
- CI检查通过
- 无冲突

---

## 5. 常用命令

### 5.1 日常操作

```bash
# 查看状态
git status

# 查看分支
git branch -a

# 切换分支
git checkout <branch>

# 拉取更新
git pull origin <branch>

# 推送
git push origin <branch>
```

### 5.2 分支操作

```bash
# 创建并切换分支
git checkout -b feature/xxx

# 删除本地分支
git branch -d feature/xxx

# 删除远程分支
git push origin --delete feature/xxx

# 查看分支合并情况
git branch --merged
```

### 5.3 提交操作

```bash
# 暂存所有文件
git add .

# 暂存指定文件
git add path/to/file

# 提交
git commit -m "message"

# 修改上次提交
git commit --amend

# 查看提交历史
git log --oneline -10
```

### 5.4 合并操作

```bash
# 合并分支
git merge feature/xxx

# 变基（保持线性历史）
git rebase develop

# 解决冲突后继续变基
git rebase --continue

# 放弃变基
git rebase --abort
```

### 5.5 撤销操作

```bash
# 撤销工作区修改
git checkout -- <file>

# 撤销暂存
git reset HEAD <file>

# 撤销提交（保留修改）
git reset --soft HEAD^

# 撤销提交（丢弃修改）
git reset --hard HEAD^
```

---

## 6. 版本发布

### 6.1 发布流程

```bash
# 1. 确保develop是最新的
git checkout develop
git pull origin develop

# 2. 合并到main
git checkout main
git merge develop

# 3. 打标签
git tag -a v1.0.0 -m "Release v1.0.0"

# 4. 推送
git push origin main
git push origin v1.0.0
```

### 6.2 版本号规范

```
v<主版本>.<次版本>.<修订版本>

- 主版本：不兼容的API变更
- 次版本：向后兼容的功能新增
- 修订版本：向后兼容的Bug修复

示例：
v1.0.0  # 首个正式版本
v1.1.0  # 新增功能
v1.1.1  # Bug修复
v2.0.0  # 重大变更
```

---

## 7. 最佳实践

### 7.1 提交频率

- 小步提交，每个提交做一件事
- 提交前确保代码可运行
- 不要提交半成品代码到develop/main

### 7.2 分支管理

- 功能分支生命周期不超过1周
- 及时删除已合并的分支
- 定期从develop同步更新

### 7.3 冲突处理

- 尽早解决冲突
- 冲突解决后仔细检查
- 不确定时咨询相关同事
