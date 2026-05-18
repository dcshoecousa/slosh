# FastAPI + PostgreSQL Project Scaffold

这是一个基于 `FastAPI + PostgreSQL + SQLAlchemy 2.0 + Poetry` 的项目骨架，已经包含一套可直接继续开发的基础能力：

- JWT 登录鉴权
- 分层配置管理
- 通用 CRUD 基类与 `users` 模块示例
- 统一异常处理
- 请求日志与请求 ID
- Alembic 迁移骨架
- 单元测试与接口测试样例
- Docker / Docker Compose 本地开发环境

## Project Structure

```text
.
├── alembic/
├── app/
│   ├── api/
│   ├── core/
│   │   └── settings/
│   ├── crud/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   └── services/
├── tests/
├── .env.example
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Quick Start

### 1. Install Poetry

```powershell
pip install poetry
```

### 2. Install Dependencies

```powershell
poetry install
```

### 3. Prepare Environment Variables

```powershell
Copy-Item .env.example .env
```

请至少修改 `.env` 里的 `JWT_SECRET_KEY`。

### 4. Start PostgreSQL

```powershell
docker compose up -d postgres
```

### 5. Run Migrations

```powershell
poetry run alembic upgrade head
```

### 6. Start the API

```powershell
poetry run uvicorn app.main:app --reload
```

## CLI

### Create User

```powershell
python -m app.cli create-user --email admin@example.com --password password123 --full-name "Admin User" --role admin
```

可选参数：

- `--role`: `admin` 或 `member`，默认 `member`
- `--inactive`: 创建为禁用用户

### Start Service

```powershell
python -m app.cli serve
python -m app.cli serve --host 127.0.0.1 --port 8044 --reload
```

启动后可以访问：

- Swagger: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/api/v1/health`

### Start Taskiq Worker

```powershell
python -m taskiq worker app.task.worker:broker app.task.tasks
```

`app/task/` 目录现在包含：

- `broker.py`: Taskiq broker 和 result backend 初始化
- `tasks.py`: 示例任务
- `worker.py`: worker 入口

启用队列前，请在 `.env` 中至少配置：

```env
TASKIQ_ENABLED=true
TASKIQ_DATABASE_URL=postgresql://slosh:sloshpassword@127.0.0.1:5432/slosh_db
```

如果 `TASKIQ_DATABASE_URL` 留空，会回退使用 `DATABASE_URL`。

### Task APIs

- `POST /api/v1/tasks/echo`: 入队一个简单 echo 任务
- `POST /api/v1/tasks/user-summary`: 入队一个用户统计任务
- `GET /api/v1/tasks/{task_id}`: 查询任务状态

示例：

```powershell
$token = "<access_token>"

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/tasks/echo" `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"message":"hello taskiq"}'
```

返回的 `task_id` 可以继续查询：

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri "http://127.0.0.1:8000/api/v1/tasks/<task_id>?wait=true&timeout_seconds=5" `
  -Headers @{ Authorization = "Bearer $token" }
```

## Authentication Flow

### Register

`POST /api/v1/auth/register`

```json
{
  "email": "admin@example.com",
  "full_name": "Admin",
  "password": "password123"
}
```

### Login

`POST /api/v1/auth/login`

请求格式是 `application/x-www-form-urlencoded`：

```text
username=admin@example.com
password=password123
```

### Get Current User

`GET /api/v1/auth/me`

Header:

```text
Authorization: Bearer <access_token>
```

## Users CRUD

- `POST /api/v1/users/`
- `GET /api/v1/users/?skip=0&limit=20`
- `GET /api/v1/users/{user_id}`
- `PATCH /api/v1/users/{user_id}`
- `DELETE /api/v1/users/{user_id}`

`/users` 下的接口需要先登录并携带 Bearer Token。

## Testing

```powershell
poetry run pytest
```

测试包含：

- `tests/unit/test_security.py`: JWT 与密码哈希单元测试
- `tests/integration/test_auth.py`: 注册、登录、获取当前用户
- `tests/integration/test_users.py`: users 模块 CRUD 流程

## Pre-commit

安装 hooks：

```powershell
poetry run pre-commit install
```

手动检查全部文件：

```powershell
poetry run pre-commit run --all-files
```

当前已启用：

- 基础文件检查
- `pyupgrade`
- `ruff` lint
- `ruff format`

## Configuration

配置按环境拆分在 `app/core/settings/`：

- `base.py`: 通用配置
- `environments.py`: `development / testing / production`
- `__init__.py`: 根据 `APP_ENV` 加载配置

当前 `.env.example` 已支持：

- `APP_ENV`
- `DATABASE_URL`
- `TASKIQ_ENABLED`
- `TASKIQ_DATABASE_URL`
- `TASKIQ_KEEP_RESULTS`
- `TASKIQ_MESSAGE_TABLE_NAME`
- `TASKIQ_RESULT_TABLE_NAME`
- `TASKIQ_CHANNEL_NAME`
- `TASKIQ_POLL_INTERVAL_SECONDS`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `LOG_LEVEL`
- `CORS_ORIGINS`

## Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

如果要同时启动 API 和 worker：

```powershell
docker compose up --build postgres backend worker
```

## Notes

- 当前仓库已经切换到 `Poetry`，不再使用 `requirements.txt`
- 建议执行 `poetry install` 后把生成的 `poetry.lock` 纳入版本管理
- 如果你打算继续扩展模块，可以复用 `app/crud/base.py`、`app/services/` 和 `app/schemas/` 这套结构
