from __future__ import annotations

import typing

import aiosqlite

from .types import DriverWrapper

if typing.TYPE_CHECKING:
    from .types import UserDatabaseConfig, DatabaseConfig
    from .model import DatabaseWrapper, DatabaseTransaction

    class SQLiteDatabaseWrapper(DatabaseWrapper):
        config: UserDatabaseConfig
        pool: None
        conn: typing.Optional[aiosqlite.Connection]
        cursor: typing.Optional[aiosqlite.Cursor]
        caller: aiosqlite.Connection

    class SQLiteDatabaseTransaction(DatabaseTransaction):
        parent: SQLiteDatabaseWrapper
        _transaction: None
        is_active: bool
        commit_on_exit: bool


class SQLiteWrapper(DriverWrapper):

    @staticmethod
    async def create_pool(config: DatabaseConfig) -> None:
        return None

    @staticmethod
    async def get_connection(dbw: typing.Type[SQLiteDatabaseWrapper]) -> SQLiteDatabaseWrapper:
        connection = await aiosqlite.connect(dbw.config.get("database"))
        connection.row_factory = aiosqlite.Row
        v = dbw(
            conn=connection,
        )
        v.is_active = True
        return v

    @staticmethod
    async def release_connection(dbw: SQLiteDatabaseWrapper) -> None:
        assert dbw.conn
        await dbw.conn.close()
        if dbw.cursor:
            try:
                await dbw.cursor.close()
            except ValueError:
                pass
            dbw.cursor = None
        dbw.conn = None
        dbw.is_active = False

    @staticmethod
    async def fetch(dbw: SQLiteDatabaseWrapper, sql: str, *args) -> typing.List[typing.Any]:
        if dbw.cursor:
            try:
                await dbw.cursor.close()
            except ValueError:
                pass
            dbw.cursor = None
        cursor: aiosqlite.Cursor = await dbw.caller.execute(sql, args)
        dbw.cursor = cursor
        return await cursor.fetchall() or list()

    @staticmethod
    async def executemany(dbw: SQLiteDatabaseWrapper, sql: str, *args_list) -> None:
        assert dbw.conn
        await dbw.caller.executemany(sql, args_list)
