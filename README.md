# LitReviewAgent (MVP)

桌面端 + 本地后端原型，用于在用户合法访问会话中自动化 WoS/Scopus 题录导出、RIS 入库去重、Evidence 抽取与 Word 草稿生成。

## Monorepo 结构

- `apps/desktop/` Electron + React + TypeScript UI
- `services/backend/` FastAPI + Playwright + SQLite + pipeline
- `data/` 运行数据（截图/导出/草稿/审计）

## 合规与安全边界（已实现）

1. 不绕过付费墙，不破解，不批量爬取。
2. 默认仅导出题录。全文下载需人工审批接口（MVP 预留，当前默认不自动下全文）。
3. allowlist 强校验：导航前后都检查 host，越界直接失败。
4. takeover 模式：遇到登录/验证码/条款关键字时状态切 `NEED_TAKEOVER`，需 `/approve_takeover` 才恢复。
5. 审计日志：保存 run 动作结果、截图与导出文件 hash 到 `data/audit/`。
6. 不记录密码（日志里不落任何凭据字段）。

## 后端 API

- `POST /api/projects`
- `GET /api/projects`
- `POST /api/runs/{project_id}/start`
- `POST /api/runs/{run_id}/approve_takeover`
- `GET /api/runs/{run_id}/status`
- `GET /api/runs/{run_id}/latest_screenshot`
- `POST /api/ingest/ris`
- `POST /api/drafts/generate`
- `GET /api/files/{...}`

附加：
- `GET /api/papers/{project_id}`
- `GET /api/evidence/{project_id}`
- `GET /api/drafts/{project_id}`


## 小白快速上手（推荐先看）

如果你不熟悉开发环境，请先按这个顺序操作：

1. 打开 `docs/BEGINNER_GUIDE.md`（这是面向非技术用户的逐步点击教程）。
2. 先完成“第一次启动（只做一次）”。
3. 每次使用时只执行 `make dev`。
4. 在桌面界面依次使用：`dashboard -> console -> papers/evidence -> drafts`。

详细操作见：`docs/BEGINNER_GUIDE.md`。

## 开发启动

### 1) 安装依赖

```bash
cp .env.example .env
npm install
cd apps/desktop && npm install && cd ../..
cd services/backend && python -m pip install -e .[test] && cd ../..
python -m playwright install chromium
```

### 2) 一键开发运行

```bash
make dev
```

会同时启动：
- FastAPI: `http://127.0.0.1:8000`
- Electron + React UI

### 3) 仅后端

```bash
npm run backend
```

### 4) 模拟周更触发

```bash
make run-weekly
```

### 5) 测试

```bash
make test
```

## WoS / Scopus 工作流说明

- 当前 MVP 采用通用浏览器 loop + 站点入口 (`webofscience.com` / `scopus.com`)。
- 当站点 UI 变更导致动作失败时：查看 `data/screenshots/` 最后截图与 run status message。
- 维护方式：更新 `services/backend/app/workflow/orchestrator.py` 中启发式与动作逻辑。

## PDF 解析与扩展

- 当前 MVP 基于 abstract 生成 paper_card 与 evidence。
- `ENABLE_PDF=true` 后可扩展接入 PyMuPDF（接口已预留）。
- GROBID 作为后续插件可在 `services/backend/app/services/` 添加 provider 实现。

## 打包（可选）

- 桌面端可继续接入 `electron-builder`。
- 当前仓库以开发运行为主，未包含完整打包流水线。
