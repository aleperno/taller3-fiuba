import os

RABBIT_HOST = os.environ.get("RABBIT_HOST", "localhost")
CONNECTION_RETRY_DELAY = int(os.environ.get('CONNECTION_RETRY_DELAY', 5))
CONNECTION_RETRY_BACKOFF = int(os.environ.get('CONNECTION_RETRY_BACKOFF', 2))
CONNECTION_RETRIES = int(os.environ.get('CONNECTION_RERIES', 5))
PG_USER = os.environ.get('POSTGRES_USER', 't3user')
PG_PASS = os.environ.get('POSTGRES_PASSWORD', 't3pass')
PG_DB = os.environ.get('POSTGRES_DB', 't3db')
PG_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
PG_PORT = os.environ.get('POSTGRES_PORT', '5432')
PG_CONNECTION_URL = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"
USE_DB = os.environ.get('USE_DB', 'SQLITE')
