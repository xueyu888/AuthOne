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

## 约束与约定

1. **编码规范**：遵循指定的编码规范，禁止在服务层和模型层使用裸函数，除入口外所有逻辑均封装在类中；接口使用 `Protocol` 定义；`@dataclass` 与 `@classmethod` 用于数据模型和构造；私有属性以下划线开头；统一使用 snake_case 命名；显式声明 `__all__`。
2. **静态类型检查**：建议在开发时使用 `mypy`（见 `pyproject.toml`）进行严格的类型检查，确保代码健壮。
3. **数据库可替换**：虽然默认使用 PostgreSQL + SQLAlchemy，但仓库接口允许替换为其他数据库实现，只需实现相同的协议并在 `AuthService` 中注入。

## License

MIT
