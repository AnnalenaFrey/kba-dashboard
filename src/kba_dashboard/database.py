from psycopg_pool import ConnectionPool
from psycopg.connection import Connection
from abc import ABC, abstractmethod
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
        self.pool = ConnectionPool(conninfo=connection_string, check=ConnectionPool.check_connection, open=False)
        self.schema = "kba_dashboard"

    def open(self):
        self.pool.open()
        with self.pool.connection() as conn:
            table_names = [
                            "fz11_raw",
                            "fz11_processed"
                        ]
            self.create_schema(conn, self.schema)
            self.create_all_tables(conn)

    def close(self):
        self.pool.close()

    def create_schema(self, conn: Connection, schema_name: str):
        with conn.cursor() as cur:
            cur.execute(
                f"""
                CREATE SCHEMA IF NOT EXISTS {schema_name}
            """
            )

    def create_all_tables(self, conn: Connection):
        with conn.cursor() as cur:
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.fz11_raw (
                    id UUID PRIMARY KEY DEFAULT uuidv4(),
                    filename text,
                    year int,
                    month int,
                    download_path text,
                    storage_location text,
                    downloaded_at timestamptz DEFAULT now()
                )
            """
            )

            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.fz11_processed(
                    id UUID PRIMARY KEY DEFAULT uuidv4(),
                    name text
                    )
                """
            )

    def save_raw_document(self, file: KBAFile):
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {self.schema}.fz11_raw (filename, year, month, download_path, storage_location)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                (file.filename, file.year, file.month, file.download_path, file.storage_path)
            )

    def check_if_file_exists(self, download_path: str):
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT EXISTS (
                        SELECT 1
                        FROM {self.schema}.fz11_raw
                        WHERE
                            download_path = (%s)
                    )
                """,
                (download_path,)
                )
                return cur.fetchone()[0]


if __name__ == "__main__":
    connection_string = "postgresql://postgres:password@localhost:5432"
    db = PostgresAdapter(connection_string=connection_string)
    db.open()
    db.close()