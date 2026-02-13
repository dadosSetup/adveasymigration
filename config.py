from dotenv import load_dotenv
import os

load_dotenv()
env_vars = os.environ

MIGRATION_DB_PARAMS = {
    "v1": {
        "host": os.environ.get("AD_DB_HOST", "localhost"),
        "port": os.environ.get("AD_DB_PORT", "5432"),
        "database": os.environ.get("AD_DB_NAME", "dbname"),
        "user": os.environ.get("AD_DB_USER", "my_user"),
        "password": os.environ.get("AD_DB_PASSWORD", "my_password"),
    },
    "v2": {
        "host": os.environ.get("HOMOLV2_DB_HOST", "localhost"),
        "port": os.environ.get("HOMOLV2_DB_PORT", "5432"),
        "database": os.environ.get("HOMOLV2_DB_NAME", "dbname"),
        "user": os.environ.get("HOMOLV2_DB_USER", "my_user"),
        "password": os.environ.get("HOMOLV2_DB_PASSWORD", "my_password"),
    },
}
