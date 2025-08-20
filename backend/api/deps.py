# backend/api/deps.py

from __future__ import annotations
from typing import AsyncGenerator, Awaitable, Callable, TypeVar
from fastapi import HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from ..db import UnitOfWork
from ..service import AuthService 
from ..service.exceptions import DuplicateError, NotFoundError, ConcurrencyError

# 规范 11: 所有模块必须显式声明导出符号 __all__
__all__ = ["RequestHandler"]

T = TypeVar("T")


# 规范 5: 所有逻辑必须封装为类
class RequestHandler:
    """
    封装了 API 层面的依赖注入、事务管理和错误处理逻辑。
    提供了处理“读操作”和“写事务”的统一方法。
    """
    
    @staticmethod
    def get_auth_service(request: Request) -> AuthService:
        """依赖注入：获取 AuthService 实例。"""
        return request.app.state.svc

    @staticmethod
    async def get_uow(request: Request) -> AsyncGenerator[UnitOfWork, None]:
        """依赖注入：提供一个事务性的 UnitOfWork。"""
        session_factory = request.app.state.db_manager.get_async_sessionmaker()
        uow = UnitOfWork(session_factory)
        # 'async with' ensures session is begun and will be closed/rolled back.
        async with uow:
            yield uow

    @staticmethod
    async def _handle_service_errors(coro: Awaitable[T]) -> T:
        """
        规范 6: 错误防御 - 统一将服务层和数据库异常转换为 HTTP 异常。
        """
        try:
            return await coro
        except DuplicateError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ConcurrencyError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database integrity error: {e.orig}")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
        except Exception as e:
            # 兜底处理所有未预见的异常
            # In a production environment, you might want to log this error
            # without exposing internal details to the client.
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected internal error occurred.")

    @classmethod
    async def run_read_operation(cls, service_call: Callable[[], Awaitable[T]]) -> T:
        """
        执行一个只读的服务调用。
        它只处理错误，不执行数据库提交。
        """
        return await cls._handle_service_errors(service_call())

    @classmethod
    async def run_in_transaction(cls, uow: UnitOfWork, service_call: Callable[[], Awaitable[T]]) -> T:
        """
        在单个事务中执行一个“写”服务调用。
        它会处理错误并在成功后提交事务。
        """
        async def _transactional_call() -> T:
            try:
                result = await service_call()
                await uow.commit()
                return result
            except Exception:
                # 'async with uow' from get_uow handles the rollback.
                await uow.rollback() 
                raise
        
        return await cls._handle_service_errors(_transactional_call())