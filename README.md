# BEGAMER

> 把“库里有什么”变成“今晚玩什么”。

BEGAMER 是一个 local-first 的 Steam 游戏库策展工具：同步你的公开游戏库，整理游玩脉络，用透明的本地规则生成收藏方案，并在配置 LLM 后提供更个性化的推荐与解释。

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=111827)
![Ruff](https://img.shields.io/badge/Ruff-formatted-D7FF64)
![Biome](https://img.shields.io/badge/Biome-checked-60A5FA)

## 第一版能做什么

- 使用演示数据零配置体验完整 UI。
- 使用 Steam Web API 同步拥有的游戏、总时长与近期游玩。
- 浏览、搜索、筛选、收藏自己的游戏库。
- 查看“继续玩 / 从未启动 / 长期投入”等动态书架。
- 用本地确定性算法生成 Collection 草案。
- 配置 OpenAI API 后，用结构化输出增强“下一款玩什么”的推荐。
- LLM 缺失、超时或输出无效时自动回退，不影响普通功能。

> Steam 没有面向普通用户的 Collection 写入 Web API。BEGAMER v1 只生成可审核的整理方案，不会修改 Steam 客户端。

## 技术栈

```text
apps/web  React + TypeScript + Vite + Tailwind CSS + TanStack Query
apps/api  FastAPI + SQLAlchemy 2 + SQLite + Pydantic + OpenAI SDK
quality   Biome（前端）+ Ruff（后端）+ Vitest + Pytest
tooling   pnpm + uv + GitHub Actions
```

## 快速开始

需要 Node.js 22+、pnpm 10+ 与 [uv](https://docs.astral.sh/uv/)。

```bash
cp .env.example .env
pnpm install
uv sync --all-groups
```

启动后端：

```bash
pnpm dev:api
```

另开一个终端启动前端：

```bash
pnpm dev:web
```

打开 <http://localhost:5173>。数据库首次启动会自动创建，并填充演示游戏库。

## 连接真实 Steam 游戏库

1. 在 <https://steamcommunity.com/dev/apikey> 申请 Steam Web API Key。
2. 确保 Steam 隐私设置中的“游戏详情”可见。
3. 在根目录 `.env` 填写：

```dotenv
STEAM_WEB_API_KEY=your-key
STEAM_ID=your-17-digit-steam-id
```

4. 在应用右上角打开“同步 Steam”，确认 SteamID 后同步。

密钥只由后端读取，并通过 `x-webapi-key` 请求头发给 Steam；前端、响应与日志中均不会包含密钥。

## 开启 LLM 推荐

在 `.env` 中填写：

```dotenv
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-5.6-luna
```

可选的 `OPENAI_BASE_URL` 允许连接实现了 Responses API 与 Structured Outputs 的 OpenAI-compatible provider。未配置时，应用会清晰标记“本地策展”，并继续返回可复现的规则推荐。

## 常用命令

```bash
pnpm dev             # 同时启动前后端
pnpm check           # Ruff + Biome + 类型检查
pnpm test            # Pytest + Vitest
pnpm build           # 构建前端
pnpm format          # 自动格式化前后端
pnpm db:migrate      # 运行 Alembic 数据库迁移
```

## 目录结构

```text
.
├── apps
│   ├── api
│   │   ├── migrations
│   │   ├── src/begamer
│   │   │   ├── api            # HTTP 路由与依赖
│   │   │   ├── clients        # Steam / LLM 外部客户端
│   │   │   ├── core           # 配置
│   │   │   ├── db             # ORM 与会话
│   │   │   └── services       # 同步、分析、推荐领域逻辑
│   │   └── tests
│   └── web
│       └── src
│           ├── components     # 可复用 UI 与业务组件
│           ├── lib            # API、类型与工具
│           └── pages          # 页面级组合
├── biome.json
├── pyproject.toml
└── pnpm-workspace.yaml
```

## 数据与安全边界

- 默认只监听本机，SQLite 数据位于 `data/begamer.db`，该目录不会提交到 Git。
- Steam 与 OpenAI 密钥只存在于被忽略的 `.env`。
- 同步失败、隐私受限或 Steam 返回异常空响应时，已有库不会被删除。
- LLM 只能在后端给出的候选 AppID 内排序和解释，无法运行命令或操作 Steam。
- 如果未来把服务公开到网络，必须先增加用户认证、速率限制和隐私政策。

## 官方接口依据

- [Steam IPlayerService](https://partner.steamgames.com/doc/webapi/IPlayerService)
- [Steam Web API 身份验证](https://partner.steamgames.com/doc/webapi_overview/auth)
- [OpenAI Responses API](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)

## Roadmap

- 成就按需同步与接近全成就提醒
- 商店元数据 / 标签数据源适配器
- 可编辑、可版本化的 Collection 方案与 CSV/JSON 导出
- 多 Steam 账号、PostgreSQL 与后台任务队列
- 由 Codex Computer Use 执行“已审核”的 Steam 客户端整理方案
