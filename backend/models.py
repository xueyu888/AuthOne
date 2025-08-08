"""数据模型定义。

该模块包含内部使用的实体模型（Permission、Role、Group、Account）以及对外
接口模型（AccessCheckRequest、AccessCheckResponse）。内部模型采用
``@dataclass`` 定义，并通过 ``create`` 类方法进行实例化和参数检查。
对外模型采用 ``pydantic.BaseModel`` 以保证输入输出的契约和验证。

所有属性均设为私有并通过只读属性暴露，以防止外部修改内部状态。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import list, Optional

from pydantic import BaseModel, Field, validator

__all__ = [
    "Permission",
    "Role",
    "Group",
    "Account",
    "AccessCheckRequest",
    "AccessCheckResponse",
]


@dataclass(slots=True)
class Permission:
    """表示权限实体。

    权限以 ``resource:action`` 的形式命名，例如 ``app:create`` 或
    ``module:delete``，用于精准描述对某个资源执行某个操作的权力。
    """

    _id: str
    _name: str
    _description: str

    @classmethod
    def create(cls, name: str, description: str) -> "Permission":
        """创建一个权限。

        :param name: 权限名称，必须包含冒号分隔符 ``resource:action``
        :param description: 权限描述，可以为空
        :returns: ``Permission`` 实例
        :raises ValueError: 当名称为空或格式不正确时
        """
        if not name:
            raise ValueError("permission name must not be empty")
        if ":" not in name:
            raise ValueError("permission name must be in format resource:action")
        return cls(
            _id=str(uuid.uuid4()),
            _name=name,
            _description=description or "",
        )

    @property
    def id(self) -> str:
        """权限唯一标识符。"""
        return self._id

    @property
    def name(self) -> str:
        """权限名称 ``resource:action``。"""
        return self._name

    @property
    def description(self) -> str:
        """权限的人类可读描述。"""
        return self._description


@dataclass(slots=True)
class Role:
    """角色实体。

    角色隶属于租户（tenant），可绑定多个权限。角色通过名称和描述表征其职责。
    """

    _id: str
    _tenant_id: Optional[str]
    _name: str
    _description: str
    _permissions: list[str] = field(default_factory=list)

    @classmethod
    def create(cls, tenant_id: Optional[str], name: str, description: str) -> "Role":
        """创建一个角色。

        :param tenant_id: 角色所属的租户 ID，可为空表示全局角色
        :param name: 角色名称，不能为空
        :param description: 角色描述
        :returns: ``Role`` 实例
        :raises ValueError: 当名称为空时
        """
        if not name:
            raise ValueError("role name must not be empty")
        return cls(
            _id=str(uuid.uuid4()),
            _tenant_id=tenant_id,
            _name=name,
            _description=description or "",
        )

    @property
    def id(self) -> str:
        """角色唯一标识符。"""
        return self._id

    @property
    def tenant_id(self) -> Optional[str]:
        """角色所属的租户 ID。"""
        return self._tenant_id

    @property
    def name(self) -> str:
        """角色名称。"""
        return self._name

    @property
    def description(self) -> str:
        """角色描述。"""
        return self._description

    @property
    def permissions(self) -> list[str]:
        """角色拥有的权限 ID 列表（只读）。"""
        return list(self._permissions)

    def add_permission(self, permission_id: str) -> None:
        """为角色添加一个权限关联。

        :param permission_id: 权限 ID
        """
        if permission_id not in self._permissions:
            self._permissions.append(permission_id)


@dataclass(slots=True)
class Group:
    """用户组实体。

    用户组（部门）也属于租户，并可绑定多个角色，实现对一类用户的统一授权。
    """

    _id: str
    _tenant_id: Optional[str]
    _name: str
    _description: str
    _roles: list[str] = field(default_factory=list)

    @classmethod
    def create(cls, tenant_id: Optional[str], name: str, description: str) -> "Group":
        """创建一个用户组。

        :param tenant_id: 租户 ID，可为空
        :param name: 用户组名称，不能为空
        :param description: 描述
        :returns: ``Group`` 实例
        :raises ValueError: 当名称为空时
        """
        if not name:
            raise ValueError("group name must not be empty")
        return cls(
            _id=str(uuid.uuid4()),
            _tenant_id=tenant_id,
            _name=name,
            _description=description or "",
        )

    @property
    def id(self) -> str:
        return self._id

    @property
    def tenant_id(self) -> Optional[str]:
        return self._tenant_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def roles(self) -> list[str]:
        return list(self._roles)

    def add_role(self, role_id: str) -> None:
        """绑定角色到此用户组。"""
        if role_id not in self._roles:
            self._roles.append(role_id)


@dataclass(slots=True)
class Account:
    """用户账户实体。

    ``Account`` 代表一个登录账户，可隶属于某个租户，并可直接绑定角色或加入多个用户组。
    """

    _id: str
    _username: str
    _email: str
    _tenant_id: Optional[str]
    _roles: list[str] = field(default_factory=list)
    _groups: list[str] = field(default_factory=list)

    @classmethod
    def create(cls, username: str, email: str, tenant_id: Optional[str] = None) -> "Account":
        """创建一个用户账户。

        :param username: 用户名，不能为空
        :param email: 邮箱地址，必须包含 ``@``
        :param tenant_id: 租户 ID，可为空
        :returns: ``Account`` 实例
        :raises ValueError: 当用户名或邮箱非法时
        """
        if not username:
            raise ValueError("username must not be empty")
        if not email or "@" not in email:
            raise ValueError("invalid email")
        return cls(
            _id=str(uuid.uuid4()),
            _username=username,
            _email=email,
            _tenant_id=tenant_id,
        )

    @property
    def id(self) -> str:
        return self._id

    @property
    def username(self) -> str:
        return self._username

    @property
    def email(self) -> str:
        return self._email

    @property
    def tenant_id(self) -> Optional[str]:
        return self._tenant_id

    @property
    def roles(self) -> list[str]:
        return list(self._roles)

    @property
    def groups(self) -> list[str]:
        return list(self._groups)

    def add_role(self, role_id: str) -> None:
        if role_id not in self._roles:
            self._roles.append(role_id)

    def add_group(self, group_id: str) -> None:
        if group_id not in self._groups:
            self._groups.append(group_id)


class AccessCheckRequest(BaseModel):
    """访问检查请求模型。

    调用权限校验时使用该模型封装请求参数。``resource`` 和 ``action``
    分别代表要访问的组件/模块名称和要执行的操作。
    """

    account_id: str = Field(..., description="用户账户 ID")
    resource: str = Field(..., description="资源名称，如前端组件或后端模块")
    action: str = Field(..., description="操作名称，如 create/read/update/delete")
    tenant_id: Optional[str] = Field(None, description="请求所属租户 ID，可为空")

    @validator("account_id", "resource", "action")
    def _not_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("must not be empty")
        return v


class AccessCheckResponse(BaseModel):
    """访问检查响应模型。

    ``allowed`` 表示是否允许访问，``reason`` 在拒绝时可提供简要说明。
    """

    allowed: bool = Field(..., description="是否允许访问")
    reason: Optional[str] = Field(None, description="拒绝原因")
