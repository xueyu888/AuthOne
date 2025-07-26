# AuthOne

AuthOne 是一套面向 AI 平台的现代化身份与访问控制（IAM）服务，支持多租户、细粒度权限、用户组继承以及资源级控制。系统采用 Casbin 作为策略引擎，PostgreSQL 作为默认存储，并提供一套基于 FastAPI 的 REST API，方便前端或其他服务接入。项目遵循严格的编码规范，所有内部实体使用 `@dataclass` 定义，对外接口使用 Pydantic 模型，存储层采用可替换的仓库协议。

## 特性

- **RBAC + ABAC 支持**：权限以 `resource:action` 格式定义，可同时进行角色控制和属性判断。
- **多租户隔离**：角色、用户组和资源均支持 `tenant_id` 字段，不同租户数据完全隔离。
- **资源级控制**：支持对前端组件、后端模块、数据集、模型等资源进行单独授权。
- **Casbin 持久化**：策略通过自定义适配器持久化到数据库，实现动态授权和实时更新。
- **SQLAlchemy 存储**：提供基于 SQLAlchemy 的仓库实现，也可替换为其他数据库后端。
- **FastAPI 接口**：对外暴露 RESTful API，涵盖实体管理、权限配置和访问检查等功能。
- **配置灵活**：通过 `Settings` 类集中配置数据库、日志级别和 Casbin 模型路径。

## 快速开始

### 安装依赖

