import psycopg
from config import MIGRATION_DB_PARAMS


def connect(version: str):
    params = MIGRATION_DB_PARAMS.get(version)

    if "database" in params:
        params["dbname"] = params.pop("database")
    return psycopg.connect(**params)
