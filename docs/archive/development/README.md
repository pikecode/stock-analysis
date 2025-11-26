# 🛠️ 开发文档

本目录包含开发规范、环境搭建、编码指南和工作流。适合所有开发人员。

---

## 📂 文档结构

| 文档 | 内容 | 关键章节 |
|------|------|---------|
| **SETUP.md** | 开发环境配置和部署 | 依赖安装、数据库初始化、虚拟环境 |
| **CODING_STANDARDS.md** | 编码规范和最佳实践 | 命名规范、代码结构、注释规范 |
| **GIT_WORKFLOW.md** | Git 工作流和提交规范 | 分支管理、提交信息、合并流程 |

---

## 🎯 快速导航

### 场景 1: 我是新加入的开发人员（首选）

**推荐阅读顺序：**

1. 📖 本页面 (README.md) - 了解开发文档结构
2. 🔧 [SETUP.md](./SETUP.md) - 搭建本地开发环境
   - 选择开发方式（本地或 Docker）
   - 安装依赖
   - 初始化数据库
   - 启动开发服务器
3. 📝 [CODING_STANDARDS.md](./CODING_STANDARDS.md) - 学习编码规范
   - Python 代码规范
   - JavaScript/TypeScript 规范
   - API 设计规范
4. 🌳 [GIT_WORKFLOW.md](./GIT_WORKFLOW.md) - 理解工作流程
   - 分支命名规范
   - 提交信息规范
   - Pull Request 流程

**完成后：** 你就可以开始开发了！

---

### 场景 2: 我要开始编写代码

**先决条件检查：**
- [ ] 已按照 [SETUP.md](./SETUP.md) 配置好开发环境
- [ ] 已阅读 [CODING_STANDARDS.md](./CODING_STANDARDS.md)
- [ ] 已理解 [GIT_WORKFLOW.md](./GIT_WORKFLOW.md)

**开始前：**
1. 确保所有依赖已安装
2. 启动数据库和后端服务
3. 创建新分支：`git checkout -b feature/your-feature`

**开发中：**
- 遵循 [CODING_STANDARDS.md](./CODING_STANDARDS.md) 的规范
- 定期提交代码，遵循提交规范
- 编写测试用例
- 保持代码干净和可读

**提交前：**
- 运行测试：确保所有测试通过
- 检查代码格式：运行 linter 和 formatter
- 准备 Pull Request

---

### 场景 3: 我要提交代码 / 创建 Pull Request

**参考文档：** [GIT_WORKFLOW.md](./GIT_WORKFLOW.md)

**步骤：**
1. 确保代码符合 [CODING_STANDARDS.md](./CODING_STANDARDS.md)
2. 创建 Pull Request，说明更改内容
3. 等待 Code Review
4. 根据反馈进行修改
5. 获得批准后合并到 main

---

### 场景 4: 我要查看编码规范

**直接查看：** [CODING_STANDARDS.md](./CODING_STANDARDS.md)

**主要章节：**
- Python 编码规范（PEP 8）
- JavaScript/TypeScript 规范
- 注释和文档说明规范
- API 接口设计规范

---

### 场景 5: 我遇到了部署或环境问题

**参考文档：** [SETUP.md](./SETUP.md) - 常见问题部分

**常见问题：**
- PostgreSQL 连接失败
- Redis 无法连接
- Python 虚拟环境问题
- 前端构建失败

---

## 🚀 开发工作流简图

```
┌─────────────────────────────────────────┐
│  1. 环境搭建 (SETUP.md)                 │
│  - 安装依赖                              │
│  - 配置数据库                            │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  2. 创建分支 (GIT_WORKFLOW.md)           │
│  - git checkout -b feature/xxx            │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  3. 编写代码 (CODING_STANDARDS.md)       │
│  - 遵循编码规范                          │
│  - 编写测试                              │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  4. 提交代码 (GIT_WORKFLOW.md)           │
│  - 遵循提交规范                          │
│  - 编写清晰的提交信息                    │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  5. Pull Request (GIT_WORKFLOW.md)       │
│  - 创建 PR                               │
│  - 描述更改内容                          │
│  - Code Review                           │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  6. 合并到 main                         │
│  - 测试通过                              │
│  - Review 批准                           │
└─────────────────────────────────────────┘
```

---

## 📋 技术栈概览

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | React 18+ | 用户界面和交互 |
| **前端构建** | Vite | 快速开发服务器 |
| **前端样式** | TailwindCSS | 样式管理 |
| **后端** | FastAPI | RESTful API 框架 |
| **ORM** | SQLAlchemy | 数据库映射 |
| **数据库** | PostgreSQL | 关系数据库 |
| **缓存** | Redis | 缓存和消息队列 |
| **任务队列** | Celery | 异步任务处理 |

---

## 🔗 相关资源

### 与其他文档的关联

- **架构设计** - [docs/architecture/](../architecture/) - 系统设计和规范
- **项目管理** - [docs/project/](../project/) - 进度和任务
- **使用指南** - [docs/guides/](../guides/) - 系统使用文档
- **系统初始化** - [scripts/setup/](../../scripts/setup/) - 初始化脚本

### 外部资源

- **FastAPI 官网** - https://fastapi.tiangolo.com/
- **React 官网** - https://react.dev/
- **PostgreSQL 官网** - https://www.postgresql.org/
- **PEP 8 Python 规范** - https://www.python.org/dev/peps/pep-0008/

---

## ✨ 开发提示

**1. 定期拉取最新代码**
```bash
git fetch origin
git rebase origin/main
```

**2. 开发前创建新分支**
```bash
git checkout -b feature/your-feature
```

**3. 保持代码质量**
```bash
# Python
pylint backend/
black backend/

# JavaScript
npm run lint
npm run format
```

**4. 运行测试**
```bash
# 后端测试
pytest backend/tests/

# 前端测试
npm run test
```

**5. 保持分支同步**
```bash
git fetch origin
git rebase origin/main
```

---

## 📞 获取帮助

遇到问题？

1. 查看文档中的常见问题部分
2. 在相关文档中搜索关键词
3. 查看脚本中的注释和帮助信息
4. 联系项目团队

---

## 📝 维护说明

**最后更新：** 2024-11-25

**维护建议：**
- 技术栈升级时更新 SETUP.md
- 编码规范调整时更新 CODING_STANDARDS.md
- 工作流变更时更新 GIT_WORKFLOW.md
- 定期审查文档准确性

---
