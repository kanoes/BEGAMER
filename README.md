# BEGAMER

> 把“库里有什么”变成“今晚玩什么”。

BEGAMER 是一款为手机和电脑共同设计的私人 Steam 游戏库策展应用。生产环境由一个 Cloudflare Worker 托管 React 前端与 FastAPI API，数据保存在 D1；Google 登录将访问限制为指定账号。每次推送 `main`，GitHub Actions 都会完成检查、迁移并自动发布。

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Workers-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=111827)
![Cloudflare](https://img.shields.io/badge/Cloudflare-Workers%20%2B%20D1-F38020?logo=cloudflare&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-formatted-D7FF64)
![Biome](https://img.shields.io/badge/Biome-checked-60A5FA)

## 第一版功能

- 适配手机、平板与桌面的现代响应式 UI。
- 使用 Google Identity Services 登录，并只允许指定 Google 邮箱访问。
- 使用 Steam Web API 同步个人资料、游戏、总时长与近期游玩。
- 在电脑与手机之间同步收藏、状态和备注。
- 浏览、搜索、筛选游戏库，查看动态书架与 Collection 草案。
- 使用可解释的确定性算法推荐游戏；配置 OpenAI 后可增强推荐文案与选择。
- Steam、OpenAI 和会话密钥全部保存在 Cloudflare Secrets，不进入浏览器或仓库。
- 未配置 Steam 或 LLM 时仍可使用完整演示库与规则推荐。

> Steam 没有面向普通用户的 Collection 写入 Web API。BEGAMER 只生成可审核的整理方案，不会修改 Steam 客户端。

## 生产架构

```text
手机 / 电脑
    │ HTTPS + Google 会话
    ▼
Cloudflare Worker
    ├── React 静态资源（SPA）
    ├── FastAPI /api/v1
    ├── D1：账号、游戏库、收藏与备注
    ├── Steam Web API（只读同步）
    └── OpenAI Responses API（可选）

GitHub main ── GitHub Actions ── 检查 / D1 migration / deploy
```

在个人轻量使用下通常可以保持零成本：Cloudflare Workers Free、D1 Free、Google 登录和公开仓库 GitHub Actions 均有足够的免费额度。OpenAI API 如果启用会按实际用量计费；Steam Web API 本身不收费。

## 技术栈

```text
apps/web         React + TypeScript + Vite + Tailwind CSS + TanStack Query
apps/cloudflare  FastAPI on Python Workers + D1 + httpx + Pydantic
apps/api         本地 FastAPI + SQLAlchemy + SQLite（开发与未来可移植后端）
quality          Biome + Ruff + mypy + Vitest + Pytest
delivery         pnpm + uv + Wrangler + GitHub Actions
```

## 本地开发

需要 Node.js 22+、pnpm 11+、Python 3.13 与 `uv 0.12.3+`。

```bash
cp .env.example .env
cp apps/cloudflare/.dev.vars.example apps/cloudflare/.dev.vars
pnpm install
uv sync --all-groups
uv sync --project apps/cloudflare --all-groups
```

运行原生本地前后端：

```bash
pnpm dev
```

打开 <http://localhost:5173>。Vite 会把 `/api` 代理到本地 FastAPI。

运行与线上完全同构的 Cloudflare Worker 预览：

```bash
pnpm build
pnpm db:cloudflare:local
pnpm --dir apps/cloudflare dev
```

打开 <http://localhost:8787>。`.dev.vars.example` 默认关闭本地认证，生产配置始终要求登录。

## 一次性部署设置

### 1. Cloudflare

1. 创建名为 `begamer` 的 D1 数据库。
2. 把返回的数据库 ID 写入 `apps/cloudflare/wrangler.jsonc` 的 `database_id`。
3. 创建只允许部署 Workers 与管理该 D1 的 Cloudflare API Token。
4. 在 Worker 上配置以下 Secrets：

```dotenv
GOOGLE_CLIENT_ID=
ALLOWED_GOOGLE_EMAIL=
SESSION_SECRET=
STEAM_WEB_API_KEY=
STEAM_ID=
OPENAI_API_KEY=
```

只有前三项是 Google 登录必需配置。`SESSION_SECRET` 应使用至少 32 字节的随机值。

### 2. Google 登录

在 Google Cloud Console 创建 Web OAuth Client，将最终的 `https://<worker>.workers.dev` 加入 Authorized JavaScript origins。BEGAMER 使用 Google Identity Services 返回的 ID Token；不需要 Google Client Secret，也不会读取通讯录、Drive 或 Gmail。

### 3. GitHub Actions

在仓库 `Settings → Secrets and variables → Actions` 添加：

```text
CLOUDFLARE_ACCOUNT_ID
CLOUDFLARE_API_TOKEN
```

工作流 `.github/workflows/deploy.yml` 会在每次推送 `main` 时：

1. 安装锁定依赖；
2. 运行 Ruff、Biome、mypy、Pytest、Vitest 和 TypeScript 检查；
3. 构建响应式前端；
4. 对远端 D1 执行未应用迁移；
5. 发布 Worker 与静态资源。

## Steam 与 LLM

Steam API Key 可在 [Steam Web API Key 页面](https://steamcommunity.com/dev/apikey)申请。Steam 的“游戏详情”必须可见。所有 Steam 请求仅从后端发出，SteamID64 始终按字符串处理。

配置 `OPENAI_API_KEY` 后，AI 助手会在确定性算法筛出的候选范围内调用 Responses API；未配置、超时或返回无效结果时会安全回退，不影响其他功能。模型无法执行命令，也无法写入 Steam。

## 常用命令

```bash
pnpm check                  # Ruff + Biome + mypy + TypeScript
pnpm test                   # 两套 Pytest + Vitest
pnpm build                  # 构建生产前端
pnpm format                 # 格式化前后端
pnpm dev                    # 本地 FastAPI + Vite
pnpm dev:cloudflare         # Worker + D1 同构预览
pnpm db:cloudflare:local    # 本地 D1 migrations
```

## 目录结构

```text
.
├── .github/workflows       # CI 与 Cloudflare 自动部署
├── apps
│   ├── api                 # 本地 SQLAlchemy/SQLite 后端
│   ├── cloudflare
│   │   ├── migrations      # D1 SQL migrations
│   │   ├── src             # Worker、FastAPI、认证与领域逻辑
│   │   └── tests
│   └── web
│       └── src             # 页面、组件、认证门禁与 API client
├── biome.json
├── pyproject.toml
└── pnpm-workspace.yaml
```

## 安全边界

- 生产环境默认 `AUTH_REQUIRED=true`；登录邮箱必须与 `ALLOWED_GOOGLE_EMAIL` 完全一致。
- 会话 Cookie 为 `HttpOnly`、`Secure`、`SameSite=Lax`，有效期 30 天。
- Steam/OpenAI 密钥只存在 Cloudflare Secrets；GitHub 只保存有限权限的部署 Token。
- LLM 只能在后端给出的候选 AppID 内排序和解释。
- D1 按 Google subject 隔离账号数据，未来扩展多用户时无需重做数据模型。
