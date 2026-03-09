from __future__ import annotations

from pathlib import Path

from psycopg2 import connect
from psycopg2 import sql
from sqlalchemy.engine import URL

DEFAULT_DATABASE = "demo"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_sql_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _database_url(user: str, password: str, host: str, port: int, database: str) -> str:
    return URL.create(
        drivername="postgresql",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
    ).render_as_string(hide_password=False)


def _database_exists(host: str, port: int, user: str, password: str, database: str) -> bool:
    conn = connect(host=host, port=port, user=user, password=password, dbname="postgres")
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
            return cur.fetchone() is not None
    finally:
        conn.close()


def _create_database(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    owner: str,
) -> None:
    conn = connect(host=host, port=port, user=user, password=password, dbname="postgres")
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(database),
                    sql.Identifier(owner),
                )
            )
    finally:
        conn.close()


def _execute_sql_file(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    sql_file: Path,
) -> None:
    sql_text = _read_sql_file(sql_file)
    # print(sql_text)  # Debug: print the SQL being executed
    with connect(host=host, port=port, user=user, password=password, dbname=database) as conn:
        with conn.cursor() as cur:
            cur.execute(sql_text)
        conn.commit()



def setup_database(
    owner: str,
    host: str,
    user: str,
    password: str,
    port: int,
    database: str = DEFAULT_DATABASE,
    schema_file: Path | None = None,
    seed_file: Path | None = None,
) -> str:
    """Create and initialize a PostgreSQL database, or return URL if it already exists."""
    db_url = _database_url(user=user, password=password, host=host, port=port, database=database)

    if _database_exists(host=host, port=port, user=user, password=password, database=database):
        return db_url

    root = _project_root()
    schema_path = schema_file or root / "Database" / "schema.sql"
    seed_path = seed_file or root / "Database" / "seed_data.sql"

    _create_database(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        owner=owner,
    )
    _drop_schema(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        schema_name=database,
    )
    conn = connect(host=host, port=port, user=user, password=password, dbname=database)
    cur = conn.cursor()
    cur.execute(
        sql.SQL("CREATE SCHEMA {}; SET SEARCH_PATH TO {};").format(
            sql.Identifier(database),
            sql.Identifier(database)
        )
    )
    conn.commit()
    conn.close()
    
    _execute_sql_file(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        sql_file=schema_path,
    )
    _execute_sql_file(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        sql_file=seed_path,
    )

    return db_url


# def _parse_args() -> argparse.Namespace:
#     parser = argparse.ArgumentParser(description="Create and seed the demo PostgreSQL database.")
#     parser.add_argument("--owner", required=True, help="Database owner role")
#     parser.add_argument("--host", required=True, help="PostgreSQL host")
#     parser.add_argument("--user", required=True, help="PostgreSQL user")
#     parser.add_argument("--password", required=True, help="PostgreSQL password")
#     parser.add_argument("--port", required=True, type=int, help="PostgreSQL port")
#     parser.add_argument("--database", default=DEFAULT_DATABASE, help="Database name (default: demo)")
#     parser.add_argument("--schema-file", type=Path, default=None, help="Path to schema SQL file")
#     parser.add_argument("--seed-file", type=Path, default=None, help="Path to seed SQL file")
#     return parser.parse_args()


if __name__ == "__main__":
    p = Path("G:\Coding\CrimeDB\Crime-Tracking-and-Analysis-Database\Database\seed_data.sql")
    s = Path("G:\Coding\CrimeDB\Crime-Tracking-and-Analysis-Database\Database\schema.sql")

    # re = _read_sql_file(s)
    # print(re)

    url = setup_database(
        owner="postgres",
        host="localhost",
        user="postgres",
        password="Ma314DBS@",
        port=5432,
        database="crimedb",
        schema_file=s,
        seed_file=p,
    )
    print(f"Database URL: {url}")
    
    
