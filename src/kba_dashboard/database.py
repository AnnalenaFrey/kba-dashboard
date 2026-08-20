from psycopg_pool import ConnectionPool
from abc import ABC, abstractmethod


connection_string = "postgresql://postgres:password@localhost:5432"


class DatabaseAdapter(ABC):

    @abstractmethod
    def __init__(self, connection_string: str) -> None:
        pass


class PostgresAdapter(DatabaseAdapter):

    def __init__(self, connection_string: str):
        self.pool = ConnectionPool(conninfo=connection_string, check=ConnectionPool.check_connection)


with psycopg.connect(connection_string) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE items (
                id int PRIMARY KEY,
                num int,
                item text)
            """)

        cur.execute("""
            INSERT INTO items (id, num, item)
            VALUES (%s, %s, %s) 
        """,
        (5, 1, "Banane")
        )