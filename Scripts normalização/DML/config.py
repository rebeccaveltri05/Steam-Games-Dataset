from pathlib import Path

DB_CONFIG = {
    "dbname": "Steam Games Dataset",
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": 5432
}
PATH_ROOT = Path(__file__).resolve().parents[1]
