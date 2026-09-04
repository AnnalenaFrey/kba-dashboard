from psycopg_pool import AsyncConnectionPool
from psycopg.connection_async import AsyncConnection 
from abc import ABC, abstractmethod
from psycopg.rows import dict_row
import asyncio

from .models.pydantic_models import KBAFile


class DatabaseAdapter(ABC):

    @abstractmethod
    def __init__(self, connection_string: str) -> None:
        pass

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass


class PostgresAdapter(DatabaseAdapter):

    def __init__(self, connection_string: str):
        self.apool = AsyncConnectionPool(conninfo=connection_string, check=AsyncConnectionPool.check_connection, open=False)
        self.schema = "kba_dashboard"

    async def open(self):
        await self.apool.open()
        async with self.apool.connection() as conn:
            table_names = [
                            "fz11_raw",
                            "fz11_processed"
                        ]
            await self.create_schema(conn, self.schema)
            await self.create_all_tables(conn)

            for table_name in table_names:
                if not await self.__ensure_table_exists(conn, table_name):
                    raise Exception(
                        f"Critical: Table {table_name} missing"
                    )

            
    async def close(self):
        await self.apool.close()

    async def __ensure_table_exists(self, conn:AsyncConnection, table_name: str):
        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                SELECT EXISTS(
                    SELECT * 
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = {self.schema}
                    AND TABLE_NAME = {table_name}
                )
            """
            )
            exists = await cur.fetchone()
            if exists is not None:
                return exists
            else:
                return False

    async def create_schema(self, conn: AsyncConnection, schema_name: str):
        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                CREATE SCHEMA IF NOT EXISTS {schema_name}
            """
            )

    async def create_all_tables(self, conn: AsyncConnection):
        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.fz11_raw (
                    id UUID PRIMARY KEY DEFAULT uuidv4(),
                    filename text,
                    text text,
                    year int,
                    month int,
                    download_path text,
                    storage_location text,
                    downloaded_at timestamptz DEFAULT now()
                )
            """
            )

            await cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.fz11_processed(
                    id UUID PRIMARY KEY DEFAULT uuidv4(),
                    name text
                    )
                """
            )



    async def save_raw_file(self, file: KBAFile):
        async with self.apool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    f"""
                    INSERT INTO {self.schema}.fz11_raw (filename, text, year, month, download_path, storage_location)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING *
                """,
                (file.filename,file.text, file.year, file.month, file.download_path, file.storage_location)
            )
                return await cur.fetchone()

    async def check_if_file_exists(self, download_path: str) -> bool:
        async with self.apool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"""
                    SELECT EXISTS (
                        SELECT 1
                        FROM {self.schema}.fz11_raw
                        WHERE
                            download_path = %s
                    )
                """,
                (download_path,)
                )
                return (await cur.fetchone())[0]

    async def delete_raw_file(self, filename: str):
        async with self.apool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"""
                    DELETE FROM {self.schema}.fz11_raw
                    WHERE filename = %s
                """,
                (filename,)
                )
