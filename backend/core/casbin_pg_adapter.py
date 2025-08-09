from __future__ import annotations

import threading
import asyncio
from typing import List, Optional

from casbin.persist.adapters import Adapter
from casbin.persist import load_policy_line

from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from ..db import CasbinRule  # ORM: ptype, v0..v5 + 唯一索引 (ptype,v0..v5)


class _Worker:
    """后台线程，常驻事件循环与引擎/会话工厂，串行执行所有 Casbin 持久化 I/O。"""

    def __init__(self, db_url: str) -> None:
        self._db_url = db_url
        self._loop = asyncio.new_event_loop()
        self._ready = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._ready.wait()

    def _run(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._engine = create_async_engine(self._db_url, future=True)
        self._sm = async_sessionmaker(self._engine, expire_on_commit=False)
        self._ready.set()
        self._loop.run_forever()

    def run(self, coro: asyncio.Future | asyncio.coroutines.Coroutine) -> None:
        fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
        # 抛异常到调用方（Casbin）
        fut.result()

    def sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        return self._sm

    def close(self) -> None:
        async def _close() -> None:
            await self._engine.dispose()

        self.run(_close())
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=2)


class AsyncPGAdapter(Adapter):
    """Casbin PostgreSQL 持久化（同步接口，后台线程里执行异步 SQL）。"""

    def __init__(self, db_url: str) -> None:
        self._w = _Worker(db_url)

    # --------- Adapter 接口：Casbin 同步调用，内部投递到后台 loop ---------

    def load_policy(self, model) -> None:
        async def _load() -> None:
            async with self._w.sessionmaker()() as s:
                rows = (await s.execute(select(CasbinRule))).scalars().all()
                for r in rows:
                    parts = [r.ptype]
                    for v in (r.v0, r.v1, r.v2, r.v3, r.v4, r.v5):
                        if v:
                            parts.append(v)
                    load_policy_line(", ".join(parts), model)

        self._w.run(_load())

    def save_policy(self, model) -> bool:
        async def _save() -> None:
            async with self._w.sessionmaker().begin() as s:
                await s.execute(delete(CasbinRule))

                def _emit(ptype: str, rule: List[str]):
                    data = {"ptype": ptype}
                    for i, v in enumerate(rule):
                        data[f"v{i}"] = v
                    return (
                        pg_insert(CasbinRule)
                        .values(**data)
                        .on_conflict_do_nothing(
                            index_elements=["ptype", "v0", "v1", "v2", "v3", "v4", "v5"]
                        )
                    )

                if "p" in model.model:
                    for ptype, ast in model.model["p"].items():
                        for rule in ast.policy:
                            await s.execute(_emit(ptype, rule))

                if "g" in model.model:
                    for ptype, ast in model.model["g"].items():
                        for rule in ast.policy:
                            await s.execute(_emit(ptype, rule))

        self._w.run(_save())
        return True

    def add_policy(self, sec: str, ptype: str, rule: List[str]) -> None:
        async def _add() -> None:
            async with self._w.sessionmaker().begin() as s:
                data = {"ptype": ptype}
                for i, v in enumerate(rule):
                    data[f"v{i}"] = v
                stmt = (
                    pg_insert(CasbinRule)
                    .values(**data)
                    .on_conflict_do_nothing(
                        index_elements=["ptype", "v0", "v1", "v2", "v3", "v4", "v5"]
                    )
                )
                await s.execute(stmt)

        self._w.run(_add())

    def remove_policy(self, sec: str, ptype: str, rule: List[str]) -> None:
        async def _rm() -> None:
            async with self._w.sessionmaker().begin() as s:
                q = delete(CasbinRule).where(CasbinRule.ptype == ptype)
                for i, v in enumerate(rule):
                    q = q.where(getattr(CasbinRule, f"v{i}") == v)
                await s.execute(q)

        self._w.run(_rm())

    def remove_filtered_policy(
        self, sec: str, ptype: str, field_index: int, *field_values: Optional[str]
    ) -> None:
        async def _rmf() -> None:
            async with self._w.sessionmaker().begin() as s:
                q = delete(CasbinRule).where(CasbinRule.ptype == ptype)
                for i, v in enumerate(field_values):
                    if v is None:
                        continue
                    q = q.where(getattr(CasbinRule, f"v{field_index + i}") == v)
                await s.execute(q)

        self._w.run(_rmf())

    # 应用关闭时调用
    def close(self) -> None:
        self._w.close()
