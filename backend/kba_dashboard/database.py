from psycopg_pool import AsyncConnectionPool
from psycopg.connection_async import AsyncConnection 
from abc import ABC, abstractmethod
from psycopg.rows import dict_row
import asyncio

from .models.pydantic_models import KBAFile, FZ11Record


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
                    WHERE TABLE_SCHEMA = %s
                    AND TABLE_NAME = %s
                )
            """,
            (self.schema, table_name)
            )
            exists = await cur.fetchone()
            if exists is not None:
                return exists[0]
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
                    segment text,
                    model_series text,
                    brand text,
                    model text,
                    car_registrations int,
                    commercial_share float,
                    year int,
                    month int,
                    raw_file_id UUID REFERENCES {self.schema}.fz11_raw (id) ON DELETE CASCADE
                    )
                """
            )

    async def save_raw_file(self, file: KBAFile) -> dict:
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

    async def save_processed_records(self, records: list[FZ11Record]):

        values = [
        (r.segment, r.model_series, r.brand, r.model, r.car_registrations, r.commercial_share, r.year, r.month, r.raw_file_id)
        for r in records
    ]

        async with self.apool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.executemany(
                    f"""
                    INSERT INTO {self.schema}.fz11_processed (segment, model_series, brand, model, car_registrations, commercial_share, year, month, raw_file_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                values,
            )

    async def get_raw_files(self) -> list[dict]:
        async with self.apool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    f"""
                    SELECT * FROM {self.schema}.fz11_raw
                    WHERE filename like '%.xlsx'
                    AND NOT EXISTS (
                        SELECT 1 FROM {self.schema}.fz11_processed
                        WHERE fz11_processed.raw_file_id = fz11_raw.id
                    )
                    """
                )
                return await cur.fetchall()

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

    async def get_quaterly_total(self, year: int, quarter: int) -> int:
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2

        async with self.apool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"""
                    SELECT SUM(car_registrations)
                    FROM {self.schema}.fz11_processed
                    WHERE year = %s AND month BETWEEN %s AND %s
                """,
                (year, start_month, end_month)
                )
                return (await cur.fetchone())[0]
