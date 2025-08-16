from .routers.permissions import router as perm_router
from .routers.roles import router as role_router
from .routers.groups import router as group_router
from .routers.accounts import router as account_router
from .routers.resources import router as resource_router
from .routers.relations import router as relation_router
from .routers.access import router as access_router

all_routers = [
    perm_router,
    role_router,
    group_router,
    account_router,
    resource_router,
    relation_router,
    access_router,
]