本项目使用 [Poetry](https://python-poetry.org/) 管理依赖：

```bash
poetry install
```

### 运行服务

项目提供 `api.py` 作为启动入口：

```bash
poetry run uvicorn AuthOne.api:app --reload
```

默认情况下服务会连接本地 PostgreSQL 数据库，请在运行前修改 `AuthOne/config.py` 中的 `Settings.db_url` 或通过环境变量覆盖。

### 数据库初始化

使用 SQLAlchemy 的 `Base.metadata.create_all()` 即可初始化所有表结构，具体见 `AuthOne/db.py`。

```bash
poetry run python -c "from AuthOne.db import create_all; create_all()"
```

## 代码结构

- **AuthOne/models**：领域实体及 Pydantic 模型定义。
- **AuthOne/storage**：仓库协议及 SQLAlchemy/PostgreSQL 实现。
- **AuthOne/core**：Casbin 持久化适配器与引擎封装。
- **AuthOne/service**：业务服务层，负责实体管理和权限校验。
- **AuthOne/api.py**：FastAPI 应用与路由定义。
- **AuthOne/config.py**：配置类。
- **pyproject.toml**：Poetry 项目配置。

## 接口一览

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /permissions | 创建权限（`resource:action`） |
| POST | /roles | 创建角色 |
| POST | /groups | 创建用户组 |
| POST | /accounts | 创建账户 |
| POST | /resources | 创建资源 |
| POST | /roles/{role_id}/permissions/{permission_id} | 绑定权限到角色 |
| POST | /accounts/{account_id}/roles/{role_id} | 绑定角色到账户 |
| POST | /groups/{group_id}/roles/{role_id} | 绑定角色到用户组 |
| POST | /accounts/{account_id}/groups/{group_id} | 绑定用户组到账户 |
| POST | /access/check | 权限校验 |

更多接口和返回格式请参考代码中 `api.py` 的实现。

## 前端（Next.js）

仓库包含一个基于 [Next.js](https://nextjs.org/) 的完整管理前端，位于 `frontend/` 目录。前端界面提供了多个页面用于管理角色、权限、账户、用户组和资源，每个页面都可以创建实体、查看列表并完成常见的绑定操作（如角色绑定权限、账户绑定角色、用户组绑定角色等）。导航栏包含统一的 Logo 和链接，使得管理界面结构清晰、易用。

### 安装并运行前端

1. 安装依赖：

   ```bash
   cd frontend
   npm install
   ```

2. 启动开发服务器：

   ```bash
   npm run dev
   ```

   默认监听在 `http://localhost:3000`，可通过 `NEXT_PUBLIC_API_BASE_URL` 环境变量指定后端 API 地址（默认为 `http://localhost:8000`）。

3. 生产构建与启动：

   ```bash
   npm run build
   npm run start
   ```

### 前端测试

前端使用 [Jest](https://jestjs.io/) 和 [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/) 进行单元测试，测试文件位于 `frontend/tests` 目录。运行测试：

```bash
cd frontend
npm test
```

当运行在 CI/CD 环境中时，上述测试会自动执行，确保前端组件的基本行为。

## 打包为可执行文件

如果希望将服务打包成单一可执行文件，可以借助 [PyInstaller](https://pyinstaller.org/)。下面是使用 Poetry 环境打包的示例步骤：

1. 安装 PyInstaller：

   ```bash
   poetry add --dev pyinstaller
   ```

2. 执行打包命令：

   ```bash
   poetry run pyinstaller --onefile -n authone_api -p ./AuthOne -c AuthOne/api.py
   ```

   参数说明：

   - `--onefile`：生成单一可执行文件；
   - `-n authone_api`：指定输出的可执行文件名称；
   - `-p ./AuthOne`：将包路径加入搜索路径；
   - `-c AuthOne/api.py`：指定程序入口（即 FastAPI 应用）。

生成的可执行文件位于 `dist/` 目录，直接运行即可启动 API 服务。

如需同时部署前端，可在前端完成构建后将生成的 `.next` 静态资源放入适当目录并通过 FastAPI 的静态文件路由或 Nginx 提供服务，亦可使用 Docker 将后端和前端一并封装到镜像中部署。

## VSCode 调试

要在 VSCode 中调试 AuthOne 项目，可使用以下方法：

1. 打开项目后确保安装 Python、Pylance 和 Node.js 相关扩展。
2. 在根目录下创建 `.vscode/launch.json`，添加以下配置：

   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Python: FastAPI",
         "type": "python",
         "request": "launch",
         "module": "uvicorn",
         "args": ["AuthOne.api:app", "--reload"],
         "env": {"PYTHONPATH": "${workspaceFolder}"},
         "justMyCode": true
       },
       {
         "name": "Next.js: Frontend",
         "type": "node",
         "request": "launch",
         "program": "${workspaceFolder}/frontend/node_modules/next/dist/bin/next",
         "args": ["dev"],
         "cwd": "${workspaceFolder}/frontend",
         "runtimeExecutable": "node",
         "env": {
           "PORT": "3000"
         }
       }
     ]
   }
   ```

   上述配置允许一键启动调试后端（FastAPI）和前端（Next.js）服务。后端使用 `uvicorn` 启动 `AuthOne.api:app`，前端在 `frontend` 目录运行 `next dev`。设置断点后点击调试即可。

## 约束与约定

1. **编码规范**：遵循指定的编码规范，禁止在服务层和模型层使用裸函数，除入口外所有逻辑均封装在类中；接口使用 `Protocol` 定义；`@dataclass` 与 `@classmethod` 用于数据模型和构造；私有属性以下划线开头；统一使用 snake_case 命名；显式声明 `__all__`。
2. **静态类型检查**：建议在开发时使用 `mypy`（见 `pyproject.toml`）进行严格的类型检查，确保代码健壮。
3. **数据库可替换**：虽然默认使用 PostgreSQL + SQLAlchemy，但仓库接口允许替换为其他数据库实现，只需实现相同的协议并在 `AuthService` 中注入。

## 高并发支持

AuthOne 设计上支持在生产环境中处理大量并发请求。服务基于 FastAPI 与 Uvicorn 运行，本身具有良好的异步性能。要达到 1 万并发级别，请参考以下建议：

1. **多进程模型**：通过 Uvicorn 或 Gunicorn 启动多个 worker 进程，例如：

   ```bash
   poetry run uvicorn AuthOne.api:app --workers 4 --host 0.0.0.0 --port 8000
   ```

   每个进程可以利用多核 CPU，同时处理大量连接。

2. **连接池**：确保 PostgreSQL 连接池大小足够大，可在 `Settings` 中调整 SQLAlchemy 引擎配置或使用外部连接池。

3. **合理的限流与缓存**：对高频权限校验结果做缓存（如 Redis），减少数据库和 Casbin 访问；使用反向代理（如 Nginx）进行限流。

4. **异步调用**：若在未来需要进一步提升性能，可将仓库层替换为支持异步的 SQLAlchemy 2.0 接口，并将接口定义为 `async def`。

## 持续集成

仓库提供了 `.github/workflows/ci.yml`，利用 GitHub Actions 在每次提交和拉取请求时自动进行测试。CI 流水线包含以下步骤：

1. 启动 PostgreSQL 服务并创建用于测试的数据库；
2. 使用 Poetry 安装后端依赖并运行 `pytest` 执行后端测试；
3. 使用 Node.js 安装前端依赖并运行 `npm test` 执行前端测试；

通过自动化测试，可以在持续集成阶段快速发现代码问题，确保后端和前端在所有平台上的兼容性。

## License

MIT
